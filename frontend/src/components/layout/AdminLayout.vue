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
          <span class="admin-sidebar__role">{{ adminUser?.role === 'super_admin' ? '超级管理员' : '管理员' }}</span>
        </div>
        <button class="admin-sidebar__btn" @click="openChangePwd">🔑 修改密码</button>
        <button class="admin-sidebar__btn" @click="handleLogout">🚪 退出登录</button>
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
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminLogout, adminChangePassword } from '@/api/auth'

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
      { path: '/admin/stats', label: '数据统计', icon: '◈' },
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
      { path: '/admin/admins', label: '管理员管理', icon: '⚙' },
    ],
  },
  {
    label: '安全与审核',
    items: [
      { path: '/admin/crisis-alerts', label: '危机预警', icon: '⚠' },
      { path: '/admin/posts', label: '帖子管理', icon: '▣' },
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
    label: 'AI 管理',
    items: [
      { path: '/admin/agent-config', label: 'Agent 配置', icon: '🤖' },
    ],
  },
  {
    label: '系统',
    items: [
      { path: '/admin/audit-logs', label: '审计日志', icon: '◷' },
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
  '/admin/admins': '管理员管理',
  '/admin/crisis-alerts': '危机预警',
  '/admin/audit-logs': '审计日志',
  '/admin/stats': '数据统计',
  '/admin/agent-config': 'Agent 配置',
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

async function handleLogout() {
  try {
    await adminLogout()
  } catch { /* ignore if fails */ }
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  router.replace('/admin/login')
  ElMessage.success('已退出登录')
}

async function openChangePwd() {
  try {
    const { value: formValues } = await ElMessageBox.prompt('请输入新密码（至少8位）', '修改密码', {
      confirmButtonText: '确认修改',
      cancelButtonText: '取消',
      inputType: 'password',
      inputValidator: (val) => {
        if (!val || val.length < 8) return '密码长度不能少于8位'
        return true
      },
      beforeClose: async (action, instance, done) => {
        if (action === 'confirm') {
          const newPassword = instance.inputValue
          // 获取旧密码
          try {
            const { value: oldPwd } = await ElMessageBox.prompt('请先输入当前密码', '验证身份', {
              confirmButtonText: '确认',
              cancelButtonText: '取消',
              inputType: 'password',
            })
            if (!oldPwd) { done(); return }
            try {
              await adminChangePassword({ old_password: oldPwd, new_password: newPassword })
              ElMessage.success('密码已修改，请重新登录')
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              localStorage.removeItem('user')
              router.replace('/admin/login')
            } catch (e) {
              ElMessage.error(e?.response?.data?.detail || '修改失败')
            }
          } catch { /* cancelled */ }
        }
        done()
      },
    })
  } catch { /* cancelled */ }
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
  margin-bottom: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.admin-sidebar__role {
  font-size: 11px;
  color: #5a6a8a;
}

.admin-sidebar__btn {
  width: 100%;
  padding: 8px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  color: #8892b0;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 6px;
}

.admin-sidebar__btn:hover {
  background: rgba(255,255,255,0.12);
  color: #ccd6f6;
}

.admin-sidebar__back {
  width: 100%;
  padding: 8px;
  background: rgba(100, 255, 218, 0.08);
  border: 1px solid rgba(100, 255, 218, 0.2);
  border-radius: 6px;
  color: #64ffda;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.admin-sidebar__back:hover {
  background: rgba(100, 255, 218, 0.16);
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
