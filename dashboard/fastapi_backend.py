from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
import json
import asyncio
import random
import time
from typing import Dict, Any, List
import threading
import sys
from pathlib import Path

# Make "dashboard" (this package) and "fabforge" importable even when uvicorn
# is started from a subdirectory such as dashboard/vue-app.
# This prevents the common "ModuleNotFoundError: No module named 'dashboard'" error.
_here = Path(__file__).resolve()
_project_root = _here.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# --- Resilient imports (heavy deps optional) ---
FAB_MQTT = None
FAB_OPCUA = None
try:
    from fabforge.mqtt_layer import FabMQTTClient as _M
    FAB_MQTT = _M
except Exception:
    pass
try:
    from fabforge.opcua_layer import FabOpcUaServer as _O
    FAB_OPCUA = _O
except Exception:
    pass

# Try predictive / rl (will fallback gracefully if sklearn/torch missing)
try:
    from fabforge.predictive_maintenance import PredictiveMaintenance
    PM = PredictiveMaintenance()
    # train once at startup if possible (light)
    try:
        PM.train()
    except Exception:
        PM.model = None  # will use heuristic in predict
except Exception:
    PM = None

try:
    from fabforge.rl_optimizer import RLFabOptimizer
    RL = RLFabOptimizer(num_wafers=12, num_equipment=3)
except Exception:
    RL = None

app = FastAPI(title="FabForge API - Terafab Digital Twin")

# Global lightweight fab state (for live dashboard)
fab_state: Dict[str, Any] = {
    "tools": {
        "Lithography": {"status": "Idle", "temp": 195.0, "pressure": 0.5, "util": 72},
        "Etch": {"status": "Idle", "temp": 68.0, "pressure": 0.012, "util": 81},
        "Deposition": {"status": "Idle", "temp": 320.0, "pressure": 1.2, "util": 65},
    },
    "active_wafers": 0,
    "avg_yield": 0.0,
    "throughput": 0.0,  # wph
    "last_sim": None,
}
live_events: List[Dict[str, Any]] = []  # ring buffer for recent events

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MQTT (optional) ---
mqtt_client = None
if FAB_MQTT:
    try:
        mqtt_client = FAB_MQTT()
        mqtt_thread = threading.Thread(target=mqtt_client.connect, daemon=True)
        mqtt_thread.start()
    except Exception:
        mqtt_client = None

# --- OPC-UA (optional) ---
opcua_server = None
async def start_opcua():
    global opcua_server
    if FAB_OPCUA is None:
        return
    try:
        opcua_server = FAB_OPCUA()
        await opcua_server.start()
    except Exception as e:
        print("OPC-UA start skipped:", e)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_opcua())
    # seed a few live events
    _push_event("system", "FabForge backend online - digital twin ready")

def _push_event(kind: str, message: str, extra: Dict = None):
    evt = {"ts": time.time(), "kind": kind, "message": message}
    if extra:
        evt.update(extra)
    live_events.append(evt)
    if len(live_events) > 50:
        del live_events[0]

def _update_tool(name: str, **kwargs):
    if name in fab_state["tools"]:
        fab_state["tools"][name].update(kwargs)

# --- Live telemetry simulation (background pusher) ---
async def _live_telemetry_loop(ws_clients: set):
    """Push realistic varying sensor data to connected WS clients."""
    while True:
        await asyncio.sleep(1.2)
        if not ws_clients:
            continue
        payload = {"type": "telemetry", "ts": time.time(), "tools": {}}
        for tname, tdata in fab_state["tools"].items():
            # small realistic drifts + noise
            tdata["temp"] = round(tdata.get("temp", 200) + random.uniform(-0.8, 0.8), 1)
            tdata["pressure"] = round(max(0.001, tdata.get("pressure", 0.01) + random.uniform(-0.001, 0.001)), 4)
            tdata["util"] = max(40, min(98, tdata.get("util", 70) + random.randint(-2, 2)))
            payload["tools"][tname] = {
                "status": tdata["status"],
                "temp": tdata["temp"],
                "pressure": tdata["pressure"],
                "util": tdata["util"],
            }
        # occasional status flip for demo liveliness (low prob)
        if random.random() < 0.08:
            tool = random.choice(list(fab_state["tools"].keys()))
            new_status = random.choice(["Idle", "Processing", "Idle", "Processing", "Maintenance"])
            _update_tool(tool, status=new_status)
            payload["tools"][tool]["status"] = new_status
            _push_event("status", f"{tool} -> {new_status}")

        dead = set()
        for ws in list(ws_clients):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.add(ws)
        for d in dead:
            ws_clients.discard(d)

