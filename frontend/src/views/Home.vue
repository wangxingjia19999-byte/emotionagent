<template>
  <div class="home-page">
    <main class="home-content">
      <section class="hero-grid">
        <div class="hero-card glass-card">
          <div class="hero-copy">
            <span class="section-kicker">Welcome back</span>
            <h2>今天也辛苦了，找一个舒服的方式说说心里话吧。</h2>
            <p>有些情绪不需要马上解决，先被看见也很重要。</p>
          </div>

          <div class="hero-status">
            <div class="hero-status__item">
              <span>登录状态</span>
              <strong>已连接到陪伴空间</strong>
            </div>
            <div class="hero-status__item hero-status__item--accent">
              <span>今日小提醒</span>
              <strong>慢一点也没关系，你已经在认真生活了。</strong>
            </div>
          </div>
        </div>

        <aside class="reminder-card glass-card">
          <span class="section-kicker">今日小提醒</span>
          <p>慢一点也没关系，你已经在认真生活了。</p>
          <div class="reminder-quote">先被看见，再去解决。</div>
        </aside>
      </section>

      <section class="stats-section">
        <div class="section-heading">
          <span class="section-kicker">Overview</span>
          <h3>你的陪伴空间概览</h3>
        </div>

        <div class="stats-grid">
          <article v-for="item in statCards" :key="item.key" class="stat-card glass-card">
            <div class="stat-card__icon" :class="`stat-card__icon--${item.theme}`">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div>
              <p>{{ item.label }}</p>
              <strong>{{ item.value }}</strong>
            </div>
          </article>
        </div>
      </section>

      <section class="recent-section">
        <div class="section-heading">
          <span class="section-kicker">Recent Activity</span>
          <h3>最近动态</h3>
        </div>

        <div v-if="loading" class="recent-grid">
          <div class="recent-panel glass-card">
            <el-skeleton animated :rows="5" />
          </div>
          <div class="recent-panel glass-card">
            <el-skeleton animated :rows="6" />
          </div>
        </div>

        <div v-else class="recent-grid">
          <article class="recent-panel glass-card">
            <div class="panel-head">
              <div>
                <span class="section-kicker">AI 会话</span>
                <h4>最近一次 AI 情绪陪伴</h4>
              </div>
              <el-button text class="panel-link" @click="goTo('/ai-chat')">进入 AI 聊天</el-button>
            </div>

            <template v-if="overview.recent_ai_session">
              <div class="session-card">
                <div class="session-card__title">{{ overview.recent_ai_session.title }}</div>
                <div class="session-card__meta">最后更新：{{ formatTime(overview.recent_ai_session.updated_at) }}</div>
              </div>
            </template>
            <el-empty
              v-else
              description="还没有聊天记录，开始一次新的陪伴对话吧。"
              :image-size="120"
            />
          </article>

          <article class="recent-panel glass-card">
            <div class="panel-head">
              <div>
                <span class="section-kicker">社区</span>
                <h4>最新帖子</h4>
              </div>
              <el-button text class="panel-link" @click="goTo('/community')">进入社区广场</el-button>
            </div>

            <template v-if="overview.recent_posts.length">
              <div class="post-list">
                <div v-for="post in overview.recent_posts" :key="post.id" class="post-item">
                  <div class="post-item__top">
                    <strong>{{ post.title }}</strong>
                    <span v-if="post.category" class="post-category">{{ post.category }}</span>
                  </div>
                  <div class="post-item__meta">
                    <span>点赞 {{ post.like_count }}</span>
                    <span>评论 {{ post.comment_count }}</span>
                  </div>
                </div>
              </div>
            </template>
            <el-empty
              v-else
              description="社区暂时还没有帖子，发布第一条心情记录吧。"
              :image-size="120"
            />
          </article>
        </div>
      </section>
    </main>

    <el-dialog
      v-model="profilePromptVisible"
      title="完善你的资料"
      width="520px"
      align-center
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      class="profile-prompt-dialog"
    >
      <div class="profile-prompt__intro">
        这些信息不是必填项，你可以先跳过。补全后会更方便后续做情绪陪伴和画像分析。
      </div>

      <el-form ref="profilePromptFormRef" :model="profilePromptForm" label-position="top" class="profile-prompt-form">
        <el-form-item label="邮箱">
          <el-input v-model="profilePromptForm.email" placeholder="请输入邮箱，留空也可以" />
        </el-form-item>

        <el-form-item label="职业">
          <el-input v-model="profilePromptForm.occupation" maxlength="50" show-word-limit placeholder="例如：学生、教师、程序员" />
        </el-form-item>

        <el-form-item label="年龄">
          <el-input-number v-model="profilePromptForm.age" :min="0" :max="150" :controls="true" class="age-input" placeholder="请输入年龄" />
        </el-form-item>

        <el-form-item label="性别">
          <el-select v-model="profilePromptForm.gender" placeholder="请选择性别" class="gender-select">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="其他" value="other" />
            <el-option label="未知" value="unknown" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="profile-prompt__actions">
          <el-button @click="skipProfilePrompt">暂不填写</el-button>
          <el-button type="primary" :loading="savingProfilePrompt" @click="submitProfilePrompt">保存并继续</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Collection, MagicStick, MessageBox, User, UserFilled } from '@element-plus/icons-vue'
