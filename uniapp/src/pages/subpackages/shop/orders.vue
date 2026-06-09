<template>
  <view class="page-container orders-page">
    <!-- 状态筛选 -->
    <scroll-view class="status-tabs" scroll-x :show-scrollbar="false">
      <view class="status-tab" :class="{ active: !filterStatus }" @tap="filterStatus=''; loadOrders()">全部</view>
      <view v-for="(label, key) in ORDER_STATUS_MAP" :key="key" class="status-tab" :class="{ active: filterStatus === key }" @tap="filterStatus=key; loadOrders()">{{ label }}</view>
    </scroll-view>

    <!-- 订单列表 -->
    <view class="order-list">
      <view class="order-card card" v-for="o in orders" :key="o.id">
        <view class="order-header">
          <text class="order-no text-muted">订单号：{{ o.order_no?.slice(0, 16) }}...</text>
          <text class="order-status" :style="{ color: ORDER_STATUS_COLOR[o.status] }">{{ ORDER_STATUS_MAP[o.status] }}</text>
        </view>
        <view class="order-items" v-for="item in o.items" :key="item.id">
          <image class="order-item-img" :src="item.product_image" mode="aspectFill" />
          <view class="order-item-info">
            <text class="order-item-name text-ellipsis">{{ item.product_name }}</text>
            <text class="order-item-price">¥{{ item.price }} × {{ item.quantity }}</text>
          </view>
        </view>
        <view class="order-footer" v-if="o.address">
          <text class="addr-info text-muted">{{ o.address.receiver_name }} {{ o.address.phone }}</text>
        </view>
        <view class="order-footer">
          <text class="total-amount">合计：¥{{ o.total_amount }}</text>
        </view>
        <view class="order-actions" v-if="o.status === 'pending_payment'">
          <button class="btn-ghost small-btn" @tap="cancelOrder(o.id)">取消</button>
          <button class="btn-primary small-btn" @tap="payOrder(o.id)">支付</button>
        </view>
      </view>
      <EmptyState v-if="!orders.length" title="暂无订单" />
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getOrders, cancelOrder as cancelOrd, payOrder as payOrd } from '@/api/shop'
import { ORDER_STATUS_MAP, ORDER_STATUS_COLOR } from '@/utils/constants'
import EmptyState from '@/components/empty-state.vue'

const orders = ref([])
const filterStatus = ref('')

onShow(() => loadOrders())

async function loadOrders() {
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    const res = await getOrders(params)
    orders.value = (res.data || res).items || []
  } catch {}
}

async function cancelOrder(orderId) {
  try { await cancelOrd(orderId); loadOrders() } catch {}
}
async function payOrder(orderId) {
  try { await payOrd(orderId); uni.showToast({ title: '支付成功', icon: 'success' }); loadOrders() } catch {}
}
</script>

<style lang="scss" scoped>
.orders-page { padding-bottom: calc(48rpx + $safe-bottom); }
.status-tabs { white-space: nowrap; margin-bottom: 20rpx; }
.status-tab { display: inline-block; padding: 10rpx 24rpx; font-size: 26rpx; color: $text-secondary; background: $bg-card; border-radius: 32rpx; margin-right: 12rpx; &.active { background: $primary-light; color: $primary-color; } }
.order-card { margin-bottom: 16rpx; padding: 24rpx; }
.order-header { display: flex; justify-content: space-between; margin-bottom: 16rpx; }
.order-no { font-size: 24rpx; }
.order-status { font-size: 26rpx; font-weight: 600; }
.order-items { display: flex; gap: 16rpx; padding: 16rpx 0; border-top: 1rpx solid $border-light; }
.order-item-img { width: 100rpx; height: 100rpx; border-radius: $radius-md; background: $bg-page; flex-shrink: 0; }
.order-item-info { flex: 1; }
.order-item-name { font-size: 28rpx; color: $text-primary; display: block; }
.order-item-price { font-size: 26rpx; color: $text-secondary; margin-top: 4rpx; display: block; }
.order-footer { display: flex; justify-content: space-between; padding-top: 12rpx; }
.addr-info { font-size: 24rpx; }
.total-amount { font-size: 30rpx; font-weight: 600; color: $text-primary; }
.order-actions { display: flex; gap: 12rpx; justify-content: flex-end; margin-top: 16rpx; }
.small-btn { height: 56rpx; padding: 0 24rpx; border-radius: 28rpx; font-size: 24rpx; }
</style>
