# FabForge: Real-World Capabilities, Sections, Usage & Features

**FabForge** is a production-grade **digital twin** of a semiconductor fabrication facility (fab), built as a portfolio project to demonstrate the full stack of skills needed for **Automation, Controls, and AI Software Engineer** roles at advanced manufacturers (e.g. Terafab-scale 1TW AI silicon production).

It lets you safely experiment with the exact problems real fabs face every day: running complex multi-stage processes under uncertainty, integrating with factory protocols, using AI for scheduling and maintenance, and giving operators a live, usable view of the plant.

---

## What Can Be Accomplished in the Real World?

### 1. Safe Controls & Logic Development
- Develop and test **PLC-style logic** and equipment state machines (IDLE → PROCESSING → MAINTENANCE → FAULT) without ever touching physical tools that cost hundreds of millions of dollars.
- Simulate stochastic process times, yield loss, and emergency stops.
- Use the emulated IEC 61131-3 ladder logic and state machines as a reference or training aid for real control engineers.

### 2. Industrial Protocol Prototyping & Validation
Real wafer fabs rely on specific protocols for tool-to-MES (Manufacturing Execution System) communication:

- **SECS/GEM (SEMI E5/E30)** — the dominant protocol in many 300mm/450mm fabs. FabForge includes a full emulator for both host commands (GEM) and S/F stream messages. You can prototype and test MES integration logic safely.
- **OPC-UA** — modern digital-twin / Industry 4.0 standard. The project runs a real OPC-UA server with equipment objects, writable variables (Temperature, Pressure, Status), and callable methods (`ProcessWafer`).
- **MQTT** — lightweight pub/sub for telemetry and commands. Useful for modern IIoT overlays or internal dashboards.

You can exercise the full round-trip: simulation → protocol emission → external client (or the built-in UI) → command back into the system.

### 3. AI / ML for Manufacturing Optimization
- **PPO Reinforcement Learning** for dynamic equipment assignment and scheduling under uncertainty (variable processing times, load balancing).
- **Predictive Maintenance** with failure probability + **anomaly detection** on sensor drift (temperature, vibration, pressure, runtime). The system can raise alerts that feed back into controls/scheduling.
- Train models, run inference, visualize progress (including TensorBoard curves for real training runs), and see the effect on simulated yield/throughput.

This mirrors high-value use cases where even small improvements in uptime or yield are worth tens of millions per year.

### 4. Operator Training & "What-If" Scenario Exploration
- The live Vue dashboard (with real-time WebSocket updates, tool cards, simulation player, and protocol panels) is close enough to a real fab HMI/SCADA view that it can be used for training.
- Run a simulation, watch wafers move through the line (via the SVG flow diagram), inject controls or SECS/GEM commands, trigger predictive alerts, and observe the system react.
- The central event timeline gives a unified view of everything happening across simulation, controls, protocols, and AI.

### 5. Full-Stack Digital Twin & Portfolio Demonstration
The project is deliberately built as an end-to-end showcase:
- Low-level C++ discrete-event simulation (with PyBind11 bindings).
- Multiple real industrial protocols.
- AI (RL + ML).
- Modern web UI with live data.
- Containerization (Docker), orchestration (k8s), CI, tests.

It proves you can ship a production-*style* system that integrates the layers a real automation/controls engineer must master.

---

## Architecture Overview

```
C++ Core (src/cpp/simulation)
    ↓ (via PyBind11 or standalone exe)
Python Layers (fabforge/)
    • cli.py
    • mqtt_layer.py
    • opcua_layer.py          ← runs real OPC-UA server
    • secsgem_layer.py
    • predictive_maintenance.py
    • rl_optimizer.py
    ↓
FastAPI Backend (dashboard/fastapi_backend.py)
    • REST API + WebSocket (/ws/live)
    • Live state machine + telemetry loop
    • Simulation runner (native or Python fallback)
    • Control, Predict (with anomaly), Optimize, SECS/GEM, Training endpoints
    • Background services (OPC-UA, MQTT client if available)
    ↓ (WebSocket + REST)
Vue 3 Frontend (dashboard/vue-app/)
    • Global topbar + central event timeline
    • 5 main views (detailed below)
Infrastructure
    • build_cpp.py (Windows + Unix native build)
    • Docker / docker-compose / k8s
    • pytest suite
    • CLI entry point (grok-fab after `pip install -e .`)
```

