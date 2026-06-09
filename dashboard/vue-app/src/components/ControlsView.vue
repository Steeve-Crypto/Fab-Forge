<template>
  <div>
    <div class="card" style="margin-bottom:16px">
      <h2>Real-time Equipment Controls</h2>
      <div style="color:#7f8ea3;font-size:12px">PLC ladder emulation • State machines • MQTT / OPC-UA command bridge</div>
    </div>

    <div class="tool-grid" style="margin-bottom:16px">
      <div v-for="(td, name) in tools" :key="name" class="tool-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <div style="font-weight:600;font-size:15px">{{ name }}</div>
          <span class="status-pill" :class="{ running: td.status==='Processing', fault: td.status==='Maintenance' || td.status==='Fault' }">
            {{ td.status }}
          </span>
        </div>
        <div style="font-size:12px;line-height:1.4;color:#a8b8cc">
          TEMP <b style="color:#d6e1ed">{{ td.temp }}°C</b> &nbsp; PRESS <b>{{ td.pressure }}</b><br/>
          UTIL <b>{{ td.util }}%</b>
        </div>
        <div style="margin-top:12px;display:flex;gap:6px;flex-wrap:wrap">
          <button class="btn" style="padding:5px 10px;font-size:12px" @click="sendControl(name, 'START')">START</button>
          <button class="btn secondary" style="padding:5px 10px;font-size:12px" @click="sendControl(name, 'STOP')">STOP</button>
          <button class="btn secondary" style="padding:5px 10px;font-size:12px" @click="sendControl(name, 'MAINT')">MAINT</button>
          <button class="btn secondary" style="padding:5px 10px;font-size:12px" @click="sendControl(name, 'RESET')">RESET</button>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>Live Control Log + Telemetry</h3>
      <div class="log" ref="logEl" style="min-height:160px">
        <div v-for="(line, i) in logLines" :key="i" style="margin:1px 0">{{ line }}</div>
        <div v-if="!logLines.length" style="color:#5a6878">No events yet. Send a command or start the backend live feed.</div>
      </div>
      <div style="margin-top:8px">
        <button class="btn secondary" @click="sendMqttDemo">Send MQTT demo telemetry</button>
        <button class="btn secondary" style="margin-left:6px" @click="clearLog">Clear log</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'

const tools = reactive({
  Lithography: { status: 'Idle', temp: 195.0, pressure: 0.5, util: 72 },
  Etch: { status: 'Idle', temp: 68.0, pressure: 0.012, util: 81 },
  Deposition: { status: 'Idle', temp: 320.0, pressure: 1.2, util: 65 },
})

const logLines = ref([])
const logEl = ref(null)
let ws = null
let pollTimer = null

function pushLog(msg) {
  const ts = new Date().toLocaleTimeString()
  logLines.value.push(`[${ts}] ${msg}`)
  if (logLines.value.length > 28) logLines.value.shift()
  nextTick(() => {
    if (logEl.value) logEl.value.scrollTop = logEl.value.scrollHeight
  })
}

async function sendControl(tool, action) {
  pushLog(`→ ${action} → ${tool}`)
  try {
    const { data } = await axios.post('/api/control', { tool, action })
    if (data.new_state) {
      Object.assign(tools[tool], data.new_state)
    }
    pushLog(`✓ ${tool} now ${tools[tool].status}`)
  } catch (e) {
    pushLog(`ERR control ${tool}: ${e.message || e}`)
  }
}

async function sendMqttDemo() {
  const tool = Object.keys(tools)[Math.floor(Math.random()*3)]
  const msg = { temp: tools[tool].temp, state: tools[tool].status }
  await axios.post('/api/mqtt', { topic: `fab/telemetry/${tool.toLowerCase()}`, message: JSON.stringify(msg) })
  pushLog(`MQTT pub fab/telemetry/${tool.toLowerCase()}`)
}

function clearLog() { logLines.value = [] }

function applyTelemetry(tel) {
  Object.keys(tel).forEach(k => {
    if (tools[k]) Object.assign(tools[k], tel[k])
  })
}

function connectWS() {
  try {
    ws = new WebSocket('ws://localhost:8000/ws/live')
    ws.onmessage = (ev) => {
      try {
        const m = JSON.parse(ev.data)
        if (m.type === 'telemetry' && m.tools) applyTelemetry(m.tools)
        if (m.type === 'init' && m.state?.tools) applyTelemetry(m.state.tools)
        if (m.type === 'ack') pushLog(`ACK: ${m.action} on ${m.tool}`)
      } catch (_) {}
    }
    ws.onclose = () => { setTimeout(connectWS, 3000) }
  } catch (_) {}
}

async function loadInitial() {
  try {
    const { data } = await axios.get('/api/status')
    if (data.fab?.tools) applyTelemetry(data.fab.tools)
  } catch (_) {}
  // also fetch recent events
  try {
    const { data } = await axios.get('/api/events?limit=8')
    data.events?.forEach(e => pushLog(`${e.kind.toUpperCase()}: ${e.message}`))
  } catch (_) {}
}

onMounted(() => {
  loadInitial()
  connectWS()
  pollTimer = setInterval(loadInitial, 8000)
})

onUnmounted(() => {
  if (ws) ws.close()
  if (pollTimer) clearInterval(pollTimer)
})
</script>