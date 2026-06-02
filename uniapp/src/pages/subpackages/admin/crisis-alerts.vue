<template>
  <view class="page-container admin-list-page">
    <text class="page-title">危机预警</text>
    <view class="list-item card" v-for="a in list" :key="a.id">
      <view class="item-main">
        <view class="item-info">
          <text class="item-name">⚠️ 风险等级：{{ a.risk_level || '未知' }}</text>
          <text class="item-desc">用户：{{ a.username || a.user_id }}</text>
          <text class="item-desc" v-if="a.raw_text">内容：{{ a.raw_text?.slice(0, 100) }}</text>
          <text class="item-desc">{{ a.created_at }}</text>
        </view>
      </view>
      <view class="item-actions">
        <button class="btn-danger small-btn" @tap="delItem(a.id)">删除</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getCrisisAlerts, deleteCrisisAlert } from '@/api/admin'

const list = ref([])

onShow(() => loadData())

async function loadData() {
  try { const res = await getCrisisAlerts(); list.value = (res.data || res).items || [] } catch {}
}

async function delItem(id) { try { await deleteCrisisAlert(id); loadData() } catch {} }
</script>

<style lang="scss">@import './admin-common.scss';</style>
