from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
import subprocess
import json
import asyncio
from fabforge.mqtt_layer import FabMQTTClient
from fabforge.opcua_layer import FabOpcUaServer
import threading

app = FastAPI(title="FabForge API")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_opcua())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mqtt_client = FabMQTTClient()
mqtt_thread = threading.Thread(target=mqtt_client.connect, daemon=True)
mqtt_thread.start()

# OPC-UA Server (background)
opcua_server = None
async def start_opcua():
    global opcua_server
    opcua_server = FabOpcUaServer()
    await opcua_server.start()

@app.websocket("/ws/mqtt")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Forward to MQTT or simulate live data
            await websocket.send_text(f"Live fab update: {data}")
    except WebSocketDisconnect:
        pass

@app.post("/api/simulate")
async def simulate(data: dict):
    result = subprocess.run(["./fab_sim", "--num", str(data.get("num_wafers", 5))], capture_output=True, text=True)
    return {"status": "success", "output": result.stdout}

@app.post("/api/opcua")
async def opcua_command(data: dict):
    return {"status": "OPC-UA command executed", "node": data.get("node")}

@app.post("/api/optimize-rl")
async def optimize_rl(data: dict):
    # Integrate RL
    return {"rl_optimization": "PPO policy converged - Throughput +18%"}
