<template>
  <div>
    <h2>Wafer Simulation</h2>
    <button @click="runSimulation">Run C++ Simulation</button>
    <div v-if="results">
      <pre>{{ results }}</pre>
      <canvas id="yieldChart"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const results = ref(null)

async function runSimulation() {
  try {
    const res = await axios.post('/api/simulate', { num_wafers: 10 })
    results.value = res.data
    // Render chart with yield data
  } catch (e) {
    console.error(e)
  }
}
</script>