import { getHomeOverview } from '../api/home'
import { updateProfile } from '../api/user'
import LogoutConfirmDialog from '../components/LogoutConfirmDialog.vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const profilePromptVisible = ref(false)
const logoutDialogVisible = ref(false)
const savingProfilePrompt = ref(false)
const profilePromptFormRef = ref()

const overview = reactive({
  user: {
    id: 0,
    nickname: '',
    avatar: '',
    username: '',
    email: '',
    occupation: '',
    age: null,
    gender: '',
    role: ''
  },
  statistics: {
    ai_chat_count: 0,
    friend_count: 0,
    post_count: 0,
    favorite_count: 0,
    unread_private_message_count: 0
  },
  recent_ai_session: null,
  recent_posts: []
})

const features = [
  {
    title: 'AI 情绪陪伴',
    description: '当你不知道该和谁说时，可以先在这里慢慢说。',
    route: '/ai-chat',
    theme: 'ai',
    badge: '智能陪伴',
    icon: ChatDotRound
  },
  {
    title: '好友聊天',
    description: '和熟悉的人说几句话，也许会轻松一点。',
    route: '/friends',
    theme: 'friends',
    badge: '真人互助',
    icon: UserFilled
  },
  {
    title: '社区广场',
    description: '看看别人的故事，也分享你的片刻心情。',
    route: '/community',
    theme: 'community',
    badge: '社区交流',
    icon: Collection
  }
]

const topTabs = [
  { label: '首页', route: '/home' },
  { label: 'AI 聊天', route: '/ai-chat' },
  { label: '社区', route: '/community' },
  { label: '好友', route: '/friends' },
  { label: '个人中心', route: '/profile' }
]

const statCards = computed(() => [
  {
    key: 'ai_chat_count',
    label: 'AI 聊天次数',
    value: overview.statistics.ai_chat_count,
    icon: ChatDotRound,
    theme: 'violet'
  },
  {
    key: 'friend_count',
    label: '好友数量',
    value: overview.statistics.friend_count,
    icon: User,
    theme: 'blue'
  },
  {
    key: 'post_count',
    label: '我的帖子',
    value: overview.statistics.post_count,
    icon: MessageBox,
    theme: 'mint'
  },
  {
    key: 'favorite_count',
    label: '我的收藏',
    value: overview.statistics.favorite_count,
    icon: Collection,
    theme: 'peach'
  },
  {
    key: 'unread_private_message_count',
    label: '未读消息',
    value: overview.statistics.unread_private_message_count,
    icon: UserFilled,
    theme: 'rose'
  }
])

