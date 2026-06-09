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
grok-fab dashboard --port 8501
```
Launches Streamlit visualization.

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