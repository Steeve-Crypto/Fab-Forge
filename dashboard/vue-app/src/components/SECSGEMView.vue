<template>
  <div>
    <div class="card" style="margin-bottom:16px">
      <h2>SECS/GEM Panel</h2>
      <div style="color:#7f8ea3;font-size:12px">
        SEMI E5 / E30 emulation • Host &lt;-&gt; Equipment messaging for Terafab MES integration
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <!-- Quick Actions -->
      <div class="card">
        <h3>Quick Commands</h3>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px">
          <button class="btn" @click="sendStream(1,1)">S1F1 AreYouThere</button>
          <button class="btn secondary" @click="sendStream(2,17)">S2F17 Date/Time Req</button>
          <button class="btn" @click="sendGEM('START', 42)">GEM START wafer 42</button>
          <button class="btn secondary" @click="sendGEM('STOP')">GEM STOP</button>
          <button class="btn secondary" @click="sendGEM('ABORT')">GEM ABORT</button>
        </div>

        <div style="border-top:1px solid #24313f;padding-top:12px">
          <div style="font-size:12px;color:#7f8ea3;margin-bottom:4px">Custom Stream / Function</div>
          <div style="display:flex;gap:6px;align-items:center;margin-bottom:8px">
            <input v-model.number="customS" class="input" style="width:70px" placeholder="S" />
            <input v-model.number="customF" class="input" style="width:70px" placeholder="F" />
            <input v-model="customData" class="input" style="flex:1" placeholder='{"wafer_id":7}' />
            <button class="btn" @click="sendCustomStream">Send SxFy</button>
          </div>

          <div style="font-size:12px;color:#7f8ea3;margin:8px 0 4px">GEM-style Host Command</div>
          <div style="display:flex;gap:6px">
            <input v-model="gemCmd" class="input" style="width:120px" placeholder="START" />
            <input v-model.number="gemWafer" class="input" style="width:80px" placeholder="wafer" />
            <button class="btn secondary" @click="sendGEM(gemCmd, gemWafer)">Send</button>
          </div>
        </div>
      </div>

      <!-- Status + Log -->
      <div class="card">
        <h3>Equipment Status &amp; Message Log</h3>
        <div style="margin-bottom:8px">
          Status: <span class="status-pill" :class="{ running: status==='PROCESSING' }">{{ status }}</span>
          &nbsp; Wafers processed: <b>{{ waferCount }}</b>
        </div>

        <div class="log" style="min-height:260px;max-height:320px" ref="logEl">
          <div v-for="(entry, idx) in log" :key="idx" style="margin-bottom:4px;font-size:12px">
            <span style="color:#5a6878">{{ new Date(entry.ts*1000).toLocaleTimeString() }}</span>
            <span v-if="entry.stream" style="color:#00d1ff"> {{ entry.stream }}</span>
            <span v-if="entry.gem_command" style="color:#00ff9d"> GEM {{ entry.gem_command.command }}</span>
            <span style="color:#a8b8cc"> {{ JSON.stringify(entry.data || entry.gem_command || entry) }}</span>
          </div>
          <div v-if="!log.length" style="color:#5a6878">No messages yet. Send a command above.</div>
        </div>
        <button class="btn secondary" style="margin-top:8px" @click="refreshLog">Refresh Log</button>
        <button class="btn secondary" style="margin-left:6px" @click="clearLocal">Clear view</button>
      </div>
    </div>

    <div class="card" style="margin-top:16px;font-size:12px;color:#7f8ea3">
      The emulator also participates in the global live event stream (visible in other views). 
      Real production systems would translate these S/F messages over HSMS-SS or SECS-I.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

const status = ref('IDLE')
const waferCount = ref(0)
const log = ref([])
const logEl = ref(null)

const customS = ref(1)
const customF = ref(1)
const customData = ref('{"wafer_id": 1}')

const gemCmd = ref('START')
const gemWafer = ref(7)

async function sendStream(s, f) {
  const data = { stream: s, function: f, data: { wafer_id: gemWafer.value } }
  await axios.post('/api/secsgem', data)
  await refreshLog()
}

async function sendGEM(cmd, wafer = null) {
  await axios.post('/api/secsgem', { command: cmd, wafer_id: wafer })
  await refreshLog()
}

async function sendCustomStream() {
  let payload = {}
  try { payload = JSON.parse(customData.value || '{}') } catch (_) {}
  await axios.post('/api/secsgem', {
    stream: customS.value,
    function: customF.value,
    data: payload
  })
  await refreshLog()
}

async function refreshLog() {
  try {
    const { data } = await axios.get('/api/secsgem/log')
    status.value = data.status || 'IDLE'
    waferCount.value = data.wafer_count || 0
    log.value = data.log || []
    await nextTick()
    if (logEl.value) logEl.value.scrollTop = logEl.value.scrollHeight
  } catch (e) {
    console.error(e)
  }
}

function clearLocal() {
  log.value = []
}

onMounted(() => {
  refreshLog()
  // Also listen for WS secsgem events if the global WS is open (lightweight)
  // The App already connects one; we just poll on action for simplicity.
})
</script>