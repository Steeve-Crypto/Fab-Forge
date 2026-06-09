<template>
  <div>
    <div class="card" style="margin-bottom:16px">
      <h2 style="margin-bottom:4px">Wafer Process Simulation</h2>
      <div style="color:#7f8ea3;font-size:12px;margin-bottom:12px">C++ core (or Python fallback) • Discrete-event + PLC state machines</div>

      <div style="display:flex;gap:16px;align-items:flex-end;flex-wrap:wrap">
        <div>
          <div style="font-size:11px;color:#7f8ea3;margin-bottom:4px">WAFERS</div>
          <input v-model.number="params.num_wafers" type="range" min="3" max="60" step="1" style="width:220px" />
          <div style="font-size:13px;font-weight:600">{{ params.num_wafers }}</div>
        </div>
        <div>
          <div style="font-size:11px;color:#7f8ea3;margin-bottom:4px">PROCESS STEPS</div>
          <input v-model.number="params.steps" type="range" min="2" max="9" step="1" style="width:180px" />
          <div style="font-size:13px;font-weight:600">{{ params.steps }}</div>
        </div>
        <button class="btn" @click="runSimulation" :disabled="running">
          {{ running ? 'SIMULATING...' : '▶ RUN SIMULATION' }}
        </button>
        <button class="btn secondary" @click="runSimulation(true)">Run + Auto-Chart</button>
      </div>
    </div>

    <div v-if="results" class="grid" style="display:grid;grid-template-columns:1fr 380px;gap:16px">
      <!-- KPIs + Wafers Table -->
      <div class="card">
        <h3>RESULTS</h3>
        <div style="display:flex;gap:12px;margin-bottom:14px">
          <div class="kpi" style="flex:1">
            <div class="num">{{ (results.avg_yield*100).toFixed(2) }}%</div>
            <div class="lab">AVG YIELD</div>
          </div>
          <div class="kpi" style="flex:1">
            <div class="num">{{ results.num_wafers }}</div>
            <div class="lab">WAFERS</div>
          </div>
          <div class="kpi" style="flex:1">
            <div class="num">{{ results.steps }}</div>
            <div class="lab">STEPS</div>
          </div>
          <div class="kpi" style="flex:1">
            <div class="num">{{ results.mode || 'core' }}</div>
            <div class="lab">MODE</div>
          </div>
        </div>

        <div class="log" style="margin-bottom:10px">
          Simulation finished. Average yield {{ (results.avg_yield*100).toFixed(2) }}%
        </div>

        <table style="width:100%;font-size:12px;border-collapse:collapse">
          <thead>
            <tr style="color:#7f8ea3;text-align:left;border-bottom:1px solid #24313f">
              <th style="padding:4px 6px">#</th>
              <th style="padding:4px 6px">YIELD</th>
              <th style="padding:4px 6px">PROCESS HISTORY</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="w in results.wafers.slice(0,12)" :key="w.id" style="border-bottom:1px solid #1f2835">
              <td style="padding:4px 6px;font-family:monospace">W{{ String(w.id).padStart(2,'0') }}</td>
              <td style="padding:4px 6px">
                <span :style="{color: w.yield > 0.985 ? '#00ff9d' : w.yield > 0.97 ? '#ffcc00' : '#ff4d4f'}">{{ (w.yield*100).toFixed(2) }}%</span>
              </td>
              <td style="padding:4px 6px;font-size:11px;color:#8fa2b8">{{ formatHistory(w.history) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="results.wafers.length > 12" style="font-size:11px;color:#7f8ea3;margin-top:6px">+ {{ results.wafers.length - 12 }} more wafers…</div>

        <!-- Yield Heatmap -->
        <div style="margin-top:12px">
          <div style="font-size:11px;color:#7f8ea3;margin-bottom:4px">YIELD HEATMAP (one cell per wafer — greener = higher yield)</div>
          <div style="display:flex;flex-wrap:wrap;gap:3px">
            <div v-for="w in results.wafers" :key="w.id"
                 :title="'W' + w.id + ': ' + (w.yield*100).toFixed(2) + '%'"
                 :style="{ width: '14px', height: '14px', background: yieldColor(w.yield), borderRadius: '2px', border: '1px solid #24313f' }"></div>
          </div>
        </div>
      </div>

      <!-- Yield Distribution Chart -->
      <div class="card">
        <h3>YIELD DISTRIBUTION</h3>
        <canvas ref="chartRef" width="340" height="260" style="max-width:100%"></canvas>
        <div style="margin-top:8px;font-size:11px;color:#7f8ea3">Each bar = one wafer. Target &gt;98.5% highlighted.</div>
      </div>
    </div>

    <div v-else class="card" style="text-align:center;padding:42px 20px;color:#7f8ea3">
      Configure parameters above and run a simulation to populate live results, wafer table and chart.
    </div>

    <!-- LIVE STREAMING SIM PLAYER -->
    <div v-if="results" class="card" style="margin-top:16px">
      <h3>▶ Live Simulation Player (Streaming Playback)</h3>
      <div style="display:flex;gap:12px;align-items:center;margin:8px 0;flex-wrap:wrap">
        <button class="btn" :disabled="playing" @click="startPlayback">▶ Play Live</button>
        <button class="btn secondary" :disabled="!playing" @click="pausePlayback">⏸ Pause</button>
        <button class="btn secondary" @click="resetPlayback">⟲ Reset</button>

        <div style="margin-left:12px">
          Speed:
          <select v-model.number="playSpeed" class="input" style="width:auto">
            <option :value="0.5">0.5×</option>
            <option :value="1">1×</option>
            <option :value="2">2×</option>
            <option :value="4">4×</option>
            <option :value="8">8×</option>
          </select>
        </div>

        <button class="btn secondary" style="margin-left:auto" @click="triggerBackendStream">Also stream via backend WS</button>
      </div>

      <div style="background:#0b0f14;border:1px solid #1f2835;border-radius:6px;padding:10px 14px;margin-bottom:8px">
        <div style="font-size:13px;margin-bottom:4px">
          Playing: <b>Wafer {{ playState.currentWafer }}</b> / {{ results.num_wafers }} &nbsp; Step {{ playState.currentStep }} / {{ results.steps }}
          &nbsp; Current Tool: <span style="color:var(--accent)">{{ playState.currentTool || '—' }}</span>
        </div>

        <!-- Real-time Wafer Path SVG Flow Diagram -->
        <svg width="100%" height="58" style="margin:6px 0 4px;background:#0a0e13;border-radius:4px" viewBox="0 0 420 58">
          <!-- Stations -->
          <rect x="30" y="12" width="80" height="32" rx="4" fill="#1a222b" stroke="#00d1ff" stroke-width="1.5"/>
          <text x="70" y="32" fill="#a8b8cc" font-size="11" text-anchor="middle">Lithography</text>

          <rect x="170" y="12" width="80" height="32" rx="4" fill="#1a222b" stroke="#00d1ff" stroke-width="1.5"/>
          <text x="210" y="32" fill="#a8b8cc" font-size="11" text-anchor="middle">Etch</text>

          <rect x="310" y="12" width="80" height="32" rx="4" fill="#1a222b" stroke="#00d1ff" stroke-width="1.5"/>
          <text x="350" y="32" fill="#a8b8cc" font-size="11" text-anchor="middle">Deposition</text>

          <!-- Connecting lines (process flow) -->
          <line x1="110" y1="28" x2="170" y2="28" stroke="#24313f" stroke-width="2"/>
          <line x1="250" y1="28" x2="310" y2="28" stroke="#24313f" stroke-width="2"/>

          <!-- Moving wafer indicator -->
          <g :transform="waferTransform">
            <rect width="18" height="18" rx="3" fill="#00ff9d" stroke="#0b0f14" stroke-width="1.5" x="-9" y="-9"/>
            <text x="0" y="4" fill="#0b0f14" font-size="9" text-anchor="middle" font-weight="bold">W</text>
          </g>
        </svg>

        <div style="height:6px;background:#1f2835;border-radius:999px;overflow:hidden">
          <div :style="{ width: playProgress + '%', height:'100%', background:'var(--accent2)', transition:'width .1s linear' }"></div>
        </div>
        <div style="font-size:11px;color:#7f8ea3;margin-top:3px">{{ playState.message }}</div>
      </div>

      <div class="log" style="max-height:140px">
        <div v-for="(line, i) in playLog" :key="i">{{ line }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import axios from 'axios'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const results = ref(null)
const running = ref(false)
const params = reactive({ num_wafers: 12, steps: 5 })
const chartRef = ref(null)
let chart = null

// Live player state
const playing = ref(false)
const playSpeed = ref(1)
const playState = reactive({ currentWafer: 0, currentStep: 0, currentTool: '', message: 'Idle' })
const playLog = ref([])
let playTimer = null
let playIndex = 0
let flattenedSteps = [] // [{wafer, step, tool, duration?}]

const playProgress = computed(() => {
  if (!results.value || flattenedSteps.length === 0) return 0
  return Math.min(100, Math.round((playIndex / flattenedSteps.length) * 100))
})

const waferTransform = computed(() => {
  const tool = playState.currentTool
  let x = 40 // default left (before first station)
  if (tool === 'Lithography' || tool === 'Litho') x = 70
  else if (tool === 'Etch') x = 210
  else if (tool === 'Deposition' || tool === 'Depo') x = 350
  const y = 28
  return `translate(${x},${y})`
})

function flattenHistory() {
  if (!results.value?.wafers) return []
  const eq = ['Lithography', 'Etch', 'Deposition']
  const out = []
  results.value.wafers.forEach((w, wi) => {
    const hist = w.history || []
    hist.forEach((h, si) => {
      let tool = typeof h === 'string' ? (h.split(':')[0] || eq[si % 3]) : (h.step || eq[si % 3])
      out.push({ wafer: wi, step: si, tool, orig: h })
    })
  })
  return out
}

function startPlayback() {
  if (!results.value) return
  pausePlayback()
  flattenedSteps = flattenHistory()
  if (flattenedSteps.length === 0) return
  playIndex = 0
  playLog.value = []
  playing.value = true
  playState.message = 'Streaming simulation steps...'

  const tick = () => {
    if (!playing.value || playIndex >= flattenedSteps.length) {
      pausePlayback()
      playState.message = 'Playback complete'
      return
    }
    const s = flattenedSteps[playIndex]
    playState.currentWafer = s.wafer
    playState.currentStep = s.step
    playState.currentTool = s.tool
    playLog.value.push(`Wafer ${s.wafer} • ${s.tool} (step ${s.step})`)
    if (playLog.value.length > 18) playLog.value.shift()

    // Light live feel: occasionally update quick global state via a control call (demo only)
    if (Math.random() < 0.25) {
      // fire-and-forget (no await in timer)
      axios.post('/api/control', { tool: s.tool, action: 'START' }).catch(() => {})
    }

    playIndex += 1
    const delay = Math.max(60, Math.floor(420 / playSpeed.value))
    playTimer = setTimeout(tick, delay)
  }
  tick()
}

function pausePlayback() {
  playing.value = false
  if (playTimer) {
    clearTimeout(playTimer)
    playTimer = null
  }
}

function resetPlayback() {
  pausePlayback()
  playIndex = 0
  playState.currentWafer = 0
  playState.currentStep = 0
  playState.currentTool = ''
  playState.message = 'Idle'
  playLog.value = []
  flattenedSteps = []
}

async function triggerBackendStream() {
  try {
    await axios.post('/api/simulate/stream', {
      num_wafers: params.num_wafers || results.value?.num_wafers || 6,
      steps: params.steps || results.value?.steps || 3
    })
    playState.message = 'Backend live stream started (watch Controls / global WS)'
  } catch (e) {
    playState.message = 'Stream trigger failed (backend may be down)'
  }
}

function formatHistory(h) {
  if (!h) return ''
  if (Array.isArray(h) && h.length && typeof h[0] === 'object') {
    return h.map(x => `${x.step?.[0]||''}${x.duration||''}`).join(' → ')
  }
  if (Array.isArray(h)) return h.join(' → ')
  return String(h)
}

async function runSimulation(alsoUpdateParent = false) {
  running.value = true
  try {
    const res = await axios.post('/api/simulate', {
      num_wafers: params.num_wafers,
      steps: params.steps
    })
    results.value = res.data.result || res.data
    // emit to parent App for global metrics
    if (alsoUpdateParent) {
      // @ts-ignore
      const ev = { type: 'sim', result: results.value, fab_state: res.data.fab_state, message: 'Simulation complete' }
      // parent listens via v-slot or we can just dispatch
      window.dispatchEvent(new CustomEvent('fab-sim', { detail: ev }))
    }
    await nextTick()
    renderChart()
  } catch (e) {
    console.error(e)
    alert('Simulation request failed. Is the FastAPI backend running on :8000?')
  } finally {
    running.value = false
  }
}

function yieldColor(y) {
  // Simple green-yellow-red scale for yield 0.95-1.0
  const pct = Math.max(0, Math.min(1, (y - 0.95) / 0.05))
  if (pct > 0.8) return '#00ff9d'
  if (pct > 0.5) return '#ccff66'
  if (pct > 0.2) return '#ffcc00'
  return '#ff4d4f'
}

function renderChart() {
  if (!chartRef.value || !results.value?.wafers) return
  const ctx = chartRef.value.getContext('2d')
  if (chart) chart.destroy()

  const labels = results.value.wafers.map((w, i) => 'W' + String(w.id).padStart(2, '0'))
  const yields = results.value.wafers.map(w => +(w.yield * 100).toFixed(2))
  const colors = yields.map(y => y > 98.5 ? '#00ff9d' : y > 97 ? '#ffcc00' : '#ff4d4f')

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Yield %',
        data: yields,
        backgroundColor: colors,
        borderColor: '#1f2835',
        borderWidth: 1,
      }]
    },
    options: {
      responsive: false,
      scales: {
        y: { min: 95, max: 100, grid: { color: '#1f2835' }, ticks: { color: '#7f8ea3' } },
        x: { grid: { color: '#1f2835' }, ticks: { color: '#7f8ea3', maxRotation: 50 } }
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => c.raw + '%' } }
      }
    }
  })
}

onMounted(() => {
  // optional: auto-run a small demo sim on load for nice first view
  // runSimulation()
})
</script>