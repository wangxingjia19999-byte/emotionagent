<template>
  <view class="page-container admin-list-page">
    <text class="page-title">情绪日志</text>
    <view class="list-item card" v-for="e in list" :key="e.id">
      <view class="item-main">
        <text class="item-icon" style="font-size:44rpx">{{ emotionIcon(e.emotion_label) }}</text>
        <view class="item-info">
          <text class="item-name">{{ e.emotion_label || '未知' }} · 强度 {{ e.intensity || '-' }}/5</text>
          <text class="item-desc" v-if="e.raw_text">{{ e.raw_text?.slice(0, 80) }}</text>
          <text class="item-desc">{{ e.created_at }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAdminEmotionLogs } from '@/api/admin'

const list = ref([])
const emotionIcons = { '开心':'😊', '难过':'😢', '焦虑':'😰', '愤怒':'😡', '温暖':'🥰', '平静':'😌', '孤独':'🥺' }
function emotionIcon(label) { return emotionIcons[label] || '💭' }

onShow(() => loadData())

async function loadData() {
  try { const res = await getAdminEmotionLogs(); list.value = (res.data || res).items || [] } catch {}
}
</script>

<style lang="scss">@import './admin-common.scss';</style>