The system is deliberately cross-platform and degrades gracefully (works without torch, scikit-learn, paho-mqtt, etc.).

---

## Sections & How to Use Them

### 1. C++ Simulation Core (The Heart of the Digital Twin)

**What it is**
- Discrete-event simulator for wafer processing (Lithography → Etch → Deposition).
- Per-wafer yield degradation based on random processing durations.
- Equipment State Machines + PLCEngine that emulates IEC 61131-3 ladder logic and safety interlocks.
- Now exposes rich per-wafer data (yields + step histories) via PyBind11 for the dashboard.

**How to use**
- Build once: `python build_cpp.py` (requires Visual Studio "Desktop development with C++" on Windows, or g++/cmake on Linux).
- Produces:
  - `fab_sim.exe` (or `fab_sim`) — standalone executable.
  - `fabforge_cpp.*.pyd` (or .so) — importable from Python as `fabforge_cpp`.
- From CLI (recommended):
  ```bash
  python -m fabforge.cli simulate --num-wafers 20 --steps 5 --use-cpp
  ```
- Direct from Python (after build):
  ```python
  import fabforge_cpp
  sim = fabforge_cpp.FabSimulator()
  sim.run_simulation(12, 4)
  print(sim.get_wafer_yields())
  print(sim.get_wafer_histories())
  ```
- The C++ trace (state transitions, PLC rungs, per-wafer processing) is printed to stdout for authenticity.

**Real-world analogy**
This is the "physics" layer. In a real fab you would replace or augment it with actual tool interfaces while keeping the same state-machine and protocol layers.

### 2. Python Layers (fabforge/)

Located in `fabforge/`. These are the reusable integration and intelligence modules.

- **cli.py** — The `grok-fab` command-line interface.
  - `simulate` — runs the core (with or without native C++).
  - `mqtt publish` — publish to the MQTT layer.
  - `secsgem` — exercise the SECS/GEM emulator.
  - `dashboard` — launch the FastAPI backend (works from any directory thanks to recent robustness fixes).
- **mqtt_layer.py** — thin wrapper around paho-mqtt. Publishes and subscribes on `fab/#` topics.
- **opcua_layer.py** — full OPC-UA server (asyncua) exposing `LithographyTool`, `EtchTool`, `DepositionTool` with variables and a `ProcessWafer` method.
- **secsgem_layer.py** — SEMI E5/E30 style emulator (S/F streams + GEM host commands like START/STOP).
- **predictive_maintenance.py** — RandomForest (or heuristic fallback) that predicts failure probability from sensor vectors (temp, vibration, pressure, runtime). Also supports synthetic data generation.
- **rl_optimizer.py** — Stable-Baselines3 PPO agent + custom Gym environment (`FabEnv`) for equipment scheduling. Supports `train()` (long-running, writes TensorBoard logs) and `optimize_schedule()` for inference.

**Typical usage**
```python
from fabforge.rl_optimizer import RLFabOptimizer
opt = RLFabOptimizer()
opt.train(total_timesteps=50000)          # real training
schedule = opt.optimize_schedule(state)   # get actions
```

### 3. CLI (`grok-fab` or `python -m fabforge.cli`)

After `pip install -e .` you get the `grok-fab` command.

See `CLI.md` for the current command reference. The most useful for exploration are:
- `simulate --num-wafers N --steps M [--use-cpp]`
- `secsgem --command START --wafer-id 42`
- `mqtt publish --topic fab/... --message '...'`
- `dashboard --port 8000` (launches the backend; works from any CWD)

### 4. FastAPI Backend (`dashboard/fastapi_backend.py`)

This is the "brain" that ties everything together and serves the UI.

**How to run**
```bash
# From project root (or use the robust CLI)
python -m uvicorn dashboard.fastapi_backend:app --port 8000 --reload
# or
grok-fab dashboard --port 8000
```