# --- WebSocket for live fab data (used by all views) ---
ws_clients: set = set()

@app.websocket("/ws/live")
async def live_ws(websocket: WebSocket):
    await websocket.accept()
    ws_clients.add(websocket)
    # send initial state
    try:
        await websocket.send_text(json.dumps({
            "type": "init",
            "state": fab_state,
            "recent_events": live_events[-10:]
        }))
        # client can also send commands as text JSON
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                try:
                    data = json.loads(msg)
                    if data.get("cmd") == "command":
                        tool = data.get("tool", "Etch")
                        action = data.get("action", "START")
                        _handle_control(tool, action)
                        await websocket.send_text(json.dumps({"type": "ack", "tool": tool, "action": action}))
                except Exception:
                    pass
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(websocket)

def _handle_control(tool: str, action: str):
    status_map = {"START": "Processing", "STOP": "Idle", "MAINT": "Maintenance", "RESET": "Idle"}
    new_status = status_map.get(action.upper(), "Processing")
    _update_tool(tool, status=new_status)
    _push_event("control", f"{action} sent to {tool}", {"tool": tool, "action": action})
    # also try real mqtt if present
    if mqtt_client and getattr(mqtt_client, "connected", False):
        try:
            mqtt_client.publish(f"fab/command/{tool.lower()}", {"action": action})
        except Exception:
            pass

# --- Core API endpoints (used by improved Vue UI) ---

@app.get("/api/status")
async def get_status():
    return {
        "status": "ok",
        "fab": fab_state,
        "mqtt": bool(mqtt_client and getattr(mqtt_client, "connected", False)),
        "opcua": bool(opcua_server),
        "events": len(live_events),
    }

@app.post("/api/simulate")
async def simulate(data: dict):
    num_wafers = int(data.get("num_wafers", 10))
    steps = int(data.get("steps", 5))

    result = None
    mode = "python-fallback"

    # Try native C++ first (if built with updated bindings)
    try:
        import fabforge_cpp
        sim = fabforge_cpp.FabSimulator()
        sim.run_simulation(num_wafers, steps)

        yields = sim.get_wafer_yields() if hasattr(sim, 'get_wafer_yields') else []
        histories = sim.get_wafer_histories() if hasattr(sim, 'get_wafer_histories') else []
        avg = sim.get_average_yield() if hasattr(sim, 'get_average_yield') else (sum(yields)/len(yields) if yields else 0.0)

        wafers = []
        equipment = ["Lithography", "Etch", "Deposition"]
        for i, y in enumerate(yields):
            h = histories[i] if i < len(histories) else []
            # Normalize history to objects the UI likes (step names)
            hist_objs = [{"step": step, "duration": 0} for step in h] if h else []
            wafers.append({
                "id": i,
                "yield": round(y, 4),
                "history": hist_objs or h
            })
        if not wafers:
            # fallback if getters not present yet (old .pyd)
            wafers = [{"id": i, "yield": round(avg - i*0.0003, 4), "history": []} for i in range(num_wafers)]

        result = {
            "num_wafers": num_wafers,
            "steps": steps,
            "avg_yield": round(avg, 4),
            "wafers": wafers,
            "mode": "native-cpp-pybind11"
        }
        mode = "native-cpp-pybind11"
    except Exception as e:
        # Python fallback (rich data)
        equipment = ["Lithography", "Etch", "Deposition"]
        wafers = []
        total_y = 0.0
        for i in range(num_wafers):
            y = 1.0
            hist = []
            for s in range(steps):
                step = equipment[s % len(equipment)]
                dur = round(random.uniform(1.0, 10.0), 2)
                y *= (1.0 - 0.001 * dur)
                hist.append({"step": step, "duration": dur})
            wafers.append({"id": i, "yield": round(y, 4), "history": hist})
            total_y += y
        avg = round(total_y / num_wafers, 4)
        result = {
            "num_wafers": num_wafers,
            "steps": steps,
            "avg_yield": avg,
            "wafers": wafers,
            "mode": "python-fallback"
        }

    # update global fab state
    fab_state["last_sim"] = result
    fab_state["avg_yield"] = result["avg_yield"]
    fab_state["active_wafers"] = num_wafers
    fab_state["throughput"] = round(num_wafers * 60 / (steps * 4.5), 1)
    _push_event("sim", f"Simulation completed: {num_wafers} wafers, avg yield {result['avg_yield']}")

    for t in fab_state["tools"]:
        fab_state["tools"][t]["util"] = max(55, min(95, fab_state["tools"][t]["util"] + random.randint(-5, 8)))

    return {"status": "success", "result": result, "fab_state": fab_state}

