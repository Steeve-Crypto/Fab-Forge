<template>
  <div>
    <h1>FabForge RL Optimization</h1>
    <button @click="connectWebSocket">Live MQTT WebSocket</button>
    <canvas id="rlChart" width="400" height="200"></canvas>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import Chart from 'chart.js/auto';

let chart;
onMounted(() => {
  const ctx = document.getElementById('rlChart');
  chart = new Chart(ctx, {
    type: 'line',
    data: { labels: ['Episode 1', 'Episode 2'], datasets: [{ label: 'Throughput', data: [65, 82] }] }
  });
});

function connectWebSocket() {
  const socket = new WebSocket('ws://localhost:8000/ws/mqtt');
  socket.onmessage = (e) => console.log('Live MQTT:', e.data);
}
</script>
