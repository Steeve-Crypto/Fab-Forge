# FabForge: Intelligent Semiconductor Fab Simulator & Automation Engine

[![CI](https://github.com/YOURNAME/fabforge/actions/workflows/ci.yml/badge.svg)](https://github.com/YOURNAME/fabforge/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/YOURNAME/fabforge/branch/main/graph/badge.svg)](https://codecov.io/gh/YOURNAME/fabforge)

**FabForge** is a production-grade portfolio project demonstrating end-to-end skills for **Automation, Controls & AI Software Engineer** roles at advanced semiconductor fabs (Terafab-scale, 1TW AI silicon).

See `Terafab_Application_Package.md` for resume bullets, demo video script, and GitHub setup instructions.

**For a complete explanation of real-world value, every section/layer, detailed UI usage, and features that exist only outside the browser UI, read `docs/USAGE_AND_REAL_WORLD_GUIDE.md`.**

It delivers a **full digital twin** of a multi-stage wafer fab with real-time controls, industrial protocols, ML predictive maintenance, and PPO reinforcement learning optimization — all exposed through a beautiful live Vue + FastAPI dashboard with WebSocket streaming.

## Highlights (What Makes This Stand Out)

- **Native C++ Discrete-Event Core** — high-fidelity lithography → etch → deposition simulation with stochastic timing + emulated IEC 61131-3 PLC ladder logic and equipment state machines (IDLE / PROCESSING / MAINT / FAULT).
- **Cross-Platform Today** — excellent pure-Python fallback that produces identical fidelity output. `fab_sim` Linux binary + full Windows support via `python build_cpp.py`.
- **Industrial Protocols** — Expanded OPC-UA digital twin server + MQTT pub/sub + full **SECS/GEM (SEMI E5/E30)** host/equipment message emulator with interactive panel.
- **AI & Predictive** — PPO (Stable-Baselines3) scheduler optimizer + RandomForest / heuristic predictive maintenance with live risk scoring and alerts in the Vue UI.
- **Production-Style Full-Stack Dashboard** — Dark industrial Vue 3 + FastAPI + WebSocket live telemetry. Real-time tool cards, interactive controls, yield charts, **live simulation player** (step-by-step streaming playback), and dedicated SECS/GEM terminal.
- **Ready for Interview Demos** — One-command CLI, runnable backend + frontend, tests, and a compelling story about safe high-volume AI chip production orchestration.

## Quick Start (Windows & Cross-Platform)

```bash
# 1. Python environment (core packages are light; heavy ML are optional with graceful fallbacks)
pip install -r requirements.txt
# For full optional features: pip install torch scikit-learn pandas numpy paho-mqtt asyncua

# 2. Run the FabForge CLI (the "fab forge" command)
python -m fabforge.cli simulate --num-wafers 12 --steps 5
python -m fabforge.cli simulate --num-wafers 20 --steps 4 --use-cpp   # tries native if you built it

# 3. (Optional but awesome) Build the real C++ core for Windows
python build_cpp.py
# On success: fab_sim.exe appears + fabforge_cpp.pyd is importable.
# Requires: Visual Studio Build Tools "Desktop development with C++" + run from "x64 Native Tools Command Prompt".

# 4. Launch the full live dashboard (two terminals)
# IMPORTANT: Run the backend command from the PROJECT ROOT
# (the directory that contains both "dashboard/" and "fabforge/").

# Terminal A - Backend (FastAPI + WS + all protocol emulation)
python -m uvicorn dashboard.fastapi_backend:app --port 8000

# Terminal B - Frontend (Vue 3 + Vite, already has proxy to :8000)
cd dashboard/vue-app
npm run dev
# Open http://localhost:5174 (or the port Vite reports)

# Alternative (recommended after `pip install -e .`):
#   grok-fab dashboard --port 8000
# This works even if your current directory is inside dashboard/vue-app.
```

In the dashboard:
- **SIM** tab → configure & run simulation → beautiful yield chart + wafer table → **Live Simulation Player** (Play/Pause/Speed + backend WS streaming option).
- **CONTROLS** → click START/STOP/MAINT on live tool cards (state, temp, pressure, util update in real time via WS).
- **OPTIMIZE** → trigger PPO-style scheduling optimization with before/after viz.
- **PREDICTIVE** → run failure risk predictions per tool (risk bars + mini trends + red alerts that flip tool state).
- **SECS/GEM** (new) → send S1F1 / S2F17 streams and GEM host commands; watch the structured message log.

## Project Structure

```
fabforge/               # Python package (cli, layers, predictive, rl)
  cli.py                # grok-fab style CLI (simulate, secsgem, mqtt, dashboard, ...)
  mqtt_layer.py / opcua_layer.py / secsgem_layer.py
  predictive_maintenance.py / rl_optimizer.py
src/cpp/simulation/     # Real C++ core (Wafer, FabSimulator, PLCEngine, StateMachines, bindings)
build_cpp.py            # One-command Windows (and Unix) native build helper
dashboard/
  fastapi_backend.py    # FastAPI + WS live telemetry, simulate, control, predict, optimize, SECS/GEM
  vue-app/              # Modern industrial Vue 3 dashboard (Vite)
    src/
      App.vue (live topbar + WS metrics)
      components/ (Simulation with player, Controls, Optimization, SECSGEMView, ...)
tests/                  # pytest suite (simulator, predictive, secsgem, api contracts)
build/                  # CMake artifacts (Linux ELF previously; now Windows too)
```

## Running Tests

```bash
pip install pytest httpx   # TestClient needs httpx
python -m pytest tests/ -q --tb=short
```

Tests cover the Python simulator fidelity, predictive (with/without sklearn), SECS/GEM emulator, and FastAPI endpoints.

## Native C++ + PyBind11 on Windows

See `build_cpp.py` (top of file has detailed prerequisites).

After a successful build you can force the real C++ core from the CLI (`--use-cpp`) and the dashboard will still use the rich Python data path (the native prints the authentic low-level trace).

## Architecture & Skills Demonstrated

- **Low-level systems**: C++17 discrete-event sim, manual memory (unique_ptr), state machines, PLC ladder emulation.
- **Bindings & integration**: PyBind11 exposing C++ objects cleanly to Python (with compatibility shims).
- **Industrial software**: Real protocol emulation (OPC-UA server with methods/variables, MQTT, SECS/GEM S/F streams + GEM host commands).
- **AI/ML for manufacturing**: Gymnasium + Stable-Baselines3 PPO for fab scheduling; scikit-learn (or heuristic fallback) predictive maintenance.
- **Modern full-stack**: FastAPI + WebSockets for live digital twin, Vue 3 + Chart.js + reactive controls, clean component architecture.
- **Cross-platform engineering**: Python fallback that matches C++ behavior exactly so demos always work; build script that gives actionable errors.

## TensorBoard (RL Training Curves)

```bash
tensorboard --logdir ./tb_logs --port 6006
```

(Works when you actually train the PPO model via `python -m fabforge.rl_optimizer`.)

## Why This Project

It directly attacks the hardest problems in high-volume AI semiconductor manufacturing:
- Throughput & yield under variability
- Safe controls development without risking $B tools
- Real-time visibility + predictive maintenance for 99.999% uptime
- Protocol translation between fab MES and equipment

Perfect for demonstrating **you can ship complex, production-like automation software**.

## Next Steps / Polish Ideas (for interviews)

- Add real HSMS-SS transport shim for SECS/GEM
- Expose more native C++ data (per-wafer yields) back through PyBind11
- Add a 3D-ish mini fab floorplan that lights up during the live player
- Hook the RL policy into the live player for "what-if" optimized runs

**Built with ❤️ for the Terafab Automation & Controls interview loop.**

See also:
- `CLI.md` — full command reference
- `docs/` — deployment, predictive maintenance, demo video script
- `demo/end_to_end_demo.py` — scripted full pipeline walk-through
