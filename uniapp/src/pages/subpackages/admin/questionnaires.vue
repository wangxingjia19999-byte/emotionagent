<template>
  <view class="page-container admin-list-page">
    <text class="page-title">问卷管理</text>
    <view class="filter-row">
      <view class="filter-chip" :class="{ active: !scaleFilter }" @tap="scaleFilter=''; loadData()">全部</view>
      <view v-for="s in scaleTypes" :key="s.key" class="filter-chip" :class="{ active: scaleFilter===s.key }" @tap="scaleFilter=s.key; loadData()">{{ s.name }}</view>
    </view>
    <view class="list-item card" v-for="q in list" :key="q.id">
      <view class="item-main">
        <view class="item-info">
          <text class="item-name">{{ q.scale_name || q.scale_type }}</text>
          <text class="item-desc">得分: {{ q.total_score }} | {{ q.result_level }}</text>
          <text class="item-desc">{{ q.created_at }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAdminQuestionnaires } from '@/api/admin'

const list = ref([]); const scaleFilter = ref('')
const scaleTypes = [{ key: 'daily_mood', name: '每日心情' }, { key: 'phq9', name: 'PHQ-9' }, { key: 'gad7', name: 'GAD-7' }]

onShow(() => loadData())

async function loadData() {
  try {
    const params = {}
    if (scaleFilter.value) params.scale_type = scaleFilter.value
    const res = await getAdminQuestionnaires(params)
    list.value = (res.data || res).items || []
  } catch {}
}
</script>

<style lang="scss">@import './admin-common.scss';</style>
