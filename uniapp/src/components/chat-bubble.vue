<template>
  <view class="chat-bubble" :class="isMine ? 'mine' : 'yours'">
    <!-- 对方头像 -->
    <image
      v-if="!isMine"
      class="bubble-avatar"
      src="/static/tab/chat.png"
      mode="aspectFill"
    />

    <view class="bubble-body">
      <!-- 危机提示横幅 -->
      <view
        class="crisis-banner"
        v-if="message.crisisDetected"
      >
        <text class="crisis-icon">⚠️</text>
        <text class="crisis-text">
          如果你正在经历困难，请拨打心理援助热线 400-161-9995。你并不孤单。
        </text>
      </view>

      <!-- 消息文本 -->
      <view class="bubble-content" :class="isMine ? 'mine-bg' : 'yours-bg'">
        <text class="bubble-text">{{ message.content }}</text>
      </view>

      <!-- 商品推荐卡片 -->
      <view
        class="product-recommend"
        v-if="message.products?.length"
      >
        <text class="recommend-title">🛍️ 为你推荐</text>
        <view
          class="product-mini-card"
          v-for="p in message.products"
          :key="p.index"
          @tap="goProduct(p)"
        >
          <text class="product-name">{{ p.name }}</text>
          <view class="product-price-row">
            <text class="product-price">¥{{ p.price }}</text>
            <text class="product-original" v-if="p.originalPrice">
              ¥{{ p.originalPrice }}
            </text>
          </view>
          <text class="product-category" v-if="p.category">{{ p.category }}</text>
        </view>
      </view>

      <!-- 时间 -->
      <text class="bubble-time" v-if="message.time">{{ message.time }}</text>
    </view>

    <!-- 自己头像 -->
    <image
      v-if="isMine"
      class="bubble-avatar"
      :src="userAvatar || '/static/tab/profile.png'"
      mode="aspectFill"
    />
  </view>
</template>

<script setup>
import { formatChatTime } from '@/utils/time'

const props = defineProps({
  message: {
    type: Object,
    required: true,
    default: () => ({
      content: '',
      role: 'assistant',
      time: '',
      crisisDetected: false,
      products: [],
    }),
  },
  isMine: { type: Boolean, default: false },
  userAvatar: { type: String, default: '' },
})

function goProduct(product) {
  // 跳转商品详情
}
</script>

<style lang="scss" scoped>
.chat-bubble {
  display: flex;
  margin-bottom: 24rpx;
  padding: 0 16rpx;

  &.mine {
    flex-direction: row-reverse;
  }
}

.bubble-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  flex-shrink: 0;
  background: $primary-light;
}

.bubble-body {
  max-width: 75%;
  display: flex;
  flex-direction: column;
}

.mine .bubble-body {
  align-items: flex-end;
  margin-right: 12rpx;
}

.yours .bubble-body {
  align-items: flex-start;
  margin-left: 12rpx;
}

.bubble-content {
  padding: 16rpx 24rpx;
  border-radius: $radius-lg;
  min-width: 80rpx;
}

.mine-bg {
  background: $primary-gradient;
}

.mine-bg .bubble-text {
  color: #fff;
}

.yours-bg {
  background: $bg-card;
  box-shadow: $shadow-sm;
}

.yours-bg .bubble-text {
  color: $text-primary;
}

.bubble-text {
  font-size: 30rpx;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
}

.bubble-time {
  font-size: 22rpx;
  color: $text-muted;
  margin-top: 8rpx;
}

.crisis-banner {
  background: #fff3f0;
  border: 1rpx solid #ffccc7;
  border-radius: $radius-md;
  padding: 12rpx 16rpx;
  margin-bottom: 8rpx;
  display: flex;
  gap: 8rpx;
  align-items: flex-start;
}

.crisis-icon {
  font-size: 28rpx;
}

.crisis-text {
  font-size: 24rpx;
  color: #cf1322;
  line-height: 1.5;
  flex: 1;
}

.product-recommend {
  margin-top: 12rpx;
  width: 100%;
}

.recommend-title {
  font-size: 24rpx;
  color: $text-muted;
  margin-bottom: 8rpx;
  display: block;
}

.product-mini-card {
  background: $bg-card;
  border-radius: $radius-md;
  padding: 16rpx;
  margin-bottom: 8rpx;
  box-shadow: $shadow-sm;
}

.product-name {
  font-size: 26rpx;
  color: $text-primary;
  font-weight: 500;
  display: block;
}

.product-price-row {
  display: flex;
  gap: 8rpx;
  align-items: baseline;
  margin-top: 4rpx;
}

.product-price {
  font-size: 28rpx;
  color: $error-color;
  font-weight: 600;
}

.product-original {
  font-size: 22rpx;
  color: $text-muted;
  text-decoration: line-through;
}

.product-category {
  font-size: 22rpx;
  color: $primary-color;
  background: $primary-light;
  padding: 2rpx 8rpx;
  border-radius: 4rpx;
  align-self: flex-start;
  margin-top: 4rpx;
}
</style>
