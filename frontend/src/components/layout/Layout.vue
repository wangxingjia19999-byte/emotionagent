<template>
  <div class="app-layout">
    <div class="app-layout__background"></div>

    <Sidebar
      :active-route="route.path"
      :user="currentUser"
      @navigate="goTo"
      @logout="openLogoutDialog"
    />

    <div class="app-layout__content">
      <AppHeader
        :page-key="pageKey"
        :page-tag="pageMeta.tag"
        :title="pageMeta.title"
        :subtitle="pageMeta.subtitle"
        :user="currentUser"
        @shortcut="handleShortcut"
        @command="handleMenuCommand"
      />

      <main class="app-layout__main">
        <router-view v-slot="{ Component, route: childRoute }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="childRoute.fullPath" />
          </transition>
        </router-view>
      </main>
    </div>

    <LogoutDialog v-model="logoutVisible" @confirm="confirmLogout" />

    <!-- 管理员入口浮动按钮 -->
    <button
      v-if="isAdmin"
      class="admin-fab"
      title="管理后台"
      @click="router.push('/admin')"
    >⚙</button>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Collection, MagicStick, User, UserFilled } from '@element-plus/icons-vue'
import Sidebar from './Sidebar.vue'
import AppHeader from './AppHeader.vue'
import LogoutDialog from './LogoutDialog.vue'

const router = useRouter()
const route = useRoute()
const logoutVisible = ref(false)
const currentUser = ref(loadCurrentUser())

const isAdmin = computed(() => {
  const role = currentUser.value?.role
  return role === 'admin' || role === 'super_admin'
})

const pageKey = computed(() => {
  if (route.path.startsWith('/ai-chat')) return 'ai-chat'
  if (route.path.startsWith('/friends')) return 'friends'
  if (route.path.startsWith('/community') || route.path.startsWith('/publish-post')) return 'community'
  if (route.path.startsWith('/profile')) return 'profile'
  if (route.path.startsWith('/shop')) return 'shop'
  return 'home'
})

const pageMeta = computed(() => {
  const map = {
    home: { tag: '首页概览', title: '欢迎回来', subtitle: '今天也辛苦了，先用一眼就能看懂的方式看看整体状态。' },
    'ai-chat': { tag: 'AI 情绪陪伴', title: 'AI 情绪陪伴', subtitle: '把想说的话慢慢说出来，先被看见再去处理。' },
    friends: { tag: '好友聊天', title: '好友聊天', subtitle: '和熟悉的人聊聊，也许会轻松一点。' },
    community: { tag: '社区广场', title: '社区广场', subtitle: '看看别人的故事，也分享自己的片刻心情。' },
    profile: { tag: '个人中心', title: '个人中心', subtitle: '管理你的资料与账号安全，让它更像你自己。' },
    shop: { tag: '解压商城', title: '解压商城', subtitle: '挑一件喜欢的小物，给紧绷的生活一个温柔的拥抱。' }
  }
  return map[pageKey.value]
})

function loadCurrentUser() {
  const raw = localStorage.getItem('user')
  if (!raw) return { username: '', nickname: '', avatar: '', role: '' }
  try {
    return JSON.parse(raw)
  } catch {
    return { username: '', nickname: '', avatar: '', role: '' }
  }
}

function refreshCurrentUser() {
  currentUser.value = loadCurrentUser()
}

function goTo(path) {
  if (route.path !== path) {
    router.push(path)
  }
}

function openLogoutDialog() {
  logoutVisible.value = true
}

function confirmLogout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  router.replace('/login')
}

function handleShortcut(action, value) {
  if (action === 'logout') {
    openLogoutDialog()
    return
  }

  if (action === 'security') {
    router.push('/profile')
    return
  }

  if (action === 'publish') {
    router.push('/publish-post')
    return
  }

  if (action === 'new-chat') {
    router.push('/ai-chat')
    return
  }

  if (action === 'history') {
    router.push('/home')
    return
  }

  if (action === 'notifications') {
    ElMessage.info('暂无新的通知')
    return
  }

  if (action === 'search') {
    if (pageKey.value === 'community') {
      router.push({ path: '/community', query: value ? { q: value } : {} })
      return
    }
    ElMessage.info(value ? `正在搜索：${value}` : '请输入搜索内容')
  }
}

function handleMenuCommand(command) {
  if (command === 'home') {
    router.push('/home')
    return
  }

  if (command === 'profile') {
    router.push('/profile')
    return
  }

  if (command === 'logout') {
    openLogoutDialog()
  }
}

function onUserUpdated() {
  refreshCurrentUser()
}

watch(() => route.fullPath, refreshCurrentUser)

onMounted(() => {
  window.addEventListener('session:user-updated', onUserUpdated)
  window.addEventListener('storage', onUserUpdated)
  refreshCurrentUser()
})

onBeforeUnmount(() => {
  window.removeEventListener('session:user-updated', onUserUpdated)
  window.removeEventListener('storage', onUserUpdated)
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 18px;
  padding: 18px;
  background:
    radial-gradient(circle at 8% 6%, rgba(111, 132, 232, 0.08), transparent 18%),
    radial-gradient(circle at 92% 10%, rgba(109, 165, 204, 0.08), transparent 18%),
    linear-gradient(135deg, #f6f8fc 0%, #f8f6f2 50%, #eef3fb 100%);
}

.app-layout__background {
  display: none;
}

.app-layout__content {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.app-layout__main {
  min-width: 0;
}

@media (max-width: 1180px) {
  .app-layout {
    grid-template-columns: 1fr;
  }

  .app-sidebar {
    position: static;
  }
}

@media (max-width: 720px) {
  .app-layout {
    padding: 12px;
    gap: 12px;
  }
}

.admin-fab {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  color: #64ffda;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  z-index: 999;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.admin-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 24px rgba(0,0,0,0.35);
}
</style>