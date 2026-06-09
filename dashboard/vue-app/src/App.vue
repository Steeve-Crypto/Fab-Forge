<template>
  <div id="app" :class="{ 'connected': wsConnected }">
    <!-- Top Industrial Header -->
    <header class="topbar">
      <div class="brand">
        <div class="logo">⚙︎</div>
        <div>
          <div class="title">FABFORGE</div>
          <div class="subtitle">TERAFAB DIGITAL TWIN</div>
        </div>
      </div>

      <div class="status-bar">
        <div class="metric" v-for="(val, key) in quickMetrics" :key="key">
          <span class="label">{{ key }}</span>
          <span class="value">{{ val }}</span>
        </div>
        <div class="conn" :class="{ live: wsConnected, dead: !wsConnected }">
          {{ wsConnected ? '● LIVE' : '○ OFFLINE' }}
        </div>
      </div>

      <nav class="nav">
        <router-link to="/" exact-active-class="active">SIM</router-link>
        <router-link to="/controls" active-class="active">CONTROLS</router-link>
        <router-link to="/optimization" active-class="active">OPTIMIZE</router-link>
        <router-link to="/predictive" active-class="active">PREDICTIVE</router-link>
        <router-link to="/secsgem" active-class="active">SECS/GEM</router-link>
      </nav>
    </header>

    <div class="main">
      <router-view v-slot="{ Component }">
        <component :is="Component" @fab-event="onFabEvent" />
      </router-view>
    </div>

    <footer class="footer">
      <div>Terafab • 1TW-scale AI silicon • Real-time OPC-UA + MQTT + PPO RL</div>
      <div class="events-mini" v-if="recentEvent">
        LAST: <span>{{ recentEvent.message }}</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import axios from 'axios'

const wsConnected = ref(false)
const quickMetrics = reactive({ YIELD: '—', WPH: '—', TOOLS: '3/3', ALERTS: '0' })
const recentEvent = ref(null)
let ws = null
let statusTimer = null

function connectLiveWS() {
  // Direct to backend (vite proxy covers /api http only)
  const wsUrl = 'ws://localhost:8000/ws/live'
  try {
    ws = new WebSocket(wsUrl)
    ws.onopen = () => { wsConnected.value = true }
    ws.onclose = () => { wsConnected.value = false; setTimeout(connectLiveWS, 2800) }
    ws.onerror = () => { wsConnected.value = false }
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data)
        if (msg.type === 'telemetry' && msg.tools) {
          // update quick metrics from live
          const tools = Object.keys(msg.tools).length
          quickMetrics.TOOLS = `${tools}/3`
        }
        if (msg.type === 'init' && msg.state) {
          updateQuickFromState(msg.state)
        }
      } catch (_) {}
    }
  } catch (e) {
    wsConnected.value = false
  }
}

function updateQuickFromState(state) {
  if (!state) return
  if (state.avg_yield) quickMetrics.YIELD = (state.avg_yield * 100).toFixed(1) + '%'
  if (state.throughput) quickMetrics.WPH = state.throughput
  if (state.tools) {
    const alerts = Object.values(state.tools).filter(t => t.status === 'Maintenance' || t.status === 'Fault').length
    quickMetrics.ALERTS = String(alerts)
  }
}

function onFabEvent(evt) {
  if (evt && evt.type === 'sim' && evt.result) {
    quickMetrics.YIELD = (evt.result.avg_yield * 100).toFixed(1) + '%'
    if (evt.fab_state && evt.fab_state.throughput) quickMetrics.WPH = evt.fab_state.throughput
  }
  recentEvent.value = { message: evt?.message || 'Event received' }
  setTimeout(() => { recentEvent.value = null }, 4200)
}

async function pollStatus() {
  try {
    const { data } = await axios.get('/api/status')
    if (data && data.fab) {
      updateQuickFromState(data.fab)
      if (data.fab.last_sim && data.fab.last_sim.avg_yield) {
        quickMetrics.YIELD = (data.fab.last_sim.avg_yield * 100).toFixed(1) + '%'
      }
    }
  } catch (_) {}
}

