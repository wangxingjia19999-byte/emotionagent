import { createRouter, createWebHistory } from 'vue-router'

const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Home = () => import('../views/Home.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/home', component: Home }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path === '/home' && !token) {
    next('/login')
    return
  }
  if ((to.path === '/login' || to.path === '/register') && token) {
    next('/home')
    return
  }
  next()
})

export default router
