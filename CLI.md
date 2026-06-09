# Grok CLI for FabForge

The Grok CLI is a command-line interface tool integrated into FabForge, allowing users to interact with the simulation engine, run optimizations, monitor controls, and generate reports. Inspired by powerful AI-assisted development, it leverages Grok-like capabilities for interactive fab engineering.

## Installation
```bash
# After setting up the project
pip install -e .
# or build C++ components
cmake -B build && cmake --build build
```

## Commands

### Simulation
```bash
grok-fab simulate --scenario lithography --steps 1000 --output results.json
```
Runs a wafer processing simulation.

### Controls
```bash
grok-fab control --equipment etch-chamber --state start --monitor
```
Emulates PLC logic for specific tools.

### Optimization
```bash
grok-fab optimize --objective yield --constraints energy=500kWh --algorithm ga
```
Runs genetic algorithm or RL for scheduling.

### Data & Dashboard
```bash
grok-fab dashboard --port 8000
```
Launches the FastAPI backend (for the Vue.js dashboard).

To run the full interactive dashboard:
- Terminal 1: `python -m uvicorn dashboard.fastapi_backend:app --port 8000`
- Terminal 2: `cd dashboard/vue-app && npm run dev`

Then open the URL shown by Vite (usually http://localhost:5173 or 5174). This is the primary production-style dashboard with WebSocket live updates, simulation player, controls, predictive maintenance, SECS/GEM panel, etc.

(Note: Older project docs referenced a Streamlit dashboard on port 8501. That was superseded by the current Vue + FastAPI implementation. Streamlit is no longer used.)

### Protocols
```bash
grok-fab mqtt publish --topic fab/sensor1 --message "temp:250"
grok-fab opcua server --start
```

## Purpose of CLI
- Rapid prototyping and testing of fab scenarios
- Scriptable automation for CI/CD pipelines in manufacturing software dev
- Interactive debugging of complex control systems

Full API reference in `docs/cli-reference.md` (to be expanded).