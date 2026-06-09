<template>
  <view class="page-container auth-page">
    <view class="auth-header">
      <text class="register-title">创建账号</text>
      <text class="register-subtitle">开始你的情绪陪伴之旅</text>
    </view>

    <view class="auth-form card-glass">
      <!-- 邮箱 -->
      <view class="form-item">
        <text class="form-label">邮箱</text>
        <input
          class="form-input"
          v-model="form.email"
          placeholder="请输入邮箱地址"
          placeholder-class="input-placeholder"
          type="text"
        />
      </view>

      <!-- 验证码 -->
      <view class="form-item">
        <text class="form-label">验证码</text>
        <view class="verify-row">
          <input
            class="form-input verify-input"
            v-model="form.verificationCode"
            placeholder="6位验证码"
            placeholder-class="input-placeholder"
            maxlength="6"
            type="text"
          />
          <button
            class="btn-ghost verify-btn"
            :disabled="countdown > 0"
            @tap="handleSendCode"
          >
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </view>
      </view>

      <!-- 密码 -->
      <view class="form-item">
        <text class="form-label">密码</text>
        <input
          class="form-input"
          v-model="form.password"
          placeholder="至少8位，包含字母和数字"
          placeholder-class="input-placeholder"
          type="password"
        />
      </view>

      <!-- 昵称（可选） -->
      <view class="form-item">
        <text class="form-label">昵称（选填）</text>
        <input
          class="form-input"
          v-model="form.nickname"
          placeholder="给自己起个名字吧"
          placeholder-class="input-placeholder"
          type="text"
          maxlength="20"
        />
      </view>

      <button
        class="btn-primary btn-full"
        :loading="loading"
        :disabled="loading"
        @tap="handleRegister"
      >
        {{ loading ? '注册中...' : '注 册' }}
      </button>

      <view class="form-footer">
        <text class="link-text" @tap="goLogin">已有账号？去登录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { register, sendVerifyCode } from '@/api/auth'
import { isValidEmail, isValidPassword, isValidVerificationCode } from '@/utils/validate'

const authStore = useAuthStore()
const loading = ref(false)
const countdown = ref(0)
let timer = null

const form = reactive({
  email: '',
  verificationCode: '',
  password: '',
  nickname: '',
})

async function handleSendCode() {
  if (!isValidEmail(form.email)) {
    uni.showToast({ title: '请输入有效的邮箱地址', icon: 'none' })
    return
  }
  try {
    await sendVerifyCode(form.email)
    uni.showToast({ title: '验证码已发送', icon: 'success' })
    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
        timer = null
      }
    }, 1000)
  } catch {
    // 错误已在 request.js 中处理
  }
}

async function handleRegister() {
  if (!isValidEmail(form.email)) {
    uni.showToast({ title: '请输入有效的邮箱地址', icon: 'none' })
    return
  }
  if (!isValidVerificationCode(form.verificationCode)) {
    uni.showToast({ title: '请输入6位验证码', icon: 'none' })
    return
  }
  if (!isValidPassword(form.password)) {
    uni.showToast({ title: '密码至少8位，需包含字母和数字', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res = await register({
      email: form.email.trim(),
      verification_code: form.verificationCode,
      password: form.password,
      nickname: form.nickname.trim() || undefined,
    })
    uni.showToast({ title: '注册成功，请登录', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 800)
  } catch {
    // 错误已在 request.js 中处理
  } finally {
    loading.value = false
  }
}

function goLogin() {
  uni.navigateBack()
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 80rpx;
  background: linear-gradient(180deg, #f0edff 0%, $bg-page 40%);
}

.auth-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 48rpx;
}

.register-title {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 8rpx;
}

.register-subtitle {
  font-size: 26rpx;
  color: $text-muted;
}

.auth-form {
  width: 640rpx;
}

.form-item {
  margin-bottom: 28rpx;
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

.verify-row {
  display: flex;
  gap: 16rpx;
}

.verify-input {
  flex: 1;
}

.verify-btn {
  width: 200rpx;
  height: 88rpx;
  border-radius: $radius-lg;
  font-size: 26rpx;
  flex-shrink: 0;
  white-space: nowrap;
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
