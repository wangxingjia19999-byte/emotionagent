<template>
  <view class="page-container auth-page">
    <view class="auth-header">
      <view class="logo-circle admin-logo">
        <text class="logo-icon">🛡️</text>
      </view>
      <text class="app-name">管理后台</text>
      <text class="app-slogan">心语陪伴 · 管理员登录</text>
    </view>

    <view class="auth-form card-glass">
      <view class="form-item">
        <text class="form-label">管理员账号</text>
        <input
          class="form-input"
          v-model="form.username"
          placeholder="请输入管理员账号"
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
        {{ loading ? '登录中...' : '管理员登录' }}
      </button>

      <view class="form-footer">
        <text class="link-text" @tap="goBack">返回用户登录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { adminLogin } from '@/api/auth'

const authStore = useAuthStore()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
})

async function handleLogin() {
  if (!form.username.trim()) {
    uni.showToast({ title: '请输入管理员账号', icon: 'none' })
    return
  }
  if (!form.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res = await adminLogin({
      username: form.username.trim(),
      password: form.password,
    })
    const data = res.data || res
    authStore.setAdminSession({
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      admin: data.admin,
    })
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.redirectTo({ url: '/pages/subpackages/admin/dashboard' })
    }, 500)
  } catch {
    // 错误已在 request.js 中处理
  } finally {
    loading.value = false
  }
}

function goBack() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 120rpx;
  background: linear-gradient(180deg, #e8e4ff 0%, $bg-page 40%);
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
  background: linear-gradient(135deg, #5b4fd9 0%, #7c6ff6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(91, 79, 217, 0.3);
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
</style>
