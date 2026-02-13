import { createRouter, createWebHistory } from 'vue-router'
import VideoView from '../views/VideoView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'

const routes = [
  { path: '/', component: VideoView },
  { path: '/analytics', component: AnalyticsView }
]

export default createRouter({
  history: createWebHistory(),
  routes
})