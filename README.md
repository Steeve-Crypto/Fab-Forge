# FabForge: Intelligent Semiconductor Fab Simulator & Automation Engine

## Project Overview
FabForge is a comprehensive software platform designed to simulate, control, and optimize semiconductor manufacturing processes. Built to demonstrate advanced skills for Terafab roles in Automation, Controls, and AI Engineering.

**Key Features:**
- High-performance C++ discrete event simulation for fab workflows
- Real-time equipment controls emulation (PLC-style)
- Industrial protocols: **MQTT + Expanded OPC-UA** (full digital twin nodes for tools)
- Advanced PPO RL (Stable-Baselines3) for yield & scheduling optimization
- Vue.js + FastAPI hybrid dashboard with WebSockets
- Scalable data pipeline and predictive analytics

## Purpose
**FabForge** is the ultimate **complex problem-solving software** engineered to land you the **Automation & Controls Software Engineer** role at **Terafab**.

It solves **semiconductor fab orchestration nightmares at massive (1TW-scale) production**:
- **Multi-Stage Process Control**: C++ physics-informed simulation of lithography → etch → deposition flows with stochastic variability.
- **Industrial Protocol Integration**: Expanded **OPC-UA server** (equipment nodes, methods, variables) + MQTT for real-time MES/PLC communication.
- **AI Optimization**: RL for dynamic scheduling under uncertainty.
- **Safe Prototyping**: Full digital twin for testing controls without risking billion-dollar hardware.
- **Full-Stack Demo**: Vue.js live dashboard with WebSockets + FastAPI bridge.

## Getting Started
See `CLI.md` for command-line interface usage.

## Structure
- `src/` - Core C++/Python code
- `dashboard/` - Vue.js + FastAPI hybrid frontend (C++ backend integration)
- `docs/` - Detailed documentation
- `simulations/` - Scenario definitions
- `tests/` - Unit and integration tests

**Target**: Portfolio project to land Automation Software Engineer role at Terafab.
## Predictive Maintenance Module (New)
- ML-based failure prediction (RandomForest + time-series)
- Integrates with MQTT/OPC-UA/RL for proactive fab maintenance
- Critical for Terafab's high-uptime AI chip production
