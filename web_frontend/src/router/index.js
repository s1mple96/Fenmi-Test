import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import PassengerApply from '../views/PassengerApply.vue'
import TruckApply from '../views/TruckApply.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页'
    }
  },
  {
    path: '/passenger',
    name: 'PassengerApply',
    component: PassengerApply,
    meta: {
      title: '客车申办'
    }
  },
  {
    path: '/truck',
    name: 'TruckApply',
    component: TruckApply,
    meta: {
      title: '货车申办'
    }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - ETC申办系统` : 'ETC申办系统'
  next()
})

export default router 