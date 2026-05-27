<template>
  <div class="auth-page auth-page--login">
    <div class="floating-orb floating-orb--one soft-pulse"></div>
    <div class="floating-orb floating-orb--two soft-pulse"></div>
    <div class="floating-orb floating-orb--three soft-pulse"></div>

    <section class="auth-shell">
      <aside class="auth-hero auth-hero--login fade-in-left">
        <div class="brand-mark">
          <span class="brand-dot"></span>
          <span>心语陪伴</span>
        </div>

        <div class="hero-copy fade-in-left" style="animation-delay: 0.08s;">
          <p class="eyebrow-pill">情绪陪伴与社交互助平台</p>
          <h1>把说不出口的情绪，轻轻放在这里</h1>
          <p class="hero-description">今天也辛苦了。这里是一个温柔的情绪空间，你可以慢慢说，不用急着变好。</p>
        </div>

        <div class="hero-highlights">
          <article class="highlight-card stagger-item" style="animation-delay: 0.16s;">
            <span class="highlight-icon highlight-icon--lavender"></span>
            <div>
              <h3>情绪被看见</h3>
              <p>每一次表达都值得被认真对待。</p>
            </div>
          </article>

          <article class="highlight-card stagger-item" style="animation-delay: 0.24s;">
            <span class="highlight-icon highlight-icon--blue"></span>
            <div>
              <h3>表达被接住</h3>
              <p>不用组织得很完美，也能被温柔理解。</p>
            </div>
          </article>

          <article class="highlight-card stagger-item" style="animation-delay: 0.32s;">
            <span class="highlight-icon highlight-icon--pink"></span>
            <div>
              <h3>陪伴更轻松</h3>
              <p>让情绪陪伴变得自然、轻盈、有温度。</p>
            </div>
          </article>
        </div>

        <p class="hero-footnote fade-in-left" style="animation-delay: 0.4s;">有些话不必一次说完，在这里可以慢慢来。</p>
      </aside>

      <section class="auth-panel">
        <div class="auth-card auth-card--login fade-in-right card-enter">
          <div class="auth-card__header">
            <span class="section-badge">登录</span>
            <h2>欢迎回来</h2>
            <p>登录后继续你的情绪陪伴空间</p>
          </div>

          <div class="mode-switcher" aria-label="登录入口切换">
            <button
              v-for="item in loginModes"
              :key="item.value"
              type="button"
              class="mode-chip"
              :class="{ active: currentRole === item.value }"
              @click="currentRole = item.value"
            >
              {{ item.label }}
            </button>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" class="auth-form" @submit.prevent>
            <el-form-item prop="username" class="stagger-item" style="animation-delay: 0.08s;">
              <el-input v-model="form.username" size="large" placeholder="用户名" clearable />
            </el-form-item>

            <el-form-item prop="password" class="stagger-item" style="animation-delay: 0.16s;">
              <el-input v-model="form.password" size="large" type="password" show-password placeholder="密码" />
            </el-form-item>

            <el-button class="primary-btn primary-btn--login" type="primary" size="large" :loading="loading" @click="onLogin">
              登录
            </el-button>

            <div class="auth-link auth-link--animated">
              还没有账号？<router-link to="/register">立即注册</router-link>
            </div>
          </el-form>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const currentRole = ref('user')

const loginModes = [
  { label: '用户登录入口', value: 'user' },
  { label: '管理员登录入口', value: 'admin' },
  { label: '系统管理员登录入口', value: 'super_admin' }
]

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const onLogin = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await login({
        username: form.username,
        password: form.password,
        role: currentRole.value
      })
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      ElMessage.success('登录成功')
      router.push('/home')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.72s var(--ease-out) both;
}

.auth-shell {
  width: min(1360px, 100%);
  min-height: calc(100vh - 56px);
  display: grid;
  grid-template-columns: 48% 52%;
  border-radius: 32px;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.auth-hero {
  padding: 56px 56px 44px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 28px;
  background: linear-gradient(150deg, rgba(247, 249, 255, 0.92), rgba(235, 240, 255, 0.88) 54%, rgba(255, 243, 249, 0.82));
  backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.72);
}

.auth-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 18% 14%, rgba(124, 111, 246, 0.12), transparent 24%),
    radial-gradient(circle at 78% 76%, rgba(255, 184, 210, 0.18), transparent 28%);
  pointer-events: none;
}

.auth-hero > * {
  position: relative;
  z-index: 1;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: 0.02em;
}

.brand-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  box-shadow: 0 0 20px rgba(124, 111, 246, 0.35);
}

.hero-copy {
  max-width: 560px;
  margin-top: 20px;
}

