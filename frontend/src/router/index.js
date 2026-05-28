import { createRouter, createWebHistory } from 'vue-router'

const Layout = () => import('../components/layout/Layout.vue')
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Home = () => import('../views/Home.vue')
const Profile = () => import('../views/Profile.vue')
const UserProfile = () => import('../views/UserProfile.vue')
const AiChat = () => import('../views/AiChat.vue')
const Friends = () => import('../views/Friends.vue')
const Community = () => import('../views/Community.vue')
const PrivateChat = () => import('../views/PrivateChat.vue')
const PostDetail = () => import('../views/PostDetail.vue')
const PublishPost = () => import('../views/PublishPost.vue')
const Admin = () => import('../views/Admin.vue')
const AgentConfig = () => import('../views/AgentConfig.vue')
const DailyCheck = () => import('../views/DailyCheck.vue')
const Shop = () => import('../views/Shop.vue')
const ShopProduct = () => import('../views/ShopProduct.vue')
const ShopCart = () => import('../views/ShopCart.vue')
const ShopOrders = () => import('../views/ShopOrders.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/home' },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    {
      path: '/',
      component: Layout,
      children: [
        { path: 'home', component: Home },
        { path: 'profile', component: Profile },
        { path: 'users/:id', component: UserProfile, props: true },
        { path: 'ai-chat', component: AiChat },
        { path: 'friends', component: Friends },
        { path: 'community', component: Community },
        { path: 'private-chat', component: PrivateChat },
        { path: 'community/:id', component: PostDetail, props: true },
        { path: 'publish-post', component: PublishPost },
        { path: 'admin', component: Admin },
        { path: 'agent-config', component: AgentConfig },
        { path: 'daily-check', component: DailyCheck },
        { path: 'shop', component: Shop },
        { path: 'shop/:id', component: ShopProduct, props: true },
        { path: 'shop/cart', component: ShopCart },
        { path: 'shop/orders', component: ShopOrders }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const publicRoutes = ['/login', '/register']

  if (!token && !publicRoutes.includes(to.path)) {
    next('/login')
    return
  }

  if (token && publicRoutes.includes(to.path)) {
    next('/home')
    return
  }

  next()
})

export default router
