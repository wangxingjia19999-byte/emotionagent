<template>
  <view class="page-container auth-page">
    <!-- Logo 区域 -->
    <view class="auth-header">
      <view class="logo-circle">
        <text class="logo-icon">💜</text>
      </view>
      <text class="app-name">心语陪伴</text>
      <text class="app-slogan">让情绪被看见，让陪伴更靠近</text>
    </view>

    <!-- 登录表单 -->
    <view class="auth-form card-glass">
      <view class="form-item">
        <text class="form-label">账号 / 邮箱</text>
        <input
          class="form-input"
          v-model="form.account"
          placeholder="请输入账号或邮箱"
          placeholder-class="input-placeholder"
          type="text"
        />
      </view>

      <view class="form-item">
        <text class="form-label">密码</text>
        <input
          class="form-input"
          v-model="form.password"
          placeholder="请输入密码"
          placeholder-class="input-placeholder"
          type="password"
        />
      </view>

      <button
        class="btn-primary btn-full"
        :loading="loading"
        :disabled="loading"
        @tap="handleLogin"
      >
        {{ loading ? '登录中...' : '登 录' }}
      </button>

      <view class="form-footer">
        <text class="link-text" @tap="goRegister">没有账号？去注册</text>
      </view>
    </view>

    <!-- 管理员入口 -->
    <view class="admin-entry">
      <text class="link-text" @tap="goAdminLogin">管理后台登录 →</text>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api/auth'

const authStore = useAuthStore()
const loading = ref(false)
const form = reactive({
  account: '',
  password: '',
})

async function handleLogin() {
  if (!form.account.trim()) {
    uni.showToast({ title: '请输入账号或邮箱', icon: 'none' })
    return
  }
  if (!form.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res = await login({
      account: form.account.trim(),
      password: form.password,
      role: 'user',
    })
    const data = res.data || res
    authStore.setSession({
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      user: data.user,
    })
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/tabbar/home/index' })
    }, 500)
  } catch {
    // 错误已在 request.js 中处理
  } finally {
    loading.value = false
  }
}

function goRegister() {
  uni.navigateTo({ url: '/pages/auth/register' })
}

function goAdminLogin() {
  uni.navigateTo({ url: '/pages/auth/admin-login' })
}
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 120rpx;
  background: linear-gradient(180deg, #f0edff 0%, $bg-page 40%);
}

.auth-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 64rpx;
}

.logo-circle {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: $primary-gradient;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(124, 111, 246, 0.3);
}

.logo-icon {
  font-size: 56rpx;
}

.app-name {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 8rpx;
}

.app-slogan {
  font-size: 26rpx;
  color: $text-muted;
}

.auth-form {
  width: 640rpx;
}

.form-item {
  margin-bottom: 32rpx;
}

.form-label {
  font-size: 28rpx;
  color: $text-secondary;
  margin-bottom: 12rpx;
  display: block;
}

.form-input {
  width: 100%;
  height: 88rpx;
  background: $bg-page;
  border-radius: $radius-lg;
  padding: 0 24rpx;
  font-size: 30rpx;
  color: $text-primary;
}

.input-placeholder {
  color: $text-placeholder;
}

.btn-full {
  width: 100%;
  height: 88rpx;
  border-radius: $radius-lg;
  font-size: 32rpx;
  font-weight: 600;
  margin-top: 16rpx;
}

.form-footer {
  display: flex;
  justify-content: center;
  margin-top: 32rpx;
}

.link-text {
  font-size: 26rpx;
  color: $primary-color;
}

.admin-entry {
  margin-top: 48rpx;
}
</style>
