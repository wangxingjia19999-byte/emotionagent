import { createRouter, createWebHistory } from 'vue-router'

const Layout = () => import('../components/layout/Layout.vue')
const AdminLayout = () => import('../components/layout/AdminLayout.vue')
const Login = () => import('../views/Login.vue')
const AdminLogin = () => import('../views/AdminLogin.vue')
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
const AgentConfig = () => import('../views/AgentConfig.vue')
const DailyCheck = () => import('../views/DailyCheck.vue')
const Shop = () => import('../views/Shop.vue')
const ShopProduct = () => import('../views/ShopProduct.vue')
const ShopCart = () => import('../views/ShopCart.vue')
const ShopOrders = () => import('../views/ShopOrders.vue')

// Admin views
const AdminDashboard = () => import('../views/admin/AdminDashboard.vue')
const AdminProducts = () => import('../views/admin/AdminProducts.vue')
const AdminCategories = () => import('../views/admin/AdminCategories.vue')
const AdminOrders = () => import('../views/admin/AdminOrders.vue')
const AdminUsers = () => import('../views/admin/AdminUsers.vue')
const AdminQuestionnaires = () => import('../views/admin/AdminQuestionnaires.vue')
const AdminEmotionLogs = () => import('../views/admin/AdminEmotionLogs.vue')
const AdminPosts = () => import('../views/admin/AdminPosts.vue')

function checkAdminRole() {
  try {
    const raw = localStorage.getItem('user')
    if (!raw) return false
    const user = JSON.parse(raw)
    return ['admin', 'super_admin'].includes(user.role)
  } catch {
    return false
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/home' },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/admin/login', component: AdminLogin },
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
        { path: 'agent-config', component: AgentConfig },
        { path: 'daily-check', component: DailyCheck },
        { path: 'shop', component: Shop },
        { path: 'shop/:id', component: ShopProduct, props: true },
        { path: 'shop/cart', component: ShopCart },
        { path: 'shop/orders', component: ShopOrders },
      ],
    },
    {
      path: '/admin',
      component: AdminLayout,
      children: [
        { path: '', component: AdminDashboard },
        { path: 'products', component: AdminProducts },
        { path: 'categories', component: AdminCategories },
        { path: 'orders', component: AdminOrders },
        { path: 'users', component: AdminUsers },
        { path: 'questionnaires', component: AdminQuestionnaires },
        { path: 'emotion-logs', component: AdminEmotionLogs },
        { path: 'posts', component: AdminPosts },
      ],
    },
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const publicRoutes = ['/login', '/register', '/admin/login']

  // 未登录只能访问公开页面
  if (!token && !publicRoutes.includes(to.path)) {
    if (to.path.startsWith('/admin')) {
      next('/admin/login')
    } else {
      next('/login')
    }
    return
  }

  // 已登录用户访问公开页面时重定向
  if (token && publicRoutes.includes(to.path)) {
    if (to.path === '/admin/login') {
      next(checkAdminRole() ? '/admin' : '/home')
    } else {
      next('/home')
    }
    return
  }

  // 管理后台路由需要管理员角色
  if (to.path.startsWith('/admin') && to.path !== '/admin/login' && !checkAdminRole()) {
    next('/home')
    return
  }

  next()
})

export default router