const profilePromptForm = reactive({
  email: '',
  occupation: '',
  age: null,
  gender: ''
})

const displayName = computed(() => overview.user.nickname || overview.user.username || '朋友')
const avatarText = computed(() => (displayName.value || '朋').slice(0, 1))

const normalizePayload = (response) => response?.data ?? response ?? {}

const notifySessionUserUpdated = () => {
  window.dispatchEvent(new CustomEvent('session:user-updated'))
}

const syncProfilePromptForm = () => {
  profilePromptForm.email = overview.user.email || ''
  profilePromptForm.occupation = overview.user.occupation || ''
  profilePromptForm.age = overview.user.age ?? null
  profilePromptForm.gender = overview.user.gender || ''
}

const hasMissingPromptFields = () => {
  return !overview.user.occupation || overview.user.age === null || overview.user.age === undefined || !overview.user.gender
}

const getProfilePromptSeenKey = (userId) => `profile-prompt-seen:${userId}`

const shouldShowProfilePrompt = () => {
  if (!overview.user.id) return false
  if (!hasMissingPromptFields()) return false
  return localStorage.getItem(getProfilePromptSeenKey(overview.user.id)) !== '1'
}

const markProfilePromptSeen = () => {
  if (!overview.user.id) return
  localStorage.setItem(getProfilePromptSeenKey(overview.user.id), '1')
}

const openProfilePrompt = () => {
  syncProfilePromptForm()
  profilePromptVisible.value = true
}

const skipProfilePrompt = () => {
  markProfilePromptSeen()
  profilePromptVisible.value = false
}

const submitProfilePrompt = async () => {
  const payload = {}
  const email = profilePromptForm.email?.trim()
  const occupation = profilePromptForm.occupation?.trim()

  if (email) payload.email = email
  if (occupation) payload.occupation = occupation
  if (profilePromptForm.age !== null && profilePromptForm.age !== undefined && profilePromptForm.age !== '') {
    payload.age = profilePromptForm.age
  }
  if (profilePromptForm.gender) payload.gender = profilePromptForm.gender

  if (!Object.keys(payload).length) {
    skipProfilePrompt()
    return
  }

  savingProfilePrompt.value = true
  try {
    const response = await updateProfile(payload)
    const result = normalizePayload(response)
    Object.assign(overview.user, result.data || result)
    localStorage.setItem('user', JSON.stringify(overview.user))
    notifySessionUserUpdated()
    markProfilePromptSeen()
    profilePromptVisible.value = false
    ElMessage.success('资料已保存')
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '资料保存失败'
    ElMessage.error(message)
  } finally {
    savingProfilePrompt.value = false
  }
}

const formatTime = (value) => {
  if (!value) return '暂无时间'
  return String(value)
}

const goTo = (path) => {
  router.push(path)
}

const isActiveRoute = (path) => route.path === path || route.path.startsWith(`${path}/`)
const isCurrentRoute = (path) => route.path === path || route.path.startsWith(`${path}/`)

const goProfile = () => {
  router.push('/profile')
}

const openLogoutDialog = () => {
  logoutDialogVisible.value = true
}

const confirmLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  router.replace('/login')
}

