<template>
  <view class="page-container community-page">
    <!-- 顶部筛选栏 -->
    <view class="filter-bar">
      <view class="search-row">
        <input
          class="search-input"
          v-model="keyword"
          placeholder="搜索帖子..."
          placeholder-class="input-placeholder"
          confirm-type="search"
          @confirm="handleSearch"
        />
        <text class="search-icon" @tap="handleSearch">🔍</text>
      </view>
      <scroll-view class="filter-tabs" scroll-x :show-scrollbar="false">
        <view
          class="filter-tab"
          :class="{ active: activeCategory === '' }"
          @tap="selectCategory('')"
        >全部</view>
        <view
          class="filter-tab"
          v-for="cat in categories"
          :key="cat"
          :class="{ active: activeCategory === cat }"
          @tap="selectCategory(cat)"
        >{{ cat }}</view>
      </scroll-view>
    </view>

    <!-- 排序栏 -->
    <view class="sort-bar">
      <view
        class="sort-item"
        :class="{ active: sort === 'latest' }"
        @tap="sort = 'latest'; loadPosts()"
      >最新</view>
      <view
        class="sort-item"
        :class="{ active: sort === 'hot' }"
        @tap="sort = 'hot'; loadPosts()"
      >最热</view>
      <view class="sort-spacer"></view>
      <button class="btn-ghost publish-btn" @tap="goPublish">
        ✏️ 发帖
      </button>
    </view>

    <!-- 帖子列表 -->
    <scroll-view
      class="post-list"
      scroll-y
      @scrolltolower="loadMore"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @click="goDetail"
        @like="handleLike"
        @hug="handleHug"
        @favorite="handleFavorite"
      />
      <view class="load-more-status">
        <text class="text-muted" v-if="loading">加载中...</text>
        <text class="text-muted" v-else-if="noMore">— 没有更多了 —</text>
      </view>
      <EmptyState
        v-if="!loading && posts.length === 0"
        title="还没有帖子"
        description="来发布第一条帖子吧"
        action-text="发布帖子"
        @action="goPublish"
      />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { getPosts, likePost, unlikePost, hugPost, unhugPost, favoritePost, unfavoritePost } from '@/api/posts'
import PostCard from '@/components/post-card.vue'
import EmptyState from '@/components/empty-state.vue'

const authStore = useAuthStore()
const posts = ref([])
const keyword = ref('')
const activeCategory = ref('')
const sort = ref('latest')
const page = ref(1)
const pageSize = 10
const total = ref(0)
const loading = ref(false)
const refreshing = ref(false)
const noMore = ref(false)

const categories = ['情绪倾诉', '学习生活', '人际关系', '校园日常', '其他']

onShow(async () => {
  if (!authStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/auth/login' })
    return
  }
  page.value = 1
  await loadPosts()
})

async function loadPosts() {
  loading.value = true
  try {
    const res = await getPosts({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value || undefined,
      category: activeCategory.value || undefined,
      sort: sort.value,
    })
    const data = res.data || res
    posts.value = data.items || []
    total.value = data.total || 0
    noMore.value = posts.value.length >= total.value
  } catch {
    // 错误已在 request.js 中处理
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

async function loadMore() {
  if (loading.value || noMore.value) return
  page.value++
  loading.value = true
  try {
    const res = await getPosts({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value || undefined,
      category: activeCategory.value || undefined,
      sort: sort.value,
    })
    const data = res.data || res
    const newItems = data.items || []
    posts.value = [...posts.value, ...newItems]
    noMore.value = posts.value.length >= (data.total || 0)
  } catch {
    page.value--
  } finally {
    loading.value = false
  }
}

function onRefresh() {
  refreshing.value = true
  page.value = 1
  loadPosts()
}

function selectCategory(cat) {
  activeCategory.value = cat
  page.value = 1
  loadPosts()
}

function handleSearch() {
  page.value = 1
  loadPosts()
}

async function handleLike(post) {
  try {
    if (post.liked) {
      await unlikePost(post.id)
      post.liked = false
      post.like_count = Math.max(0, (post.like_count || 0) - 1)
    } else {
      await likePost(post.id)
      post.liked = true
      post.like_count = (post.like_count || 0) + 1
    }
  } catch {}
}

async function handleHug(post) {
  try {
    if (post.hugged) {
      await unhugPost(post.id)
      post.hugged = false
      post.hug_count = Math.max(0, (post.hug_count || 0) - 1)
    } else {
      await hugPost(post.id)
      post.hugged = true
      post.hug_count = (post.hug_count || 0) + 1
    }
  } catch {}
}

async function handleFavorite(post) {
  try {
    if (post.favorited) {
      await unfavoritePost(post.id)
      post.favorited = false
    } else {
      await favoritePost(post.id)
      post.favorited = true
    }
  } catch {}
}

function goDetail(post) {
  uni.navigateTo({
    url: `/pages/subpackages/posts/detail?id=${post.id}`,
  })
}

function goPublish() {
  uni.navigateTo({ url: '/pages/subpackages/posts/publish' })
}
</script>

<style lang="scss" scoped>
.community-page {
  padding-bottom: calc(24rpx + $safe-bottom);
}

.filter-bar {
  margin-bottom: 16rpx;
}

.search-row {
  position: relative;
  margin-bottom: 16rpx;
}

.search-input {
  width: 100%;
  height: 80rpx;
  background: $bg-card;
  border-radius: 40rpx;
  padding: 0 80rpx 0 32rpx;
  font-size: 28rpx;
  color: $text-primary;
  box-shadow: $shadow-sm;
}

.input-placeholder {
  color: $text-placeholder;
}

.search-icon {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  font-size: 32rpx;
}

.filter-tabs {
  white-space: nowrap;
}

.filter-tab {
  display: inline-block;
  padding: 10rpx 24rpx;
  font-size: 26rpx;
  color: $text-secondary;
  background: $bg-card;
  border-radius: 32rpx;
  margin-right: 12rpx;

  &.active {
    background: $primary-light;
    color: $primary-color;
    font-weight: 500;
  }
}

.sort-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.sort-item {
  font-size: 26rpx;
  color: $text-muted;

  &.active {
    color: $primary-color;
    font-weight: 500;
  }
}

.sort-spacer {
  flex: 1;
}

.publish-btn {
  font-size: 24rpx;
  padding: 8rpx 20rpx;
}

.post-list {
  min-height: 60vh;
}

.load-more-status {
  display: flex;
  justify-content: center;
  padding: 32rpx;
}
</style>
