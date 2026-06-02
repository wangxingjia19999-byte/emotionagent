// ── 认证状态管理 (Pinia) ──────────────────────────
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // ── State ────────────────────────────────
  const accessToken = ref('')
  const refreshToken = ref('')
  const user = ref(null)
  const adminToken = ref('')
  const adminUser = ref(null)

  // ── Getters ──────────────────────────────
  const isLoggedIn = computed(() => !!accessToken.value)
  const isAdmin = computed(
    () =>
      ['admin', 'super_admin'].includes(user.value?.role) || !!adminToken.value
  )
  const isSuperAdmin = computed(() => adminUser.value?.role === 'super_admin')
  const displayName = computed(
    () => user.value?.nickname || user.value?.username || ''
  )
  const userAvatar = computed(() => user.value?.avatar || '')

  // ── Actions ──────────────────────────────
  function restoreSession() {
    accessToken.value = uni.getStorageSync('access_token') || ''
    refreshToken.value = uni.getStorageSync('refresh_token') || ''
    const userRaw = uni.getStorageSync('user')
    user.value = userRaw ? JSON.parse(userRaw) : null
    adminToken.value = uni.getStorageSync('admin_token') || ''
  }

  function setSession({ access_token, refresh_token, user: userData }) {
    accessToken.value = access_token
    refreshToken.value = refresh_token || ''
    user.value = userData
    uni.setStorageSync('access_token', access_token)
    uni.setStorageSync('refresh_token', refresh_token || '')
    uni.setStorageSync('user', JSON.stringify(userData))
  }

  function setAdminSession({ access_token, refresh_token, admin }) {
    adminToken.value = access_token
    adminUser.value = admin
    uni.setStorageSync('admin_token', access_token)
    if (refresh_token) {
      uni.setStorageSync('admin_refresh_token', refresh_token)
    }
    uni.setStorageSync('admin_user', JSON.stringify(admin))
  }

  function clearSession() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    uni.removeStorageSync('access_token')
    uni.removeStorageSync('refresh_token')
    uni.removeStorageSync('user')
  }

  function clearAdminSession() {
    adminToken.value = ''
    adminUser.value = null
    uni.removeStorageSync('admin_token')
    uni.removeStorageSync('admin_refresh_token')
    uni.removeStorageSync('admin_user')
  }

  function clearAllSessions() {
    clearSession()
    clearAdminSession()
  }

  function updateUser(userData) {
    user.value = { ...user.value, ...userData }
    uni.setStorageSync('user', JSON.stringify(user.value))
  }

  function logout() {
    clearSession()
    uni.reLaunch({ url: '/pages/auth/login' })
  }

  return {
    accessToken,
    refreshToken,
    user,
    adminToken,
    adminUser,
    isLoggedIn,
    isAdmin,
    isSuperAdmin,
    displayName,
    userAvatar,
    restoreSession,
    setSession,
    setAdminSession,
    clearSession,
    clearAdminSession,
    clearAllSessions,
    updateUser,
    logout,
  }
})