**Key responsibilities (many not directly visible in the UI)**
- Manages shared `fab_state` (tool status, sensors, last simulation results).
- Background telemetry pusher that drifts temperatures/pressures/utilization and occasionally flips states.
- WebSocket `/ws/live` — pushes telemetry, sim_step events, training progress, and init state. Clients can also send control commands over the socket.
- REST surface used by the Vue app (and useful for custom clients):
  - `POST /api/simulate` — run simulation (tries native C++ first for authenticity, falls back to Python). Returns rich per-wafer data.
  - `POST /api/control` — send START/STOP/MAINT/RESET to a tool.
  - `POST /api/predict` — failure probability + **anomaly detection** (sensor drift scoring) + recommendation.
  - `POST /api/optimize` — get PPO (or heuristic) recommended schedule + projected improvement.
  - `POST /api/train-ppo` — starts a visible training run that streams progress/reward/loss over WS (simulated by default; can do a short real PPO run).
  - `POST /api/simulate/stream` — fire-and-forget background simulation that emits `sim_step` events (great for driving the player from the backend).
  - `POST /api/secsgem` + `GET /api/secsgem/log` — full SECS/GEM interaction.
  - `POST /api/mqtt` — publish via the MQTT layer (or simulated).
  - `GET /api/status`, `GET /api/events`.
- On startup it tries to start the real OPC-UA server and MQTT client (if the layers are importable).
- Event ring buffer that feeds both the WS and the `/events` endpoint (used by the central timeline).

**Important**: The backend is where a lot of "real" behavior lives (protocol servers, background loops, anomaly math, optional real RL). The UI is mostly a consumer of this surface.

### 5. Vue.js Frontend (The Operator Interface)

Run with:
```bash
cd dashboard/vue-app
npm run dev
```
(Proxies `/api` and expects the backend on 8000.)

**Global / Shared Features (available on every tab)**
- Top industrial header with live metrics pulled from WS + polling: YIELD, WPH (wafers per hour), TOOLS (healthy count), ALERTS.
- "● LIVE" / "○ OFFLINE" indicator for the WebSocket connection.
- 5-tab navigation (SIM / CONTROLS / OPTIMIZE / PREDICTIVE / SECS/GEM).
- Central **Event Timeline** (toggleable in footer) — unified log of sim, control, alert, secsgem, opt, training, status, mqtt, etc. events. Fed by both WS and `/api/events`.
- Consistent dark industrial styling and card-based layout.

#### SIM Tab (Wafer Process Simulation)
- Sliders for number of wafers (3–60) and process steps (2–9).
- "▶ RUN SIMULATION" (and "Run + Auto-Chart").
- Results panel:
  - KPI cards (Avg Yield, Wafers, Steps, Mode — shows "native-cpp-pybind11" when the real C++ is used).
  - Wafer results table (first 12 shown) with color-coded yield % and process history.
  - **Yield Heatmap** — grid of small colored squares (one per wafer). Green = high yield, red = low. Hover for exact %.
  - Yield Distribution bar chart (Chart.js).
- **Live Simulation Player** (appears after a run):
  - Play / Pause / Reset + speed selector (0.5×–8×).
  - Live "Playing: Wafer X / N — Step Y — Current Tool: Z".
  - **Real-time SVG wafer path flow diagram** — three stations (Lithography, Etch, Deposition) with a green "W" marker that moves along the process flow as playback advances.
  - Playback event log.
  - "Also stream via backend WS" button (calls `/api/simulate/stream` so other views can react to the steps).

#### CONTROLS Tab (Real-time Equipment Controls)
- Three live **tool cards** (Lithography, Etch, Deposition) showing:
  - Current status (with colored pills: Processing = green, Maintenance/Fault = red).
  - Live temperature, pressure, utilization (updated via WS telemetry).
- Four command buttons per tool: START, STOP, MAINT, RESET.
  - Buttons call the backend; state updates immediately via WS and the global fab_state.
- Live scrolling control log (shows commands sent + acks + MQTT demo publishes).
- "Send MQTT demo telemetry" button (exercises the MQTT path).

#### OPTIMIZE Tab (RL Scheduling Optimizer)
- Objective selector (Yield / Throughput / Energy + Yield).
- "🚀 RUN PPO POLICY OPTIMIZATION" — calls `/api/optimize`, shows improvement %, projected yield, and recommended equipment assignments for the first few wafers.
- Before/after gain bar chart.
- **"▶ TRAIN PPO LIVE (short demo)"** button:
  - Shows a progress bar + live reward value.
  - Streams `training` events over WS (the backend can do a short real PPO run or pure simulation).
  - Direct link to TensorBoard (`http://localhost:6006`) for real training curves.
