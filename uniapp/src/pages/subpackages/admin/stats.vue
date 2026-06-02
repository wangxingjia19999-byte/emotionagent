<template>
  <view class="page-container admin-list-page">
    <text class="page-title">统计分析</text>

    <!-- 本周概览 -->
    <view class="card" style="margin-bottom:24rpx" v-if="overview">
      <text class="stat-title">本周概览</text>
      <view class="stat-row">
        <text>新增用户：{{ overview.this_week?.new_users || 0 }} (较上周 {{ overview.this_week?.new_users_vs_last_week >= 0 ? '+' : '' }}{{ overview.this_week?.new_users_vs_last_week || 0 }})</text>
      </view>
      <view class="stat-row">
        <text>本周收入：¥{{ overview.this_week?.revenue || 0 }}</text>
      </view>
      <view class="stat-row">
        <text>最多情绪：{{ overview.this_week?.top_emotion || '-' }}</text>
      </view>
      <view class="stat-row">
        <text>危机预警：{{ overview.this_week?.crisis_alerts || 0 }} 次</text>
      </view>
    </view>

    <!-- 情绪分布 -->
    <view class="card" style="margin-bottom:24rpx" v-if="emotionTrends">
      <text class="stat-title">情绪分布 (近{{ days }}天)</text>
      <view class="stat-row" v-for="e in emotionTrends" :key="e.emotion">
        <text>{{ e.emotion }}：{{ e.count }} 次 ({{ e.percentage }}%)</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getStatsOverview, getEmotionTrends } from '@/api/admin'

const overview = ref(null)
const emotionTrends = ref(null)
const days = ref(30)

onShow(async () => {
  try {
    const [overRes, emoRes] = await Promise.all([getStatsOverview(), getEmotionTrends(days.value)])
    overview.value = (overRes.data || overRes)
    emotionTrends.value = (emoRes.data || emoRes).distribution || []
  } catch {}
})
</script>

<style lang="scss">@import './admin-common.scss';
.stat-title { font-size:30rpx; font-weight:600; color:$text-primary; margin-bottom:16rpx; display:block; }
.stat-row { padding:8rpx 0; font-size:26rpx; color:$text-secondary; }
</style>
