import { createRouter, createWebHistory } from 'vue-router'
import SimulationView from '../components/SimulationView.vue'
import ControlsView from '../components/ControlsView.vue'
import OptimizationView from '../components/OptimizationView.vue'
import PredictiveMaintenanceView from '../views/PredictiveMaintenanceView.vue'

const routes = [
  { path: '/', component: SimulationView },
  { path: '/controls', component: ControlsView },
  { path: '/optimization', component: OptimizationView },
  { path: '/predictive', component: PredictiveMaintenanceView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router