.eyebrow-pill {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(124, 111, 246, 0.12);
  color: var(--primary);
  font-size: 13px;
  letter-spacing: 0.08em;
  margin: 0 0 18px;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(40px, 4vw, 66px);
  line-height: 1.08;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.hero-description {
  margin: 18px 0 0;
  max-width: 520px;
  font-size: 16px;
  line-height: 2;
  color: var(--text-secondary);
}

.hero-highlights {
  display: grid;
  gap: 14px;
  max-width: 420px;
}

.highlight-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(124, 111, 246, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease-out), border-color 0.28s var(--ease-out);
}

.highlight-card:hover {
  transform: translateY(-3px);
  border-color: rgba(124, 111, 246, 0.18);
  box-shadow: 0 16px 30px rgba(124, 111, 246, 0.08);
}

.highlight-card h3 {
  margin: 0 0 4px;
  font-size: 15px;
  color: var(--text-primary);
}

.highlight-card p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.highlight-icon {
  width: 42px;
  height: 42px;
  border-radius: 16px;
  flex: 0 0 42px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
}

.highlight-icon--lavender {
  background: linear-gradient(135deg, rgba(124, 111, 246, 0.18), rgba(139, 124, 246, 0.3));
}

.highlight-icon--blue {
  background: linear-gradient(135deg, rgba(108, 140, 255, 0.18), rgba(184, 198, 255, 0.32));
}

.highlight-icon--pink {
  background: linear-gradient(135deg, rgba(255, 184, 210, 0.22), rgba(255, 210, 230, 0.34));
}

.hero-footnote {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  background: linear-gradient(180deg, rgba(250, 251, 255, 0.72), rgba(247, 248, 255, 0.82));
}

.auth-card {
  width: min(460px, 100%);
  padding: 40px 40px 36px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 24px 64px rgba(111, 123, 211, 0.15);
  backdrop-filter: blur(18px);
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out), border-color 0.3s var(--ease-out);
}

.auth-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 30px 72px rgba(111, 123, 211, 0.18);
  border-color: rgba(124, 111, 246, 0.12);
}

.auth-card__header h2 {
  margin: 12px 0 6px;
  font-size: 30px;
  line-height: 1.15;
  color: var(--text-primary);
}

.auth-card__header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.8;
}

.section-badge {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(124, 111, 246, 0.1);
  color: var(--primary);
  font-size: 12px;
  letter-spacing: 0.06em;
}

.mode-switcher {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 22px 0 18px;
}

.mode-chip {
  appearance: none;
  border: 1px solid rgba(124, 111, 246, 0.12);
  background: rgba(255, 255, 255, 0.72);
  color: var(--text-secondary);
  border-radius: 999px;
  min-height: 42px;
  padding: 0 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.24s var(--ease-out);
}

.mode-chip:hover {
  transform: translateY(-1px);
  border-color: rgba(124, 111, 246, 0.28);
  color: var(--text-primary);
}

.mode-chip.active {
  background: linear-gradient(135deg, rgba(124, 111, 246, 0.14), rgba(255, 184, 210, 0.2));
  border-color: rgba(124, 111, 246, 0.34);
  color: var(--text-primary);
  box-shadow: 0 10px 24px rgba(124, 111, 246, 0.12);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.auth-form :deep(.el-form-item) {
  animation: staggerItem 0.62s var(--ease-out) both;
}

.auth-form :deep(.el-form-item:nth-child(1)) {
  animation-delay: 0.08s;
}

.auth-form :deep(.el-form-item:nth-child(2)) {
  animation-delay: 0.16s;
}

.primary-btn--login {
  background-size: 200% 200%;
  animation: flowGradient 10s ease infinite;
}

.primary-btn--login:hover {
  transform: translateY(-2px);
}

.auth-link--animated a {
  position: relative;
  display: inline-block;
}

.auth-link--animated a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -3px;
  width: 100%;
  height: 1px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 0.24s var(--ease-out);
}

.auth-link--animated a:hover::after {
  transform: scaleX(1);
}

.auth-link {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 2px;
}

.primary-btn--login {
  margin-top: 6px;
}

@media (max-width: 1180px) {
  .auth-shell {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .auth-hero {
    padding-bottom: 34px;
  }

  .auth-panel {
    padding-top: 0;
  }
}

@media (max-width: 640px) {
  .auth-page {
    padding: 16px;
  }

  .auth-hero,
  .auth-panel {
    padding-left: 20px;
    padding-right: 20px;
  }

  .auth-hero {
    padding-top: 24px;
  }

  .hero-copy h1 {
    font-size: 34px;
  }

  .auth-card {
    padding: 28px 22px 24px;
    width: min(100%, 460px);
  }

  .mode-switcher {
    grid-template-columns: 1fr;
  }

  .hero-highlights {
    max-width: none;
  }

  .auth-page {
    padding: 16px;
  }
}
</style>
