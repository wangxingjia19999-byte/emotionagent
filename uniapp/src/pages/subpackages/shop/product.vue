<template>
  <view class="page-container product-page">
    <view class="product-detail" v-if="product.id">
      <image class="product-image" :src="product.image_url" mode="aspectFill" />
      <view class="product-info card">
        <text class="product-name">{{ product.name }}</text>
        <view class="price-row">
          <text class="price">¥{{ product.price }}</text>
          <text class="original" v-if="product.original_price && product.original_price > product.price">¥{{ product.original_price }}</text>
          <text class="type-badge" v-if="product.product_type">{{ product.product_type === 'physical' ? '实物' : '服务' }}</text>
        </view>
        <view class="stats">
          <text>已售 {{ product.sales_count || 0 }}</text>
          <text v-if="product.product_type === 'physical'">库存 {{ product.stock || 0 }}</text>
        </view>
        <text class="description-label">商品描述</text>
        <text class="description">{{ product.description || '暂无描述' }}</text>
      </view>

      <!-- 数量选择 -->
      <view class="quantity-row card">
        <text class="qty-label">数量</text>
        <view class="qty-control">
          <button class="qty-btn" @tap="qty = Math.max(1, qty - 1)">−</button>
          <text class="qty-val">{{ qty }}</text>
          <button class="qty-btn" @tap="qty = Math.min(maxQty, qty + 1)">+</button>
        </view>
      </view>
    </view>

    <!-- 底部操作 -->
    <view class="bottom-bar safe-bottom">
      <button class="btn-outline cart-btn" @tap="addToCart">加入购物车</button>
      <button class="btn-primary buy-btn" @tap="buyNow">立即购买</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getProductDetail, addToCart as addCart } from '@/api/shop'

const product = ref({})
const qty = ref(1)
const maxQty = computed(() => product.value.product_type === 'physical' ? Math.min(product.value.stock || 99, 99) : 99)

onLoad(async (options) => {
  if (options.id) {
    try { const res = await getProductDetail(options.id); product.value = (res.data || res) } catch {}
  }
})

async function addToCart() {
  try {
    await addCart({ product_id: product.value.id, quantity: qty.value })
    uni.showToast({ title: '已加入购物车', icon: 'success' })
  } catch {}
}

async function buyNow() {
  try {
    await addCart({ product_id: product.value.id, quantity: qty.value })
    uni.navigateTo({ url: '/pages/subpackages/shop/cart' })
  } catch {}
}
</script>

<style lang="scss" scoped>
.product-page { padding-bottom: calc(140rpx + $safe-bottom); }
.product-image { width: 100%; height: 500rpx; background: $bg-page; }
.product-info { margin: 24rpx 0; padding: 32rpx; }
.product-name { font-size: 36rpx; font-weight: 600; color: $text-primary; display: block; margin-bottom: 16rpx; }
.price-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 12rpx; }
.price { font-size: 44rpx; font-weight: 700; color: $error-color; }
.original { font-size: 28rpx; color: $text-muted; text-decoration: line-through; }
.type-badge { font-size: 22rpx; background: $primary-light; color: $primary-color; padding: 4rpx 12rpx; border-radius: $radius-sm; }
.stats { display: flex; gap: 32rpx; font-size: 24rpx; color: $text-muted; margin-bottom: 20rpx; }
.description-label { font-size: 28rpx; font-weight: 600; color: $text-primary; margin-bottom: 8rpx; display: block; }
.description { font-size: 28rpx; color: $text-secondary; line-height: 1.7; }
.quantity-row { display: flex; justify-content: space-between; align-items: center; padding: 24rpx 32rpx; margin-bottom: 24rpx; }
.qty-label { font-size: 28rpx; color: $text-primary; }
.qty-control { display: flex; align-items: center; gap: 16rpx; }
.qty-btn { width: 56rpx; height: 56rpx; border-radius: 50%; background: $bg-page; display: flex; align-items: center; justify-content: center; font-size: 32rpx; color: $text-secondary; }
.qty-val { font-size: 32rpx; font-weight: 600; color: $text-primary; min-width: 48rpx; text-align: center; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; gap: 16rpx; padding: 16rpx 24rpx; background: $bg-card; border-top: 1rpx solid $border-light; }
.cart-btn { flex: 1; height: 80rpx; border-radius: $radius-lg; font-size: 28rpx; }
.buy-btn { flex: 1; height: 80rpx; border-radius: $radius-lg; font-size: 28rpx; }
</style>