const loadOverview = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.replace('/login')
    return
  }

  loading.value = true
  try {
    const response = await getHomeOverview()
    const payload = normalizePayload(response)

    Object.assign(overview.user, payload.user || {})
    Object.assign(overview.statistics, payload.statistics || {})
    overview.recent_ai_session = payload.recent_ai_session || null
    overview.recent_posts = Array.isArray(payload.recent_posts) ? payload.recent_posts : []

    localStorage.setItem('user', JSON.stringify(overview.user))
    notifySessionUserUpdated()
    if (shouldShowProfilePrompt()) {
      openProfilePrompt()
    }
  } catch (error) {
    const status = error?.response?.status
    if (status !== 401) {
      ElMessage.error('首页数据加载失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOverview()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  padding: 28px;
  position: relative;
  overflow: hidden;
  color: #2f3142;
  background:
    radial-gradient(circle at 18% 15%, rgba(124, 111, 246, 0.12), transparent 22%),
    radial-gradient(circle at 82% 12%, rgba(138, 124, 255, 0.12), transparent 18%),
    radial-gradient(circle at 84% 82%, rgba(169, 156, 255, 0.14), transparent 20%),
    linear-gradient(135deg, #f7f8fc 0%, #f4f0ff 45%, #eef7ff 100%);
}

.home-shell {
  width: min(1240px, 100%);
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.home-layout {
  display: grid;
  grid-template-columns: minmax(280px, 320px) minmax(0, 1fr);
  gap: 22px;
  margin-top: 22px;
  align-items: start;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  box-shadow: 0 18px 46px rgba(109, 109, 173, 0.12);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 18px 22px;
  border-radius: 24px;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border-radius: 16px;
  color: #ffffff;
  background: linear-gradient(135deg, #7c6ff6, #8a7cff 55%, #a99cff 100%);
  box-shadow: 0 14px 28px rgba(124, 111, 246, 0.28);
}

.brand-copy h1 {
  margin: 0;
  font-size: 22px;
  line-height: 1.1;
  color: #2f3142;
}

.brand-copy p {
  margin: 6px 0 0;
  color: #5f6475;
  font-size: 13px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 18px;
  background: rgba(124, 111, 246, 0.08);
}

.user-chip__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
<style scoped>
.home-page {
  min-height: 100vh;
  padding: 28px;
  position: relative;
  overflow: hidden;
  color: #2f3142;
  background:
    radial-gradient(circle at 18% 15%, rgba(124, 111, 246, 0.12), transparent 22%),
    radial-gradient(circle at 82% 12%, rgba(138, 124, 255, 0.12), transparent 18%),
    radial-gradient(circle at 84% 82%, rgba(169, 156, 255, 0.14), transparent 20%),
    linear-gradient(135deg, #f7f8fc 0%, #f4f0ff 45%, #eef7ff 100%);
}

.home-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 22px;
  width: min(1600px, 100%);
  margin: 0 auto;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  box-shadow: 0 18px 46px rgba(109, 109, 173, 0.12);
}

.brand-mark {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border-radius: 16px;
  color: #ffffff;
  background: linear-gradient(135deg, #7c6ff6, #8a7cff 55%, #a99cff 100%);
  box-shadow: 0 14px 28px rgba(124, 111, 246, 0.28);
}

.brand-copy h1,
.brand-copy p {
  margin: 0;
}

.brand-copy h1 {
  font-size: 22px;
  line-height: 1.1;
  color: #2f3142;
}

.brand-copy p {
  margin-top: 6px;
  color: #5f6475;
  font-size: 13px;
}

.sidebar {
  position: sticky;
  top: 28px;
  height: calc(100vh - 56px);
  padding: 18px 16px;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow: hidden;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 4px 10px;
}

.sidebar__section {
  display: grid;
  gap: 8px;
}

.sidebar__section-title {
  padding: 6px 10px 2px;
  font-size: 13px;
  color: #8a8fa3;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  min-height: 54px;
  padding: 0 14px;
  border: 0;
  border-radius: 14px;
  background: transparent;
  color: #3a3d57;
  text-align: left;
  cursor: pointer;
  transition: background 0.22s ease, transform 0.22s ease, box-shadow 0.22s ease;
}

.sidebar-item:hover {
  background: rgba(124, 111, 246, 0.06);
  transform: translateX(2px);
}

.sidebar-item--active {
  background: rgba(124, 111, 246, 0.08);
  box-shadow: inset 0 0 0 1px rgba(124, 111, 246, 0.08);
}

.sidebar-item__icon {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 10px;
  color: #5a5f7a;
  background: rgba(90, 95, 122, 0.08);
  flex: 0 0 auto;
}

.sidebar-item__icon--ai { color: #7c6ff6; background: rgba(124, 111, 246, 0.12); }
.sidebar-item__icon--friends { color: #6c8cff; background: rgba(108, 140, 255, 0.12); }
.sidebar-item__icon--community { color: #6cc7b2; background: rgba(108, 199, 178, 0.14); }
.sidebar-item__icon--violet { color: #7c6ff6; background: rgba(124, 111, 246, 0.12); }
.sidebar-item__icon--blue { color: #6c8cff; background: rgba(108, 140, 255, 0.12); }

.sidebar-item__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-item__text strong {
  font-size: 15px;
  font-weight: 600;
  color: #2f3142;
}

.sidebar-item__text small {
  font-size: 12px;
  color: #8a8fa3;
}

.sidebar__footer {
  margin-top: auto;
  display: grid;
  gap: 12px;
}

.sidebar__logout {
  width: 100%;
}

.content-shell {
  display: grid;
  gap: 18px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 64px;
  padding: 0 18px;
  border-radius: 20px;
}

.topbar-tabs {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.topbar-tab {
  min-height: 38px;
  padding: 0 12px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: #5f6475;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.22s ease, color 0.22s ease;
}

.topbar-tab:hover,
.topbar-tab--active {
  background: rgba(124, 111, 246, 0.1);
  color: #7c6ff6;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.topbar-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.topbar-meta__label {
  font-size: 12px;
  color: #8a8fa3;
}

.topbar-meta strong {
  font-size: 14px;
  color: #2f3142;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 18px;
  background: rgba(124, 111, 246, 0.08);
}

.user-chip--sidebar {
  padding: 12px 14px;
}

.user-chip--topbar {
  padding: 8px 12px;
}

.user-chip__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-chip__text span {
  font-size: 12px;
  color: #8a8fa3;
}

.user-chip__text strong {
  color: #2f3142;
}

.logout-button {
  min-height: 42px;
  padding: 0 18px;
  border-radius: 14px;
  color: #ffffff;
  border-color: transparent;
  background: linear-gradient(135deg, #7c6ff6 0%, #8a7cff 55%, #a99cff 100%);
  box-shadow: 0 16px 28px rgba(124, 111, 246, 0.22);
}

.logout-button:hover,
.panel-link:hover {
  transform: translateY(-2px);
}


.profile-prompt__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.page-body {
  display: grid;
  gap: 22px;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(290px, 0.85fr);
  gap: 22px;
}

.hero-card,
.reminder-card,
.recent-panel,
.stat-card {
  border-radius: 26px;
}

.hero-card {
  padding: 30px;
  display: grid;
  gap: 28px;
}

.hero-copy {
  max-width: 640px;
}

.section-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: #7c6ff6;
  background: rgba(124, 111, 246, 0.1);
}

.hero-copy h2 {
  margin: 14px 0 0;
  font-size: clamp(28px, 3vw, 46px);
  line-height: 1.16;
  letter-spacing: -0.03em;
  color: #2f3142;
}

.hero-copy p {
  margin: 14px 0 0;
  font-size: 16px;
  line-height: 1.9;
  color: #5f6475;
}

.hero-status {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.hero-status__item {
  padding: 18px 18px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(124, 111, 246, 0.08);
}

.hero-status__item span {
  display: block;
  font-size: 12px;
  color: #8a8fa3;
}

.hero-status__item strong {
  display: block;
  margin-top: 8px;
  font-size: 15px;
  line-height: 1.7;
  color: #2f3142;
}

.hero-status__item--accent {
  background: linear-gradient(135deg, rgba(124, 111, 246, 0.12), rgba(169, 156, 255, 0.12));
}

.reminder-card {
  padding: 26px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 22px;
}

.reminder-card p {
  margin: 8px 0 0;
  font-size: 18px;
  line-height: 1.8;
  color: #2f3142;
}

.reminder-quote {
  padding: 14px 16px;
  border-radius: 18px;
  color: #7c6ff6;
  background: rgba(124, 111, 246, 0.08);
}

.section-heading {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-heading h3 {
  margin: 0;
  font-size: 24px;
  line-height: 1.2;
  color: #2f3142;
}

.stats-section,
.recent-section {
  display: grid;
  gap: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  padding: 20px;
  display: grid;
  gap: 14px;
  min-height: 144px;
  transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.24s cubic-bezier(0.22, 1, 0.36, 1);
}

.stat-card:hover,
.recent-panel:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 48px rgba(109, 109, 173, 0.16);
}

.stat-card p {
  margin: 0;
  color: #8a8fa3;
  font-size: 13px;
}

.stat-card strong {
  display: block;
  margin-top: 10px;
  font-size: 28px;
  line-height: 1.1;
  color: #2f3142;
}

.stat-card__icon {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 14px;
  color: #ffffff;
}

.stat-card__icon--violet { background: linear-gradient(135deg, #7c6ff6, #a99cff); }
.stat-card__icon--blue { background: linear-gradient(135deg, #6c8cff, #8fbcff); }
.stat-card__icon--mint { background: linear-gradient(135deg, #6cc7b2, #a8e6cf); }
.stat-card__icon--peach { background: linear-gradient(135deg, #ff9d8f, #ffc7ad); }
.stat-card__icon--rose { background: linear-gradient(135deg, #ff8fb1, #ffb8d2); }

.recent-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.recent-panel {
  padding: 24px;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.24s cubic-bezier(0.22, 1, 0.36, 1);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.panel-head h4 {
  margin: 8px 0 0;
  font-size: 22px;
  color: #2f3142;
}

.panel-link {
  color: #7c6ff6;
}

.session-card {
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(124, 111, 246, 0.1), rgba(169, 156, 255, 0.08));
}

.session-card__title {
  font-size: 18px;
  color: #2f3142;
}

.session-card__meta {
  margin-top: 10px;
  font-size: 13px;
  color: #8a8fa3;
}

.post-list {
  display: grid;
  gap: 12px;
}

.post-item {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(124, 111, 246, 0.08);
}

.post-item__top,
.post-item__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.post-item__top strong {
  color: #2f3142;
}

.post-category {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #7c6ff6;
  background: rgba(124, 111, 246, 0.08);
}

.post-item__meta {
  margin-top: 10px;
  font-size: 13px;
  color: #8a8fa3;
}

.floating-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(24px);
  opacity: 0.82;
  pointer-events: none;
  animation: floatBlob 12s ease-in-out infinite;
}

.floating-orb--one {
  width: 240px;
  height: 240px;
  background: rgba(124, 111, 246, 0.2);
  top: 5%;
  left: 2%;
}

.floating-orb--two {
  width: 200px;
  height: 200px;
  background: rgba(138, 124, 255, 0.16);
  right: 4%;
  top: 16%;
  animation-delay: -3s;
}

.floating-orb--three {
  width: 200px;
  height: 200px;
  background: rgba(168, 230, 207, 0.18);
  right: 10%;
  bottom: 8%;
  animation-delay: -6s;
}

@keyframes floatBlob {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  50% {
    transform: translate3d(12px, -18px, 0) scale(1.04);
  }
}

@media (max-width: 1180px) {
  .home-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    top: 0;
    height: auto;
  }

  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .recent-grid,
  .hero-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .home-page {
    padding: 18px;
  }

  .sidebar {
    height: auto;
  }

  .topbar {
    padding: 16px;
    align-items: flex-start;
    flex-direction: column;
  }

  .topbar-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .hero-card,
  .reminder-card,
  .recent-panel,
  .stat-card {
    border-radius: 22px;
  }

  .hero-status {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .panel-head,
  .post-item__top,
  .post-item__meta {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 520px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.home-page {
  min-height: auto;
  padding: 0;
  color: #2f3142;
  background: transparent;
}

.home-content {
  display: grid;
  gap: 22px;
}
</style>