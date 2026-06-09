<template>
  <div id="app">
    <header>
      <h1>FabForge - Terafab Digital Twin Dashboard</h1>
      <nav>
        <router-link to="/">Simulation</router-link> |
        <router-link to="/controls">Controls (PLC/State Machines)</router-link> |
        <router-link to="/optimization">RL Optimization (PPO)</router-link> |
        <router-link to="/predictive">Predictive Maintenance</router-link>
      </nav>
    </header>
    <router-view></router-view>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
}
</style>