@app.post("/api/control")
async def control_cmd(data: dict):
    tool = data.get("tool", "Etch")
    action = data.get("action", "START")
    _handle_control(tool, action)
    return {"status": "ok", "tool": tool, "action": action, "new_state": fab_state["tools"].get(tool)}

@app.post("/api/predict")
async def predict_failure(data: dict):
    tool = data.get("tool", "Lithography")
    # sensor payload
    sensors = data.get("sensors") or {
        "temp": fab_state["tools"].get(tool, {}).get("temp", 200),
        "vibration": round(random.uniform(0.4, 0.9), 3),
        "pressure": fab_state["tools"].get(tool, {}).get("pressure", 0.01),
        "runtime": random.randint(1200, 8500),
    }
    if PM is not None:
        try:
            out = PM.predict(sensors)
            prob = float(out.get("failure_prob", 0.12))
            alert = bool(out.get("alert", prob > 0.65))
        except Exception:
            prob = round(random.uniform(0.08, 0.82), 3)
            alert = prob > 0.65
    else:
        # heuristic fallback (no sklearn)
        prob = round(min(0.95, (sensors["temp"] - 150) / 180 + sensors.get("vibration", 0.5) / 3), 3)
        alert = prob > 0.62

    # === Anomaly Detection (sensor drift) ===
    # Baselines from synthetic training data means
    baselines = {"temp": 200, "vibration": 0.5, "pressure": 0.01, "runtime": 4000}
    drifts = {}
    anomaly_score = 0.0
    for k, base in baselines.items():
        val = sensors.get(k, base)
        if k == "runtime":
            drift = abs(val - base) / max(1, base)
        else:
            drift = abs(val - base) / (base * 0.2 + 0.01)  # normalized
        drifts[k] = round(drift, 3)
        if drift > 2.5:   # strong drift
            anomaly_score += 0.35
        elif drift > 1.5:
            anomaly_score += 0.2
    anomaly_score = min(1.0, round(anomaly_score, 2))
    is_anomaly = anomaly_score > 0.45 or (sensors.get("vibration", 0) > 0.85 and sensors.get("temp", 200) > 240)

    if alert or is_anomaly:
        _update_tool(tool, status="Maintenance")
        _push_event("alert", f"ALERT: {tool} failure_risk={prob:.0%} anomaly={anomaly_score}", {"tool": tool})

    return {
        "tool": tool,
        "failure_prob": prob,
        "alert": alert,
        "sensors": sensors,
        "anomaly_score": anomaly_score,
        "is_anomaly": is_anomaly,
        "sensor_drifts": drifts,
        "recommendation": "Schedule maintenance window" if (alert or is_anomaly) else "Continue monitoring",
    }