- Impact summary cards.

#### PREDICTIVE Tab (Predictive Maintenance)
- One card per tool with:
  - Risk progress bar (failure probability).
  - Current sensor values (temperature, vibration, runtime, etc.).
  - **Anomaly score** + "DRIFT DETECTED" warning when sensor drift exceeds thresholds (implemented in the backend even when the sklearn model is not available).
  - "RUN PREDICTION" button (calls `/api/predict`).
- Mini trend charts per tool.
- When risk or anomaly is high the card and global state react (status flips to Maintenance, alerts appear in timeline and topbar).

#### SECS/GEM Tab (Protocol Panel)
- Quick command buttons for common messages: S1F1 (Are You There?), S2F17 (Date/Time), GEM START/STOP/ABORT.
- Custom SxFy sender (stream/function + JSON payload).
- GEM-style host command sender (command + optional wafer id).
- Live message log showing both S/F streams and GEM commands with timestamps and data.
- Current equipment status and wafer count from the emulator.
- "Refresh Log" / "Clear view".

All tabs benefit from the live WebSocket connection and the central event timeline.

---

## Features That Are NOT Available Through the UI

The UI is an excellent operator / demo surface, but many powerful capabilities live only in the backend, CLI, or direct code.

**AI / Training**
- Full, long-running PPO training with proper evaluation callbacks and model saving (use `python -m fabforge.rl_optimizer` or call `RLFabOptimizer().train(total_timesteps=...)` directly). The UI only offers a short visible demo.
- Real TensorBoard curves from a serious training run (the UI just links to the server).

**Protocols & Integration (deeper / external use)**
- Starting and interacting with the real OPC-UA server from external clients (the backend starts it on `opc.tcp://0.0.0.0:4840`, but you can browse/call nodes from any OPC-UA client).
- Real MQTT pub/sub against an external broker for telemetry or command injection.
- Using the SECS/GEM emulator from your own MES prototype code (the layer is reusable; the UI only exercises a subset).
- No real HSMS-SS (TCP) or SECS-I (serial) wire transport — it is pure message emulation.

**Simulation & Low-Level Control**
- Direct access to the C++ objects (`Wafer`, `PLCEngine`, `EquipmentStateMachine`, per-wafer history via PyBind11) from your own Python scripts beyond what the backend returns.
- Standalone execution of the C++ simulator (`./fab_sim`) for custom logging or embedding.
- The full internal `fab_state` mutation logic and background loops (telemetry, event pushing, anomaly scoring) are only indirectly visible.

**Orchestration & Tooling**
- The end-to-end demo script (`demo/end_to_end_demo.py`) that strings C++ sim + MQTT + OPC-UA + SECS/GEM + predictive + RL together.
- Native binary rebuild process (`python build_cpp.py`).
- Running the test suite.
- Docker / Kubernetes deployment.
- Direct calls to many backend-only or internal endpoints (`/api/status`, `/api/events`, `/api/simulate/stream`, the exact drift math, etc.).

**Other**
- Real persisted ML models for predictive maintenance in a production setting (the module can save/load, but the UI treats it as best-effort).
- Any production-scale physics or fab layout (current model is intentionally simplified for demo clarity and interview focus).

In short: the UI shows the *experience* an operator or engineer would have. The real power for integration, training, and extension lives in the layers, the backend services, the CLI, and the C++ core.

---

## Recommended Starting Points

1. `python -m fabforge.cli simulate --num-wafers 12 --steps 4 --use-cpp` (or without `--use-cpp`).
2. Start backend + frontend as described in the README.
3. Walk through the five tabs while a simulation or live player is running.
4. Use the SECS/GEM and Controls panels to send commands and watch the system react.
5. Trigger "Train PPO Live" and open TensorBoard in another tab.
6. For deeper work, read the layer files and the backend, then write small scripts that use them directly.

This project is deliberately built so you can start at the pretty UI and gradually go deeper into protocols, AI, or low-level simulation — exactly the journey a real automation/controls engineer would take.

For interview/demo scripting, see `Terafab_Application_Package.md` and `demo/end_to_end_demo.py`.

Run it, break it, extend it, and ship something that actually helps keep billion-dollar fabs running.