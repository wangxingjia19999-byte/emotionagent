<template>
  <view class="page-container admin-list-page">
    <text class="page-title">订单管理</text>
    <view class="filter-row">
      <view class="filter-chip" :class="{ active: !filter }" @tap="filter=''; loadData()">全部</view>
      <view v-for="(l,k) in statusMap" :key="k" class="filter-chip" :class="{ active: filter===k }" @tap="filter=k; loadData()">{{ l }}</view>
    </view>
    <view class="list-item card" v-for="o in list" :key="o.id">
      <view class="item-main">
        <view class="item-info">
          <text class="item-name">{{ o.order_no?.slice(0,18) }}...</text>
          <text class="order-status" :style="{color: statusColor[o.status]}">{{ statusMap[o.status] }}</text>
        </view>
        <text class="item-price">¥{{ o.total_amount }}</text>
      </view>
      <view class="item-meta">
        <text>{{ o.items?.map(i=>i.product_name).join(', ') }}</text>
      </view>
      <view class="item-actions" v-if="o.status==='paid'">
        <button class="btn-primary small-btn" @tap="updateStatus(o.id, 'shipped')">标记发货</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAdminOrders, updateAdminOrderStatus } from '@/api/admin'

const list = ref([]); const filter = ref('')
const statusMap = { pending_payment:'待支付', paid:'已支付', shipped:'已发货', completed:'已完成', cancelled:'已取消' }
const statusColor = { pending_payment:'#faad14', paid:'#1890ff', shipped:'#7c6ff6', completed:'#52c41a', cancelled:'#8a8fa3' }

onShow(() => loadData())

async function loadData() {
  try { const params = {}; if (filter.value) params.status_filter = filter.value; const res = await getAdminOrders(params); list.value = (res.data || res).items || [] } catch {}
}

async function updateStatus(orderId, status) {
  try { await updateAdminOrderStatus(orderId, status); loadData() } catch {}
}
</script>

<style lang="scss">@import './admin-common.scss'; .order-status { font-size:24rpx; font-weight:600; }</style>
