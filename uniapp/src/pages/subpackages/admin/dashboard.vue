<template>
  <view class="page-container admin-page">
    <text class="page-title">管理后台</text>

    <view class="stats-grid" v-if="dash">
      <view class="stat-card">
        <text class="stat-val">{{ dash.users?.total || 0 }}</text>
        <text class="stat-lbl">总用户</text>
        <text class="stat-sub">本周新增 {{ dash.users?.new_this_week || 0 }}</text>
      </view>
      <view class="stat-card">
        <text class="stat-val">¥{{ (dash.shop?.revenue || 0).toFixed(0) }}</text>
        <text class="stat-lbl">总收入</text>
        <text class="stat-sub">{{ dash.shop?.total_orders || 0 }} 个订单</text>
      </view>
      <view class="stat-card">
        <text class="stat-val">{{ dash.community?.total_posts || 0 }}</text>
        <text class="stat-lbl">总帖子</text>
        <text class="stat-sub">本周新增 {{ dash.community?.new_this_week || 0 }}</text>
      </view>
      <view class="stat-card">
        <text class="stat-val">{{ dash.emotion?.total_questionnaires || 0 }}</text>
        <text class="stat-lbl">总问卷</text>
        <text class="stat-sub">{{ dash.emotion?.total_emotion_logs || 0 }} 条情绪记录</text>
      </view>
    </view>

    <!-- 快捷入口 -->
    <view class="menu-grid">
      <view class="menu-item" v-for="m in menus" :key="m.path" @tap="goPage(m.path)">
        <text class="menu-icon">{{ m.icon }}</text>
        <text class="menu-label">{{ m.label }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { getAdminDashboard } from '@/api/admin'

const authStore = useAuthStore()
const dash = ref(null)

const menus = [
  { icon: '📦', label: '商品管理', path: '/pages/subpackages/admin/products' },
  { icon: '📂', label: '分类管理', path: '/pages/subpackages/admin/categories' },
  { icon: '📋', label: '订单管理', path: '/pages/subpackages/admin/orders' },
  { icon: '👥', label: '用户管理', path: '/pages/subpackages/admin/users' },
  { icon: '📝', label: '问卷管理', path: '/pages/subpackages/admin/questionnaires' },
  { icon: '📊', label: '情绪日志', path: '/pages/subpackages/admin/emotion-logs' },
  { icon: '💬', label: '帖子管理', path: '/pages/subpackages/admin/posts' },
  { icon: '🛡️', label: '管理员', path: '/pages/subpackages/admin/admins' },
  { icon: '⚠️', label: '危机预警', path: '/pages/subpackages/admin/crisis-alerts' },
  { icon: '📜', label: '审计日志', path: '/pages/subpackages/admin/audit-logs' },
  { icon: '📈', label: '统计分析', path: '/pages/subpackages/admin/stats' },
  { icon: '⚙️', label: 'Agent配置', path: '/pages/subpackages/admin/agent-config' },
]

onShow(async () => {
  if (!authStore.isLoggedIn) return
  try {
    const res = await getAdminDashboard()
    dash.value = (res.data || res)
  } catch {}
})

function goPage(path) {
  uni.navigateTo({ url: path })
}
</script>

<style lang="scss" scoped>
.admin-page { padding-bottom: calc(48rpx + $safe-bottom); }
.page-title { font-size: 36rpx; font-weight: 700; color: $text-primary; margin-bottom: 24rpx; display: block; }
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16rpx; margin-bottom: 32rpx; }
.stat-card { padding: 24rpx; background: $bg-card; border-radius: $radius-lg; }
.stat-val { font-size: 36rpx; font-weight: 700; color: $primary-color; display: block; }
.stat-lbl { font-size: 26rpx; color: $text-secondary; margin-top: 4rpx; display: block; }
.stat-sub { font-size: 22rpx; color: $text-muted; margin-top: 4rpx; display: block; }
.menu-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; }
.menu-item { padding: 32rpx 16rpx; background: $bg-card; border-radius: $radius-lg; display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
.menu-icon { font-size: 44rpx; }
.menu-label { font-size: 24rpx; color: $text-secondary; }
</style>
