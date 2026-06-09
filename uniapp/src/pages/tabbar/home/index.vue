<template>
  <view class="page-container home-page">
    <!-- 顶部问候 -->
    <view class="greeting-section">
      <view class="greeting-left">
        <image
          class="greeting-avatar"
          :src="authStore.userAvatar || '/static/tab/profile.png'"
          mode="aspectFill"
          @tap="goProfile"
        />
        <view class="greeting-text">
          <text class="greeting-hello">
            {{ greetingWord }}，{{ authStore.displayName || '你好' }}
          </text>
          <text class="greeting-date">{{ todayDate }}</text>
        </view>
      </view>
      <view class="greeting-emotion">
        <text class="emotion-label" v-if="!loading && overview.statistics">
          今日已陪伴 {{ overview.statistics.ai_chat_count || 0 }} 次对话
        </text>
      </view>
    </view>

    <!-- 统计卡片 -->
    <view class="stats-grid" v-if="!loading">
      <view class="stat-card" @tap="goChat">
        <text class="stat-value">{{ overview.statistics?.friend_count || 0 }}</text>
        <text class="stat-label">好友</text>
      </view>
      <view class="stat-card" @tap="goCommunity">
        <text class="stat-value">{{ overview.statistics?.post_count || 0 }}</text>
        <text class="stat-label">帖子</text>
      </view>
      <view class="stat-card" @tap="goFavorites">
        <text class="stat-value">{{ overview.statistics?.favorite_count || 0 }}</text>
        <text class="stat-label">收藏</text>
      </view>
      <view class="stat-card" @tap="goFriends">
        <text class="stat-value">{{ overview.statistics?.unread_private_message_count || 0 }}</text>
        <text class="stat-label">未读消息</text>
      </view>
    </view>

    <!-- 快捷操作 -->
    <view class="quick-actions">
      <view class="action-item" @tap="goChat">
        <view class="action-icon-wrap" style="background: #ede9fe">
          <text class="action-icon">💬</text>
        </view>
        <text class="action-name">AI 陪伴</text>
      </view>
      <view class="action-item" @tap="goDailyCheck">
        <view class="action-icon-wrap" style="background: #fef3c7">
          <text class="action-icon">📋</text>
        </view>
        <text class="action-name">情绪打卡</text>
      </view>
      <view class="action-item" @tap="goCommunity">
        <view class="action-icon-wrap" style="background: #dbeafe">
          <text class="action-icon">🏘️</text>
        </view>
        <text class="action-name">社区广场</text>
      </view>
      <view class="action-item" @tap="goShop">
        <view class="action-icon-wrap" style="background: #fce7f3">
          <text class="action-icon">🛍️</text>
        </view>
        <text class="action-name">解压商城</text>
      </view>
    </view>

    <!-- 最近对话 -->
    <view class="section" v-if="overview.recent_ai_session">
      <view class="section-header">
        <text class="section-title">最近情绪陪伴</text>
        <text class="section-more" @tap="goChat">继续对话 →</text>
      </view>
      <view class="recent-session card" @tap="goChat">
        <view class="session-info">
          <text class="session-title">
            {{ overview.recent_ai_session.title || '上一次情绪陪伴' }}
          </text>
          <text class="session-time">{{ overview.recent_ai_session.updated_at }}</text>
        </view>
      </view>
    </view>

    <!-- 近期帖子 -->
    <view class="section" v-if="overview.recent_posts?.length">
      <view class="section-header">
        <text class="section-title">我的近期帖子</text>
        <text class="section-more" @tap="goCommunity">查看全部 →</text>
      </view>
      <view
        class="recent-post card"
        v-for="post in overview.recent_posts"
        :key="post.id"
        @tap="goPostDetail(post.id)"
      >
        <text class="post-title text-ellipsis">{{ post.title }}</text>
        <view class="post-meta">
          <text class="badge" v-if="post.category">{{ post.category }}</text>
          <text class="text-muted">❤️ {{ post.like_count || 0 }}</text>
          <text class="text-muted">💬 {{ post.comment_count || 0 }}</text>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-state" v-if="loading">
      <text class="text-muted">加载中...</text>
    </view>

    <EmptyState
      v-if="!loading && !overview.statistics"
      title="获取数据失败"
      description="请检查网络连接后重试"
      action-text="重新加载"
      @action="loadOverview"
    />
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { getHomeOverview } from '@/api/home'
import EmptyState from '@/components/empty-state.vue'
import { formatTime } from '@/utils/time'

