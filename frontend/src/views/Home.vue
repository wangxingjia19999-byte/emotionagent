<template>
  <div class="home-page">
    <div class="floating-orb floating-orb--one soft-pulse"></div>
    <div class="floating-orb floating-orb--two soft-pulse"></div>
    <div class="floating-orb floating-orb--three soft-pulse"></div>

    <div class="home-shell">
      <header class="home-navbar fade-in-down">
        <div class="home-brand">
          <span class="brand-dot"></span>
          <span>心语陪伴</span>
        </div>

        <div class="home-userbar">
          <div class="home-userbar__meta">
            <span class="user-label">当前用户</span>
            <span class="user-name">{{ user.nickname || user.username || '未命名用户' }}</span>
          </div>

          <el-button class="ghost-btn" text @click="logout">退出登录</el-button>
        </div>
      </header>

      <main class="home-content fade-in">
        <section class="home-hero-card card-enter" style="animation-delay: 0.08s;">
          <div class="home-hero-copy">
            <span class="eyebrow-pill">Welcome back</span>
            <h1>欢迎来到心语陪伴</h1>
            <p>登录成功，这里将成为你的情绪陪伴空间。</p>
          </div>

          <div class="welcome-stats">
            <article class="welcome-stat stagger-item" style="animation-delay: 0.12s;">
              <span class="welcome-stat__label">用户名</span>
              <strong>{{ user.username || '-' }}</strong>
            </article>
            <article class="welcome-stat stagger-item" style="animation-delay: 0.18s;">
              <span class="welcome-stat__label">昵称</span>
              <strong>{{ user.nickname || '-' }}</strong>
            </article>
            <article class="welcome-stat stagger-item" style="animation-delay: 0.24s;">
              <span class="welcome-stat__label">邮箱</span>
              <strong>{{ user.email || '-' }}</strong>
            </article>
          </div>
        </section>

        <section class="feature-grid">
          <article class="feature-card feature-card--primary card-enter" style="animation-delay: 0.16s;">
            <div class="feature-card__icon feature-card__icon--lavender feature-card__icon--float"></div>
            <h2>AI 情绪陪伴</h2>
            <p>有些话不方便说出口，可以先和 AI 慢慢聊聊。</p>
            <span class="feature-card__tag">即将开放</span>
          </article>

          <article class="feature-card feature-card--secondary card-enter" style="animation-delay: 0.24s;">
            <div class="feature-card__icon feature-card__icon--blue feature-card__icon--float"></div>
            <h2>好友聊天</h2>
            <p>和熟悉的人聊一聊，也许会轻松一点。</p>
            <span class="feature-card__tag">即将开放</span>
          </article>

          <article class="feature-card feature-card--secondary card-enter" style="animation-delay: 0.32s;">
            <div class="feature-card__icon feature-card__icon--pink feature-card__icon--float"></div>
            <h2>社区广场</h2>
            <p>看看别人的故事，也分享你的片刻心情。</p>
            <span class="feature-card__tag">即将开放</span>
          </article>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { getProfile } from '../api/user'

const router = useRouter()
const user = reactive({ username: '', nickname: '' })

onMounted(() => {
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    Object.assign(user, JSON.parse(savedUser))
  }

  getProfile().then((res) => {
    Object.assign(user, res.data)
    localStorage.setItem('user', JSON.stringify(res.data))
  })
})

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding: 24px;
  display: flex;
  justify-content: center;
  animation: fadeIn 0.72s var(--ease-out) both;
}

.home-shell {
  width: min(1360px, 100%);
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding: 8px 0 24px;
}

.home-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.64);
  border: 1px solid rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  box-shadow: 0 12px 36px rgba(111, 123, 211, 0.1);
  animation: fadeInDown 0.72s var(--ease-out) both;
}

.home-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: 0.02em;
}

.home-userbar {
  display: inline-flex;
  align-items: center;
  gap: 18px;
}

.home-userbar__meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.user-label {
  font-size: 12px;
  color: var(--text-muted);
}

.user-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
}

