<template>
  <div>
    <h2>AI Optimization</h2>
    <button @click="runOptimization">Run Genetic Algorithm</button>
  </div>
</template>

<script setup>
import axios from 'axios'

async function runOptimization() {
  await axios.post('/api/optimize', { objective: 'yield' })
}
</script>