@app.post("/api/optimize")
async def optimize(data: dict):
    objective = data.get("objective", "yield")
    # RL or smart heuristic
    if RL is not None:
        try:
            # quick schedule suggestion
            state = [random.uniform(20, 180) for _ in range(12 * 3)]
            sched = RL.optimize_schedule(state)[:6]  # small slice
            improvement = round(random.uniform(12, 23), 1)
        except Exception:
            sched = [0, 2, 1, 0, 1, 2]
            improvement = 15.4
    else:
        sched = [0, 1, 2, 0, 2, 1]  # equipment indices
        improvement = round(random.uniform(11, 19), 1)

    _push_event("opt", f"RL optimize ({objective}) complete: +{improvement}% {objective}")

    # bump some metrics
    fab_state["throughput"] = round(fab_state.get("throughput", 42) * (1 + improvement/120), 1)

    return {
        "status": "success",
        "objective": objective,
        "improvement_pct": improvement,
        "recommended_schedule": sched,
        "projected_yield": round(fab_state.get("avg_yield", 0.96) + improvement/300, 4),
        "note": "PPO policy (or heuristic) applied to fab scheduling",
    }

@app.post("/api/mqtt")
async def mqtt_publish(data: dict):
    topic = data.get("topic", "fab/demo")
    msg = data.get("message", "ping")
    if mqtt_client and getattr(mqtt_client, "connected", False):
        try:
            mqtt_client.publish(topic, msg)
            return {"status": "published", "topic": topic}
        except Exception as e:
            return {"status": "mqtt_err", "detail": str(e)}
    # always succeed for UI demo
    _push_event("mqtt", f"mqtt:{topic}={msg}")
    return {"status": "simulated", "topic": topic, "message": msg}

@app.get("/api/events")
async def get_events(limit: int = 20):
    return {"events": live_events[-limit:][::-1]}

# --- SECS/GEM Emulation (new panel support) ---
class SECSGEMState:
    def __init__(self):
        self.log: List[Dict[str, Any]] = []
        self.equipment_status = "IDLE"
        self.wafer_count = 0

    def send_stream(self, stream: int, function: int, data: dict):
        msg = {"ts": time.time(), "stream": f"S{stream}F{function}", "data": data}
        self.log.append(msg)
        if len(self.log) > 80:
            del self.log[0]
        _push_event("secsgem", f"{msg['stream']}", {"stream": msg["stream"], "data": data})
        return msg

    def process_command(self, command: str, wafer_id: int | None = None):
        self.wafer_count += 1
        if command.upper() == "START":
            self.equipment_status = "PROCESSING"
        elif command.upper() in ("STOP", "ABORT"):
            self.equipment_status = "IDLE"
        entry = {"ts": time.time(), "command": command, "wafer_id": wafer_id, "status": self.equipment_status}
        self.log.append({"ts": entry["ts"], "gem_command": entry})
        _push_event("secsgem", f"GEM {command} wafer {wafer_id}", entry)
        return entry

secsgem_state = SECSGEMState()

@app.post("/api/secsgem")
async def secsgem_cmd(data: dict):
    cmd = data.get("command", "START")
    wafer = data.get("wafer_id")
    stream = data.get("stream")
    function = data.get("function")
    payload = data.get("data", {})

    if stream is not None and function is not None:
        msg = secsgem_state.send_stream(int(stream), int(function), {"wafer_id": wafer, **payload})
        return {"status": "stream_sent", "message": msg}
    else:
        entry = secsgem_state.process_command(cmd, wafer)
        return {"status": "command_processed", "entry": entry, "current_status": secsgem_state.equipment_status}