.ghost-btn {
  border-radius: 999px;
  padding: 10px 16px;
  color: var(--text-primary);
  background: rgba(124, 111, 246, 0.08);
  border: 1px solid rgba(124, 111, 246, 0.12);
  transition: transform 0.24s var(--ease-out), box-shadow 0.24s var(--ease-out), background 0.24s var(--ease-out), color 0.24s var(--ease-out);
}

.ghost-btn:hover {
  transform: translateY(-1px);
  background: rgba(124, 111, 246, 0.12);
  box-shadow: 0 10px 24px rgba(124, 111, 246, 0.1);
  color: var(--primary);
}

.home-content {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 22px;
}

.home-hero-card {
  padding: 32px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(18px);
  box-shadow: 0 22px 60px rgba(111, 123, 211, 0.14);
  animation: fadeInUp 0.74s var(--ease-out) both;
}

.home-hero-copy h1 {
  margin: 12px 0 10px;
  font-size: clamp(34px, 3.8vw, 54px);
  line-height: 1.08;
  letter-spacing: -0.03em;
  color: var(--text-primary);
}

.home-hero-copy p {
  margin: 0;
  font-size: 16px;
  line-height: 1.9;
  color: var(--text-secondary);
}

.welcome-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 28px;
}

.welcome-stat {
  padding: 18px 18px 16px;
  border-radius: 22px;
  background: rgba(247, 249, 255, 0.88);
  border: 1px solid rgba(124, 111, 246, 0.08);
  transition: transform 0.25s var(--ease-out), box-shadow 0.25s var(--ease-out), border-color 0.25s var(--ease-out);
}

.welcome-stat:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 34px rgba(124, 111, 246, 0.1);
  border-color: rgba(124, 111, 246, 0.16);
}

.welcome-stat__label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.welcome-stat strong {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  word-break: break-word;
}

.feature-grid {
  display: grid;
  gap: 16px;
}

.feature-card {
  position: relative;
  padding: 24px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(16px);
  box-shadow: 0 18px 44px rgba(111, 123, 211, 0.11);
  transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease-out), border-color 0.28s var(--ease-out);
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 26px 58px rgba(111, 123, 211, 0.18);
  border-color: rgba(124, 111, 246, 0.18);
}

.feature-card h2 {
  margin: 16px 0 8px;
  font-size: 20px;
  color: var(--text-primary);
}

.feature-card p {
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}

.feature-card__icon {
  width: 48px;
  height: 48px;
  border-radius: 18px;
  transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease-out);
}

.feature-card:hover .feature-card__icon {
  transform: scale(1.08);
}

.feature-card__icon--lavender {
  background: linear-gradient(135deg, rgba(124, 111, 246, 0.2), rgba(139, 124, 246, 0.32));
}

.feature-card__icon--blue {
  background: linear-gradient(135deg, rgba(108, 140, 255, 0.18), rgba(184, 198, 255, 0.34));
}

.feature-card__icon--pink {
  background: linear-gradient(135deg, rgba(255, 184, 210, 0.18), rgba(255, 230, 241, 0.4));
}

.feature-card__tag {
  display: inline-flex;
  margin-top: 16px;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  color: var(--primary);
  background: rgba(124, 111, 246, 0.1);
}

.feature-grid .feature-card:nth-child(1) {
  animation-delay: 0.18s;
}

.feature-grid .feature-card:nth-child(2) {
  animation-delay: 0.26s;
}

.feature-grid .feature-card:nth-child(3) {
  animation-delay: 0.34s;
}

.feature-card__icon--float {
  animation: floatBlob 12s ease-in-out infinite;
}

@media (max-width: 1024px) {
  .home-content {
    grid-template-columns: 1fr;
  }

  .welcome-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .home-page {
    padding: 14px;
  }

  .home-navbar {
    padding: 16px 18px;
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }

  .home-userbar {
    width: 100%;
    justify-content: space-between;
  }

  .home-userbar__meta {
    align-items: flex-start;
  }

  .home-hero-card,
  .feature-card {
    padding: 20px;
  }

  .floating-orb--one,
  .floating-orb--two,
  .floating-orb--three {
    opacity: 0.45;
    filter: blur(28px);
  }
}
</style>
