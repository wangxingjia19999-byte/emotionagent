<template>
  <view class="page-container detail-page">
    <!-- 帖子内容 -->
    <view class="detail-card card" v-if="post.id">
      <view class="detail-author">
        <image class="detail-avatar" :src="post.author?.avatar || '/static/tab/profile.png'" mode="aspectFill" />
        <view>
          <text class="detail-name">{{ post.is_anonymous ? '匿名用户' : (post.author?.nickname || post.author?.username) }}</text>
          <text class="detail-time">{{ post.created_at }}</text>
        </view>
      </view>
      <text class="detail-title" v-if="post.title">{{ post.title }}</text>
      <text class="detail-content">{{ post.content }}</text>
      <view class="detail-images" v-if="images.length">
        <image v-for="(url, i) in images" :key="i" class="detail-img" :src="url" mode="widthFix" @tap="previewImages(i)" />
      </view>
      <view class="detail-tags">
        <text class="tag" v-if="post.mood_tag">{{ post.mood_tag }}</text>
        <text class="tag" v-if="post.category">{{ post.category }}</text>
      </view>
      <view class="detail-actions">
        <view class="action" :class="{ active: post.liked }" @tap="toggleLike">
          <text>{{ post.liked ? '❤️' : '🤍' }} {{ post.like_count || 0 }}</text>
        </view>
        <view class="action" :class="{ active: post.hugged }" @tap="toggleHug">
          <text>🤗 {{ post.hug_count || 0 }}</text>
        </view>
        <view class="action" :class="{ active: post.favorited }" @tap="toggleFavorite">
          <text>{{ post.favorited ? '⭐ 已收藏' : '☆ 收藏' }}</text>
        </view>
      </view>
    </view>

    <!-- 评论列表 -->
    <view class="comments-section">
      <text class="comments-title">评论 ({{ comments.length }})</text>
      <view class="comment-item" v-for="c in comments" :key="c.id">
        <image class="comment-avatar" :src="c.author?.avatar || '/static/tab/profile.png'" mode="aspectFill" />
        <view class="comment-body">
          <view class="comment-header">
            <text class="comment-name">{{ c.author?.nickname || c.author?.username }}</text>
            <text class="comment-time">{{ c.created_at }}</text>
          </view>
          <text class="comment-text">{{ c.content }}</text>
        </view>
      </view>
      <EmptyState v-if="!comments.length" title="暂无评论" description="来发表第一条评论吧" />
    </view>

    <!-- 底部评论输入 -->
    <view class="comment-input-bar safe-bottom">
      <input class="comment-input" v-model="commentText" placeholder="写下你的评论..." confirm-type="send" @confirm="submitComment" />
      <button class="btn-primary comment-send" :disabled="!commentText.trim()" @tap="submitComment">发送</button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { getPostDetail, likePost, unlikePost, hugPost, unhugPost, favoritePost, unfavoritePost, getComments, createComment } from '@/api/posts'
import EmptyState from '@/components/empty-state.vue'

const authStore = useAuthStore()
const post = reactive({ id: 0, liked: false, hugged: false, favorited: false, like_count: 0, hug_count: 0 })
const comments = ref([])
const commentText = ref('')

const images = computed(() => {
  const urls = post.image_urls || []
  if (post.image_url && !urls.includes(post.image_url)) urls.unshift(post.image_url)
  return urls.filter(Boolean)
})

onLoad(async (options) => {
  if (!authStore.isLoggedIn) return uni.reLaunch({ url: '/pages/auth/login' })
  if (options.id) {
    await Promise.all([loadPost(options.id), loadComments(options.id)])
  }
})

async function loadPost(id) {
  try {
    const res = await getPostDetail(id)
    Object.assign(post, res.data || res)
  } catch {}
}

async function loadComments(postId) {
  try {
    const res = await getComments(postId)
    comments.value = (res.data || res).items || []
  } catch {}
}

async function toggleLike() {
  try {
    post.liked ? await unlikePost(post.id) : await likePost(post.id)
    post.liked = !post.liked
    post.like_count += post.liked ? 1 : -1
  } catch {}
}

async function toggleHug() {
  try {
    post.hugged ? await unhugPost(post.id) : await hugPost(post.id)
    post.hugged = !post.hugged
    post.hug_count += post.hugged ? 1 : -1
  } catch {}
}

async function toggleFavorite() {
  try {
    post.favorited ? await unfavoritePost(post.id) : await favoritePost(post.id)
    post.favorited = !post.favorited
  } catch {}
}

async function submitComment() {
  const text = commentText.value.trim()
  if (!text) return
  try {
    await createComment(post.id, text)
    commentText.value = ''
    loadComments(post.id)
  } catch {}
}

function previewImages(current) {
  uni.previewImage({ urls: images.value, current })
}
</script>

<style lang="scss" scoped>
.detail-page { padding-bottom: calc(120rpx + $safe-bottom); }
.detail-card { margin-bottom: 24rpx; padding: 32rpx; }
.detail-author { display: flex; align-items: center; gap: 16rpx; margin-bottom: 20rpx; }
.detail-avatar { width: 80rpx; height: 80rpx; border-radius: 50%; background: $primary-light; }
.detail-name { font-size: 28rpx; font-weight: 500; color: $text-primary; display: block; }
.detail-time { font-size: 22rpx; color: $text-muted; }
.detail-title { font-size: 36rpx; font-weight: 600; color: $text-primary; margin-bottom: 16rpx; display: block; }
.detail-content { font-size: 30rpx; color: $text-secondary; line-height: 1.8; display: block; margin-bottom: 20rpx; }
.detail-images { margin-bottom: 20rpx; }
.detail-img { width: 100%; border-radius: $radius-md; margin-bottom: 8rpx; background: $bg-page; }
.detail-tags { display: flex; gap: 8rpx; margin-bottom: 20rpx; }
.tag { background: $primary-light; color: $primary-color; font-size: 22rpx; padding: 4rpx 12rpx; border-radius: $radius-sm; }
.detail-actions { display: flex; justify-content: space-around; padding-top: 20rpx; border-top: 1rpx solid $border-light; }
.action { font-size: 28rpx; &.active { opacity: 1; } }
.comments-section { margin-bottom: 24rpx; }
.comments-title { font-size: 30rpx; font-weight: 600; color: $text-primary; margin-bottom: 20rpx; display: block; }
.comment-item { display: flex; gap: 12rpx; margin-bottom: 20rpx; padding: 20rpx; background: $bg-card; border-radius: $radius-lg; }
.comment-avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: $bg-page; flex-shrink: 0; }
.comment-body { flex: 1; }
.comment-header { display: flex; justify-content: space-between; margin-bottom: 8rpx; }
.comment-name { font-size: 26rpx; font-weight: 500; color: $text-primary; }
.comment-time { font-size: 22rpx; color: $text-muted; }
.comment-text { font-size: 28rpx; color: $text-secondary; line-height: 1.6; }
.comment-input-bar { position: fixed; bottom: 0; left: 0; right: 0; background: $bg-card; padding: 12rpx 20rpx; display: flex; gap: 12rpx; align-items: center; border-top: 1rpx solid $border-light; }
.comment-input { flex: 1; height: 72rpx; background: $bg-page; border-radius: 36rpx; padding: 0 24rpx; font-size: 28rpx; }
.comment-send { height: 72rpx; border-radius: 36rpx; padding: 0 24rpx; font-size: 26rpx; flex-shrink: 0; }
</style>