onMounted(() => {
  connectLiveWS()
  pollStatus()
  statusTimer = setInterval(pollStatus, 6500)
})

onUnmounted(() => {
  if (ws) ws.close()
  if (statusTimer) clearInterval(statusTimer)
})
</script>

<style>
:root {
  --bg: #0b0f14;
  --panel: #12181f;
  --panel-2: #1a222b;
  --accent: #00d1ff;
  --accent2: #00ff9d;
  --warn: #ff4d4f;
  --text: #d6e1ed;
  --muted: #7f8ea3;
}

* { box-sizing: border-box; }

#app {
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topbar {
  background: linear-gradient(180deg, #11161d, #0b0f14);
  border-bottom: 1px solid #1f2835;
  padding: 10px 22px;
  display: flex;
  align-items: center;
  gap: 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo {
  font-size: 28px;
  line-height: 1;
  color: var(--accent);
  filter: drop-shadow(0 0 6px rgba(0,209,255,0.6));
}
.title { font-weight: 700; letter-spacing: 3px; font-size: 20px; }
.subtitle { font-size: 10px; letter-spacing: 1.5px; color: var(--muted); margin-top: -2px; }

.status-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-left: 8px;
  padding: 4px 12px;
  background: var(--panel);
  border-radius: 999px;
  border: 1px solid #1f2835;
}
.metric {
  font-size: 11px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 54px;
}
.metric .label { color: var(--muted); font-size: 9px; text-transform: uppercase; letter-spacing: .5px; }
.metric .value { font-weight: 600; font-variant-numeric: tabular-nums; color: var(--accent2); }

.conn {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: #1f2835;
  color: var(--muted);
}
.conn.live { color: var(--accent2); background: rgba(0,255,157,0.1); }
.conn.dead { color: var(--warn); }

.nav {
  margin-left: auto;
  display: flex;
  gap: 4px;
}
.nav a {
  color: var(--muted);
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: .6px;
  transition: all .1s ease;
}
.nav a:hover { color: var(--text); background: #1a222b; }
.nav a.active { color: #0b0f14; background: var(--accent); font-weight: 700; }

.main {
  flex: 1;
  padding: 22px;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
}

.footer {
  border-top: 1px solid #1f2835;
  padding: 10px 22px;
  font-size: 11px;
  color: var(--muted);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #0a0e13;
}
.events-mini { font-family: ui-monospace, monospace; font-size: 11px; }
.events-mini span { color: var(--accent); }

.card {
  background: var(--panel);
  border: 1px solid #1f2835;
  border-radius: 10px;
  padding: 16px;
}
.card h2, .card h3 { margin: 0 0 12px; font-size: 15px; letter-spacing: .5px; color: #a8b8cc; }
.btn {
  background: var(--accent);
  color: #0b0f14;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  font-size: 13px;
  transition: transform .05s ease, filter .1s;
}
.btn:hover { filter: brightness(1.08); }
.btn:active { transform: translateY(1px); }
.btn.secondary { background: #1f2835; color: var(--text); }
.input {
  background: #0b0f14;
  border: 1px solid #2a3645;
  color: var(--text);
  padding: 7px 10px;
  border-radius: 6px;
  font-size: 13px;
}
.kpi {
  background: var(--panel-2);
  border: 1px solid #1f2835;
  padding: 10px 14px;
  border-radius: 8px;
  text-align: center;
}
.kpi .num { font-size: 22px; font-weight: 700; color: var(--accent2); }
.kpi .lab { font-size: 10px; color: var(--muted); text-transform: uppercase; }

.tool-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.tool-card {
  background: var(--panel-2);
  border: 1px solid #24313f;
  border-radius: 8px;
  padding: 12px;
}
.status-pill {
  display: inline-block;
  font-size: 10px;
  padding: 1px 8px;
  border-radius: 999px;
  background: #24313f;
}
.status-pill.running { background: rgba(0,255,157,.15); color: var(--accent2); }
.status-pill.fault { background: rgba(255,77,79,.15); color: var(--warn); }

.log {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background: #0b0f14;
  border: 1px solid #1f2835;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  max-height: 220px;
  overflow: auto;
  white-space: pre-wrap;
}
</style>