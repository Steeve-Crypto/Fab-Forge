# Terafab Application Package — FabForge

**Candidate**: [Your Name]  
**Role**: Automation & Controls Software Engineer (AI / Digital Twin focus)  
**Project**: FabForge — Intelligent Semiconductor Fab Simulator & Automation Engine

**For the full story** (real-world value, detailed breakdown of every section + how to use it, complete UI feature tour, and explicit list of capabilities that are *not* available in the browser), see `docs/USAGE_AND_REAL_WORLD_GUIDE.md`.

---

## One-Pager Summary (for Recruiter / Hiring Manager)

FabForge is a complete, production-style digital twin of a 1TW-scale AI silicon fab. It demonstrates end-to-end ownership of the full stack required for modern semiconductor automation:

- High-fidelity **C++ discrete-event simulation** (lithography → etch → deposition) with stochastic variability and IEC 61131-3 PLC/state-machine emulation.
- Real **industrial protocols**: OPC-UA digital twin server, MQTT, and full **SECS/GEM (SEMI E5/E30)** host/equipment messaging.
- **AI/ML**: PPO reinforcement learning for dynamic scheduling + predictive maintenance (failure risk + anomaly detection on sensor drift).
- **Live full-stack dashboard**: Vue 3 + FastAPI + WebSockets with real-time tool cards, interactive controls, live simulation playback, yield heatmaps, and a dedicated SECS/GEM panel.
- **Cross-platform & production-ready**: Excellent pure-Python fallback (identical behavior), one-command Windows native build (`python build_cpp.py`), pytest coverage, and clean separation of concerns.

This project directly proves I can design safe controls, integrate factory protocols, apply RL to real manufacturing objectives, and deliver a beautiful, usable operator interface — all without risking actual billion-dollar equipment.

**Key Demo Flow (90–120 seconds)**:
1. CLI: `python -m fabforge.cli simulate --num-wafers 20 --steps 5 --use-cpp`
2. Dashboard (http://localhost:5174): Run sim → watch Live Player + SVG wafer flow + yield heatmap update in real time.
3. Controls tab: Click START/STOP on live tools; watch WS telemetry + state machines.
4. SECS/GEM tab: Send S1F1 / S2F17 and GEM commands; see structured log.
5. Predictive: Trigger risk predictions + anomaly flags (sensor drift rules).
6. Optimize: Run policy + “Train PPO Live” (progress + TensorBoard link).

---

## Demo Video Script (for submission / interview)

**Title**: FabForge — Full Digital Twin for Terafab Automation (3–4 min)

**0:00–0:20** — Intro + Motivation  
“Hi, I’m [Name]. This is FabForge — a complete digital twin I built to demonstrate the exact skills Terafab needs for Automation & Controls at 1TW scale.”

**0:20–1:10** — C++ Core + Native Build  
Show terminal: `python build_cpp.py` (or pre-built).  
Run with `--use-cpp`. Point out authentic C++ trace (state transitions, PLC ladder, yield degradation).  
“Real discrete-event engine with IEC 61131-3 emulation, exposed cleanly via PyBind11.”

**1:10–2:20** — Live Dashboard + Player  
Open Vue UI.  
- Run simulation with sliders.  
- Show wafer table + **yield heatmap** (green cells).  
- Launch **Live Simulation Player**: play/pause/speed + **SVG real-time wafer path** (wafer dot moves Litho → Etch → Depo).  
- While playing, open Controls tab — tools flip to Processing, WS telemetry streams.

**2:20–2:50** — Industrial Protocols  
Switch to SECS/GEM panel.  
Send S1F1, S2F17, GEM START/STOP.  
“Full SEMI E5/E30 emulation — the same messages that travel between real MES and equipment.”

**2:50–3:30** — AI Layer  
Predictive tab: run predictions, show risk bars + anomaly flags on drifted sensors.  
Optimization: “Run PPO”, then “Train PPO Live” button — watch progress bar + live reward/loss via WebSocket.  
Mention TensorBoard link for actual training curves.

**3:30–end** — Why This Matters + Close  
“Every piece is production-grade: native performance, protocol fidelity, live observability, safe RL experimentation.  
I can ship the controls, the integration layer, the operator UI, and the intelligence — and I can demo it end-to-end today.”

(End screen: GitHub link, `python -m fabforge.cli simulate`, dashboard URL, contact)

---

## GitHub Setup & Run Instructions (for reviewers)

```bash
# 1. Clone
git clone <your-repo>
cd fab

# 2. Python deps (core)
pip install -r requirements.txt
# Optional for full AI: pip install torch scikit-learn pandas numpy paho-mqtt asyncua pytest httpx

# 3. (Recommended) Build native C++ core (Windows)
# Requires Visual Studio "Desktop development with C++" workload
python build_cpp.py

# 4. Quick CLI test (native if built)
python -m fabforge.cli simulate --num-wafers 12 --steps 4 --use-cpp

# 5. Full live demo (two terminals)
# Terminal A
python -m uvicorn dashboard.fastapi_backend:app --port 8000

# Terminal B
cd dashboard/vue-app
npm install   # only first time
npm run dev
# Open http://localhost:5174 (or port shown)
```

**Tests**:
```bash
pip install pytest httpx
python -m pytest tests/ -q
```

**TensorBoard** (after any RL training):
```bash
tensorboard --logdir ./tb_logs --port 6006
```

**Rebuild native after C++ changes**:
```bash
python build_cpp.py
```

---

## Resume Tie-In Bullets (copy-paste ready)

- Designed and implemented a full-stack digital twin for semiconductor manufacturing, including a high-performance C++ discrete-event simulator with PyBind11 bindings and real-time Vue + FastAPI dashboard.
- Integrated production industrial protocols (OPC-UA, MQTT, SECS/GEM) and emulated IEC 61131-3 PLC logic + equipment state machines.
- Applied reinforcement learning (PPO) for fab scheduling optimization and built ML-based predictive maintenance with anomaly detection on sensor drift.
- Delivered live operator experience with WebSocket streaming, interactive simulation playback, yield heatmaps, and protocol command panels.
- Achieved true cross-platform execution (excellent Python fallback + one-command native Windows build) with automated tests and clean CI.

**Technologies**: C++17, PyBind11, Python, FastAPI, Vue 3, WebSockets, Chart.js, Stable-Baselines3 / Gymnasium, scikit-learn, OPC-UA (asyncua), MQTT, SECS/GEM emulation.

---

## GitHub Actions / CI (recommended to add)

See `.github/workflows/ci.yml` (created alongside this package). It runs:
- Python tests on push/PR
- Coverage report (pytest-cov)
- (Optional) build check for the C++ side on Windows runner if desired

**Badge to add to README** (example):
```markdown
![CI](https://github.com/YOURNAME/fabforge/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/YOURNAME/fabforge/branch/main/graph/badge.svg)](https://codecov.io/gh/YOURNAME/fabforge)
```

---

This package + the working FabForge repo is designed to be the centerpiece of your Terafab interview loop. Run it live, walk through the code, and you will stand out.

Good luck — you’ve built something genuinely impressive.