const authStore = useAuthStore()
const appStore = useAppStore()
const loading = ref(true)
const overview = reactive({
  user: null,
  statistics: null,
  recent_ai_session: null,
  recent_posts: [],
})

const todayDate = computed(() => {
  const d = new Date()
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  return `${d.getMonth() + 1}月${d.getDate()}日 星期${weekDays[d.getDay()]}`
})

const greetingWord = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

onShow(async () => {
  if (!authStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/auth/login' })
    return
  }
  await loadOverview()
  appStore.refreshUnreadCount()
})

async function loadOverview() {
  loading.value = true
  try {
    const res = await getHomeOverview()
    const data = res.data || res
    Object.assign(overview, {
      user: data.user,
      statistics: data.statistics,
      recent_ai_session: data.recent_ai_session,
      recent_posts: data.recent_posts || [],
    })
  } catch {
    // 错误已处理
  } finally {
    loading.value = false
  }
}

function goProfile() {
  uni.switchTab({ url: '/pages/tabbar/profile/index' })
}

function goChat() {
  uni.switchTab({ url: '/pages/tabbar/chat/index' })
}

function goCommunity() {
  uni.switchTab({ url: '/pages/tabbar/community/index' })
}

function goDailyCheck() {
  uni.navigateTo({ url: '/pages/subpackages/questionnaire/daily-check' })
}

function goShop() {
  uni.navigateTo({ url: '/pages/subpackages/shop/index' })
}

function goFriends() {
  uni.navigateTo({ url: '/pages/subpackages/friends/list' })
}

function goFavorites() {
  uni.switchTab({ url: '/pages/tabbar/community/index' })
}

function goPostDetail(postId) {
  uni.navigateTo({
    url: `/pages/subpackages/posts/detail?id=${postId}`,
  })
}
</script>

<style lang="scss" scoped>
.home-page {
  padding-bottom: calc(24rpx + $safe-bottom);
}

.greeting-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32rpx;
  padding: $spacing-lg;
  background: linear-gradient(135deg, $primary-light, rgba(167, 139, 250, 0.08));
  border-radius: $radius-xl;
}

.greeting-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.greeting-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  border: 3rpx solid rgba(255, 255, 255, 0.8);
}

.greeting-hello {
  font-size: 32rpx;
  font-weight: 600;
  color: $text-primary;
  display: block;
}

.greeting-date {
  font-size: 24rpx;
  color: $text-muted;
  display: block;
  margin-top: 4rpx;
}

.greeting-emotion {
  .emotion-label {
    font-size: 24rpx;
    color: $primary-color;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.stat-card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 20rpx 12rpx;
  text-align: center;
  box-shadow: $shadow-sm;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 700;
  color: $primary-color;
  display: block;
}

.stat-label {
  font-size: 22rpx;
  color: $text-muted;
  margin-top: 4rpx;
}

.quick-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 32rpx;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.action-icon-wrap {
  width: 96rpx;
  height: 96rpx;
  border-radius: $radius-xl;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon {
  font-size: 44rpx;
}

.action-name {
  font-size: 24rpx;
  color: $text-secondary;
}

.section {
  margin-bottom: 32rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
}

.section-more {
  font-size: 26rpx;
  color: $primary-color;
}

.recent-session {
  display: flex;
  align-items: center;
}

.session-title {
  font-size: 28rpx;
  color: $text-primary;
  display: block;
}

.session-time {
  font-size: 24rpx;
  color: $text-muted;
  margin-top: 8rpx;
  display: block;
}

.recent-post {
  margin-bottom: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.post-title {
  font-size: 28rpx;
  color: $text-primary;
}

.post-meta {
  display: flex;
  gap: 16rpx;
  align-items: center;
}

.badge {
  background: $primary-light;
  color: $primary-color;
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: $radius-sm;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 48rpx;
}
</style>
