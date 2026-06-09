<template>
  <div class="pm-view">
    <h1>Predictive Maintenance</h1>
    <div v-for="tool in tools" :key="tool.id" class="tool-card">
      <h3>{{ tool.name }}</h3>
      <canvas :id="'chart-' + tool.id"></canvas>
      <div v-if="tool.alert" class="alert">⚠️ HIGH FAILURE RISK!</div>
      <button @click="predict(tool)">Predict</button>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  data() {
    return { tools: [] };
  },
  mounted() {
    this.fetchTools();
    // WebSocket for live alerts
  },
  methods: {
    async fetchTools() {
      // Fetch from FastAPI
      this.tools = [{id:1, name:'Litho', alert:false}];
    },
    predict(tool) {
      // Call API, update charts
      console.log('Predicting for', tool);
      // Simulate chart update
    }
  }
};
</script>
<style>
.alert { color: red; font-weight: bold; }
</style>
