<template>
  <view class="page-container admin-list-page">
    <text class="page-title">Agent 配置 (MCP)</text>

    <view class="card" style="margin-bottom:24rpx">
      <text class="stat-title">MCP 服务器</text>
      <view class="list-item" v-for="s in servers" :key="s.id" style="margin-bottom:12rpx">
        <view class="item-info">
          <text class="item-name">{{ s.name }}</text>
          <text class="item-desc">命令: {{ s.command }}</text>
          <text class="item-desc" :class="{ 'text-primary': s.enabled }">{{ s.enabled ? '已启用' : '已禁用' }}</text>
        </view>
      </view>
    </view>

    <view class="card">
      <text class="stat-title">系统预设</text>
      <button class="btn-primary" style="margin-top:16rpx" @tap="loadPresets">加载预设 MCP 配置</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMcpStatus } from '@/api/mcp'
import { getMcpPresets, loadMcpPresets } from '@/api/mcp'

const servers = ref([])

onShow(async () => {
  try { const res = await getMcpStatus(); servers.value = (res.data || res) || [] } catch {}
})

async function loadPresets() {
  try { await loadMcpPresets(); uni.showToast({ title: '加载成功', icon: 'success' }) } catch {}
}
</script>

<style lang="scss">@import './admin-common.scss';
.stat-title { font-size:30rpx; font-weight:600; color:$text-primary; margin-bottom:16rpx; display:block; }
.text-primary { color: $primary-color; }
</style>
