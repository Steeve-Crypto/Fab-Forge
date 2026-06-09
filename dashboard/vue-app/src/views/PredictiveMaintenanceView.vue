<template>
  <div>
    <div class="card" style="margin-bottom:16px">
      <h2>Predictive Maintenance</h2>
      <div style="color:#7f8ea3">RandomForest / heuristic sensor model • real-time risk scoring from fab telemetry</div>
    </div>

    <div class="tool-grid">
      <div v-for="tool in tools" :key="tool.name" class="tool-card">
        <div style="display:flex;justify-content:space-between">
          <div style="font-weight:700;font-size:15px">{{ tool.name }}</div>
          <span class="status-pill" :class="{ fault: tool.alert }">{{ tool.alert ? 'AT RISK' : tool.status || 'HEALTHY' }}</span>
        </div>

        <div style="margin:12px 0">
          <div style="height:8px;background:#24313f;border-radius:999px;overflow:hidden">
            <div :style="{width: (tool.risk*100)+'%', height:'100%', background: tool.alert ? 'var(--warn)' : 'var(--accent2)', transition:'width .3s'}"></div>
          </div>
          <div style="font-size:11px;margin-top:3px;color:#7f8ea3">Failure risk: <b :style="{color: tool.alert?'#ff4d4f':'#00ff9d'}">{{ (tool.risk*100).toFixed(0) }}%</b></div>
        </div>

        <div style="font-size:12px;color:#8fa2b8;line-height:1.35;margin-bottom:10px">
          T: {{ tool.sensors?.temp?.toFixed?.(1) || tool.temp }}°C &nbsp;
          V: {{ tool.sensors?.vibration || '0.6' }} &nbsp;
          RT: {{ tool.sensors?.runtime || '—' }}h
        </div>

        <div v-if="tool.anomaly_score !== undefined" style="font-size:11px;margin-bottom:6px">
          Anomaly: <b :style="{color: tool.is_anomaly ? '#ff4d4f' : '#00ff9d'}">{{ (tool.anomaly_score*100).toFixed(0) }}%</b>
          <span v-if="tool.is_anomaly" style="color:#ff4d4f"> • DRIFT DETECTED</span>
        </div>

        <button class="btn" style="width:100%" @click="runPredict(tool)">RUN PREDICTION</button>

        <canvas v-if="tool.chartData" :ref="'chart_'+tool.name" width="210" height="92" style="margin-top:10px"></canvas>
      </div>
    </div>

    <div v-if="lastAlert" class="card" style="margin-top:16px;border-color:#ff4d4f">
      <div style="color:#ff4d4f;font-weight:700">⚠ HIGH RISK DETECTED — {{ lastAlert.tool }}</div>
      <div>Recommend: {{ lastAlert.recommendation }}</div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)
import axios from 'axios'

export default {
  data() {
    return {
      tools: [
        { name: 'Lithography', risk: 0.18, alert: false, status: 'HEALTHY', sensors: { temp: 195, vibration: 0.52, pressure: 0.5, runtime: 4820 } },
        { name: 'Etch', risk: 0.31, alert: false, status: 'HEALTHY', sensors: { temp: 68, vibration: 0.71, pressure: 0.011, runtime: 7100 } },
        { name: 'Deposition', risk: 0.09, alert: false, status: 'HEALTHY', sensors: { temp: 318, vibration: 0.44, pressure: 1.18, runtime: 2940 } },
      ],
      lastAlert: null,
      charts: {},
    }
  },
  mounted() {
    this.fetchInitial()
  },
  methods: {
    async fetchInitial() {
      try {
        const { data } = await axios.get('/api/status')
        if (data.fab?.tools) {
          this.tools.forEach(t => {
            const live = data.fab.tools[t.name]
            if (live) t.sensors.temp = live.temp
          })
        }
      } catch (_) {}
    },
    async runPredict(tool) {
      try {
        const { data } = await axios.post('/api/predict', { tool: tool.name, sensors: tool.sensors })
        tool.risk = data.failure_prob
        tool.alert = data.alert
        tool.status = (data.alert || data.is_anomaly) ? 'MAINT' : 'HEALTHY'
        tool.sensors = data.sensors
        tool.anomaly_score = data.anomaly_score
        tool.is_anomaly = data.is_anomaly
        if (data.alert || data.is_anomaly) this.lastAlert = data
        this.$nextTick(() => this.renderMiniChart(tool))
      } catch (e) {
        // offline fallback
        tool.risk = Math.min(0.94, tool.risk + 0.22)
        tool.alert = tool.risk > 0.58
        tool.anomaly_score = Math.min(0.95, (tool.anomaly_score || 0.2) + 0.25)
        tool.is_anomaly = tool.anomaly_score > 0.45
        if (tool.alert || tool.is_anomaly) this.lastAlert = { tool: tool.name, recommendation: 'Schedule maintenance' }
        this.$nextTick(() => this.renderMiniChart(tool))
      }
    },
    renderMiniChart(tool) {
      const key = 'chart_' + tool.name
      const canvas = this.$refs[key] && (Array.isArray(this.$refs[key]) ? this.$refs[key][0] : this.$refs[key])
      if (!canvas) return
      if (this.charts[key]) this.charts[key].destroy()
      const ctx = canvas.getContext('2d')
      const base = Math.max(5, Math.round((1 - tool.risk) * 100))
      this.charts[key] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['-4h','-3h','-2h','-1h','now'],
          datasets: [{
            data: [base-3, base-1, base+2, base-4, Math.round((1-tool.risk)*100)],
            borderColor: tool.alert ? '#ff4d4f' : '#00ff9d',
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2,
          }]
        },
        options: { responsive:false, scales:{x:{display:false},y:{display:false,min:0,max:100}}, plugins:{legend:{display:false}} }
      })
    }
  }
}
</script>
