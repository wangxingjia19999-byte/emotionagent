<template>
  <view class="page-container admin-list-page">
    <text class="page-title">审计日志</text>
    <view class="list-item card" v-for="log in list" :key="log.id">
      <view class="item-main">
        <view class="item-info">
          <text class="item-name">{{ log.action }} · {{ log.target_type }} #{{ log.target_id }}</text>
          <text class="item-desc">管理员：{{ log.admin_name || log.admin_id }}</text>
          <text class="item-desc" v-if="log.detail">{{ log.detail }}</text>
          <text class="item-desc">{{ log.ip_address }} · {{ log.created_at }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAuditLogs } from '@/api/admin'

const list = ref([])

onShow(() => loadData())

async function loadData() {
  try { const res = await getAuditLogs({ page_size: 50 }); list.value = (res.data || res).items || [] } catch {}
}
</script>

<style lang="scss">@import './admin-common.scss';</style>
