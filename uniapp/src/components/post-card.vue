<template>
  <view class="post-card card" @tap="$emit('click', post)">
    <!-- 头部：作者信息 -->
    <view class="post-header">
      <view class="author-info">
        <image
          class="author-avatar"
          :src="post.author?.avatar || '/static/tab/profile.png'"
          mode="aspectFill"
        />
        <view class="author-text">
          <text class="author-name">
            {{ post.is_anonymous ? '匿名用户' : (post.author?.nickname || post.author?.username || '匿名') }}
          </text>
          <text class="post-time">{{ formatTime(post.created_at) }}</text>
        </view>
      </view>
      <view class="post-tags">
        <text class="tag mood-tag" v-if="post.mood_tag">{{ post.mood_tag }}</text>
        <text class="tag cat-tag" v-if="post.category">{{ post.category }}</text>
      </view>
    </view>

    <!-- 标题 -->
    <text class="post-title" v-if="post.title">{{ post.title }}</text>

    <!-- 内容 -->
    <text class="post-content" :class="{ clamp: !expanded }">{{ post.content }}</text>
    <text
      class="expand-btn"
      v-if="needExpand"
      @tap.stop="$emit('expand', post)"
    >{{ expanded ? '收起' : '展开' }}</text>

    <!-- 图片 -->
    <view class="post-images" v-if="postImages.length">
      <image
        v-for="(url, i) in postImages.slice(0, maxImages)"
        :key="i"
        class="post-image"
        :class="getImageClass(postImages.length)"
        :src="url"
        mode="aspectFill"
        @tap.stop="previewImages(i)"
      />
      <view class="image-more" v-if="postImages.length > maxImages" @tap.stop="$emit('click', post)">
        <text>+{{ postImages.length - maxImages }}</text>
      </view>
    </view>

    <!-- 互动栏 -->
    <view class="post-actions">
      <view class="action" :class="{ active: post.liked }" @tap.stop="$emit('like', post)">
        <text>{{ post.liked ? '❤️' : '🤍' }}</text>
        <text class="action-count">{{ post.like_count || 0 }}</text>
      </view>
      <view class="action" @tap.stop="$emit('click', post)">
        <text>💬</text>
        <text class="action-count">{{ post.comment_count || 0 }}</text>
      </view>
      <view class="action" :class="{ active: post.hugged }" @tap.stop="$emit('hug', post)">
        <text>🤗</text>
        <text class="action-count">{{ post.hug_count || 0 }}</text>
      </view>
      <view class="action" :class="{ active: post.favorited }" @tap.stop="$emit('favorite', post)">
        <text>{{ post.favorited ? '⭐' : '☆' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { formatTime } from '@/utils/time'

const props = defineProps({
  post: { type: Object, required: true },
  expanded: { type: Boolean, default: false },
  maxImages: { type: Number, default: 3 },
})

defineEmits(['click', 'like', 'hug', 'favorite', 'expand'])

const postImages = computed(() => {
  const urls = props.post.image_urls || []
  if (props.post.image_url && !urls.includes(props.post.image_url)) {
    urls.unshift(props.post.image_url)
  }
  return urls.filter(Boolean)
})

const needExpand = computed(() => {
  return (props.post.content || '').length > 120
})

function getImageClass(count) {
  if (count === 1) return 'single'
  if (count === 2 || count === 4) return 'double'
  return 'triple'
}

function previewImages(current) {
  uni.previewImage({
    urls: postImages.value,
    current: current,
  })
}
</script>

<style lang="scss" scoped>
.post-card {
  margin-bottom: 16rpx;
  padding: 24rpx;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16rpx;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.author-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: $primary-light;
}

.author-name {
  font-size: 28rpx;
  font-weight: 500;
  color: $text-primary;
  display: block;
}

.post-time {
  font-size: 22rpx;
  color: $text-muted;
  margin-top: 4rpx;
  display: block;
}

.post-tags {
  display: flex;
  gap: 8rpx;
  flex-wrap: wrap;
}

.tag {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: $radius-sm;
}

.mood-tag {
  background: $primary-light;
  color: $primary-color;
}

.cat-tag {
  background: $bg-page;
  color: $text-muted;
}

.post-title {
  font-size: 32rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 12rpx;
  display: block;
}

.post-content {
  font-size: 28rpx;
  color: $text-secondary;
  line-height: 1.7;
  margin-bottom: 16rpx;

  &.clamp {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.expand-btn {
  font-size: 26rpx;
  color: $primary-color;
  margin-bottom: 16rpx;
}

.post-images {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.post-image {
  border-radius: $radius-md;
  background: $bg-page;

  &.single {
    width: 400rpx;
    height: 300rpx;
  }
  &.double {
    width: calc(50% - 4rpx);
    height: 240rpx;
  }
  &.triple {
    width: calc(33.33% - 6rpx);
    height: 220rpx;
  }
}

.image-more {
  width: calc(33.33% - 6rpx);
  height: 220rpx;
  background: $bg-page;
  border-radius: $radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  color: $text-muted;
}

.post-actions {
  display: flex;
  gap: 32rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid $border-light;
}

.action {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 28rpx;

  &.active {
    opacity: 1;
  }
}

.action-count {
  font-size: 24rpx;
  color: $text-muted;
}
</style>