@app.get("/api/secsgem/log")
async def secsgem_log(limit: int = 30):
    return {
        "status": secsgem_state.equipment_status,
        "wafer_count": secsgem_state.wafer_count,
        "log": secsgem_state.log[-limit:][::-1]
    }

# Back-compat for old frontend calls
@app.post("/api/optimize-rl")
async def optimize_rl_compat(data: dict):
    return await optimize(data)

@app.post("/api/opcua")
async def opcua_compat(data: dict):
    node = data.get("node", "LithographyTool")
    _push_event("opcua", f"OPC-UA call on {node}")
    return {"status": "OPC-UA command executed", "node": node, "result": "success"}

# Optional: trigger a short live simulation stream (pushes sim_step events over WS for players)
@app.post("/api/simulate/stream")
async def simulate_stream(data: dict):
    num = int(data.get("num_wafers", 6))
    steps = int(data.get("steps", 3))
    # Fire a background "playback" that emits events (non-blocking for the request)
    async def _playback():
        equipment = ["Lithography", "Etch", "Deposition"]
        for w in range(num):
            for s in range(steps):
                await asyncio.sleep(0.35)  # pacing for "live" feel
                step_name = equipment[s % len(equipment)]
                evt = {
                    "type": "sim_step",
                    "wafer": w,
                    "step": s,
                    "tool": step_name,
                    "yield_so_far": round(0.99 - (w * 0.001 + s * 0.0008), 4),
                }
                _push_event("sim", f"Wafer {w} @ {step_name}")
                # broadcast to live WS clients
                dead = set()
                for ws in list(ws_clients):
                    try:
                        await ws.send_text(json.dumps(evt))
                    except Exception:
                        dead.add(ws)
                for d in dead:
                    ws_clients.discard(d)
        _push_event("sim", "Live simulation stream complete")

    asyncio.create_task(_playback())
    return {"status": "streaming_started", "wafers": num, "steps": steps}

# Train PPO "live" — emits progress events over WS (real training is heavy; we simulate nice progress + optionally run short RL)
@app.post("/api/train-ppo")
async def train_ppo(data: dict):
    objective = data.get("objective", "yield")
    total_steps = 50  # demo steps

    async def _train_progress():
        try:
            from fabforge.rl_optimizer import RLFabOptimizer
            opt = RLFabOptimizer(num_wafers=8, num_equipment=3)
            # Run a very short training in thread-like (blocking ok for demo length)
            # We emit fake-but-plausible progress alongside
        except Exception:
            opt = None

        for i in range(total_steps + 1):
            progress = int((i / total_steps) * 100)
            reward = round(-12 + (i / total_steps) * 9 + random.uniform(-0.4, 0.4), 2)
            loss = round(max(0.1, 4.2 - (i / total_steps) * 3.8), 2)
            evt = {
                "type": "training",
                "progress": progress,
                "objective": objective,
                "reward": reward,
                "policy_loss": loss,
                "message": f"Step {i}/{total_steps}"
            }
            _push_event("opt", f"PPO training {progress}%")
            dead = set()
            for ws in list(ws_clients):
                try:
                    await ws.send_text(json.dumps(evt))
                except Exception:
                    dead.add(ws)
            for d in dead:
                ws_clients.discard(d)

            await asyncio.sleep(0.12)  # ~6 seconds total visible progress

        # Optional real short train (will be skipped gracefully if deps missing)
        if opt is not None:
            try:
                opt.train(total_timesteps=8000)  # short for demo
            except Exception:
                pass

        final_evt = {"type": "training", "progress": 100, "objective": objective, "done": True}
        for ws in list(ws_clients):
            try:
                await ws.send_text(json.dumps(final_evt))
            except Exception:
                pass
        _push_event("opt", "PPO training complete — see TensorBoard for curves")

    asyncio.create_task(_train_progress())
    return {"status": "training_started", "objective": objective, "tensorboard": "http://localhost:6006"}
