<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="admin-sidebar__brand">
        <span class="admin-sidebar__logo">⚙</span>
        <div>
          <div class="admin-sidebar__title">管理后台</div>
          <div class="admin-sidebar__subtitle">心语陪伴</div>
        </div>
      </div>

      <nav class="admin-nav">
        <div v-for="group in navGroups" :key="group.label" class="admin-nav__group">
          <div class="admin-nav__group-label">{{ group.label }}</div>
          <router-link
            v-for="item in group.items"
            :key="item.path"
            :to="item.path"
            class="admin-nav__item"
            :class="{ 'is-active': route.path === item.path || route.path.startsWith(item.path + '/') }"
          >
            <span class="admin-nav__icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </router-link>
        </div>
      </nav>

      <div class="admin-sidebar__footer">
        <div class="admin-sidebar__user">
          <span>{{ adminUser?.nickname || adminUser?.username || '管理员' }}</span>
        </div>
        <button class="admin-sidebar__back" @click="goBack">← 返回主站</button>
      </div>
    </aside>

    <div class="admin-main">
      <header class="admin-header">
        <h2 class="admin-header__title">{{ pageTitle }}</h2>
        <div class="admin-header__actions">
          <span class="admin-header__time">{{ nowStr }}</span>
        </div>
      </header>
      <div class="admin-content">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const nowStr = ref('')
let timer = null

const adminUser = ref(null)
try {
  const raw = localStorage.getItem('user')
  if (raw) adminUser.value = JSON.parse(raw)
} catch {}

const navGroups = [
  {
    label: '概览',
    items: [
      { path: '/admin', label: '仪表盘', icon: '▦' },
    ],
  },
  {
    label: '商城管理',
    items: [
      { path: '/admin/products', label: '商品管理', icon: '▤' },
      { path: '/admin/categories', label: '分类管理', icon: '☰' },
      { path: '/admin/orders', label: '订单管理', icon: '◈' },
    ],
  },
  {
    label: '用户管理',
    items: [
      { path: '/admin/users', label: '用户列表', icon: '▨' },
    ],
  },
  {
    label: '数据查看',
    items: [
      { path: '/admin/questionnaires', label: '问卷记录', icon: '◉' },
      { path: '/admin/emotion-logs', label: '情绪日志', icon: '♡' },
    ],
  },
  {
    label: '内容审核',
    items: [
      { path: '/admin/posts', label: '帖子管理', icon: '▣' },
    ],
  },
]

const pageTitleMap = {
  '/admin': '仪表盘',
  '/admin/products': '商品管理',
  '/admin/categories': '分类管理',
  '/admin/orders': '订单管理',
  '/admin/users': '用户列表',
  '/admin/questionnaires': '问卷记录',
  '/admin/emotion-logs': '情绪日志',
  '/admin/posts': '帖子管理',
}

const pageTitle = computed(() => {
  return pageTitleMap[route.path] || '管理后台'
})

function goBack() {
  router.push('/home')
}

function checkAdminRole() {
  if (adminUser.value && !['admin', 'super_admin'].includes(adminUser.value.role)) {
    ElMessage.warning('无权访问管理后台')
    router.replace('/admin/login')
  }
}

function tick() {
  const d = new Date()
  nowStr.value = d.toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  checkAdminRole()
  tick()
  timer = setInterval(tick, 1000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px 1fr;
  background: #f0f2f5;
}

.admin-sidebar {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  color: #ccc;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.admin-sidebar__brand {
  padding: 20px 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-sidebar__logo {
  font-size: 24px;
}

.admin-sidebar__title {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
}

.admin-sidebar__subtitle {
  font-size: 12px;
  color: #8892b0;
}

.admin-nav {
  flex: 1;
  padding: 12px 0;
}

.admin-nav__group {
  margin-bottom: 8px;
}

.admin-nav__group-label {
  padding: 8px 20px 4px;
  font-size: 11px;
  color: #5a6a8a;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.admin-nav__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  color: #8892b0;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.admin-nav__item:hover {
  color: #ccd6f6;
  background: rgba(255,255,255,0.05);
}

.admin-nav__item.is-active {
  color: #64ffda;
  background: rgba(100, 255, 218, 0.08);
  border-left-color: #64ffda;
}

.admin-nav__icon {
  font-size: 16px;
  width: 22px;
  text-align: center;
}

.admin-sidebar__footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.admin-sidebar__user {
  color: #ccd6f6;
  font-size: 13px;
  margin-bottom: 12px;
}

.admin-sidebar__back {
  width: 100%;
  padding: 8px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  color: #8892b0;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.admin-sidebar__back:hover {
  background: rgba(255,255,255,0.14);
  color: #ccd6f6;
}

.admin-main {
  min-width: 0;
}

.admin-header {
  background: #fff;
  padding: 16px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 10;
}

.admin-header__title {
  margin: 0;
  font-size: 18px;
  color: #1a1a2e;
}

.admin-header__time {
  font-size: 13px;
  color: #999;
}

.admin-content {
  padding: 24px;
}
</style>
