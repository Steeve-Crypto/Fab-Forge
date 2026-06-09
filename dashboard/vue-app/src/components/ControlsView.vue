<template>
  <div>
    <h2>Real-time Controls (MQTT)</h2>
    <button @click="sendCommand">Send Etch Command</button>
    <div id="logs"></div>
  </div>
</template>

<script setup>
import axios from 'axios'

async function sendCommand() {
  await axios.post('/api/mqtt', { topic: 'fab/command/etch', message: 'START' })
}
</script>