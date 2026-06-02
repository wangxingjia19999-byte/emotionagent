<template>
  <view class="empty-state">
    <view class="empty-icon">{{ icon }}</view>
    <text class="empty-title">{{ title }}</text>
    <text class="empty-desc" v-if="description">{{ description }}</text>
    <button class="btn-primary empty-action" v-if="actionText" @tap="$emit('action')">
      {{ actionText }}
    </button>
  </view>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '' },
  actionText: { type: String, default: '' },
})
defineEmits(['action'])
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 48rpx;
}

.empty-icon {
  font-size: 96rpx;
  margin-bottom: 24rpx;
}

.empty-title {
  font-size: 30rpx;
  color: $text-secondary;
  margin-bottom: 8rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: $text-muted;
  text-align: center;
  line-height: 1.6;
  margin-bottom: 32rpx;
}

.empty-action {
  padding: 16rpx 48rpx;
  font-size: 28rpx;
}
</style>
