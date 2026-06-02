<template>
  <view class="page-container cart-page">
    <!-- 购物车列表 -->
    <view class="cart-list" v-if="items.length">
      <view class="cart-item card" v-for="item in items" :key="item.id">
        <image class="cart-img" :src="item.product?.image_url" mode="aspectFill" />
        <view class="cart-info">
          <text class="cart-name text-ellipsis">{{ item.product?.name }}</text>
          <text class="cart-type text-muted">{{ item.product?.product_type === 'physical' ? '实物' : '服务' }}</text>
          <text class="cart-price">¥{{ item.product?.price }}</text>
        </view>
        <view class="cart-qty">
          <button class="qty-btn" @tap="changeQty(item, -1)">−</button>
          <text>{{ item.quantity }}</text>
          <button class="qty-btn" @tap="changeQty(item, 1)">+</button>
        </view>
        <text class="cart-delete" @tap="removeItem(item.id)">🗑️</text>
      </view>
    </view>
    <EmptyState v-else title="购物车是空的" description="去商城逛逛吧" action-text="去逛逛" @action="goShop" />

    <!-- 地址选择 -->
    <view class="address-section card" v-if="showCheckout">
      <text class="section-title">收货地址</text>
      <view v-if="addresses.length">
        <view class="addr-item" v-for="a in addresses" :key="a.id" :class="{ active: selectedAddr === a.id }" @tap="selectedAddr = a.id">
          <text class="addr-name">{{ a.receiver_name }} {{ a.phone }}</text>
          <text class="addr-detail">{{ a.province }}{{ a.city }}{{ a.district }} {{ a.detail }}</text>
        </view>
      </view>
      <button class="btn-ghost" @tap="showAddrForm = true" style="margin-top:16rpx">+ 添加新地址</button>

      <!-- 新增地址表单 -->
      <view v-if="showAddrForm" style="margin-top:16rpx">
        <input v-model="addrForm.receiver_name" placeholder="收件人" class="form-input" />
        <input v-model="addrForm.phone" placeholder="手机号" class="form-input" />
        <input v-model="addrForm.province" placeholder="省" class="form-input" />
        <input v-model="addrForm.city" placeholder="市" class="form-input" />
        <input v-model="addrForm.district" placeholder="区" class="form-input" />
        <input v-model="addrForm.detail" placeholder="详细地址" class="form-input" />
        <button class="btn-primary" style="margin-top:16rpx" @tap="saveAddress">保存地址</button>
      </view>
    </view>

    <!-- 底部结算 -->
    <view class="bottom-bar safe-bottom" v-if="items.length">
      <view class="total-info">
        <text class="total-label">合计：</text>
        <text class="total-price">¥{{ totalAmount.toFixed(2) }}</text>
      </view>
      <button class="btn-primary checkout-btn" @tap="handleBottomAction">
        {{ showCheckout ? '确认下单' : '去结算' }}
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getCart, updateCartItem, removeCartItem, getAddresses, createAddress, createOrder } from '@/api/shop'
import EmptyState from '@/components/empty-state.vue'

const items = ref([])
const addresses = ref([])
const selectedAddr = ref(0)
const showCheckout = ref(false)
const showAddrForm = ref(false)
const addrForm = reactive({ receiver_name: '', phone: '', province: '', city: '', district: '', detail: '' })

const totalAmount = computed(() => items.value.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0))

onShow(async () => { await loadCart(); await loadAddresses() })

async function loadCart() {
  try { const res = await getCart(); items.value = (res.data || res).items || [] } catch {}
}
async function loadAddresses() {
  try { const res = await getAddresses(); const list = (res.data || res) || []; addresses.value = list; selectedAddr.value = list.find((a) => a.is_default)?.id || list[0]?.id || 0 } catch {}
}
async function changeQty(item, delta) {
  const newQty = item.quantity + delta
  if (newQty < 1) return
  try { await updateCartItem(item.id, newQty); item.quantity = newQty } catch {}
}
async function removeItem(itemId) {
  try { await removeCartItem(itemId); loadCart() } catch {}
}
async function saveAddress() {
  try { await createAddress(addrForm); showAddrForm.value = false; Object.assign(addrForm, { receiver_name: '', phone: '', province: '', city: '', district: '', detail: '' }); loadAddresses() } catch {}
}
async function handleCheckout() {
  if (!selectedAddr.value && items.value.some((i) => i.product?.product_type === 'physical')) {
    return uni.showToast({ title: '请选择收货地址', icon: 'none' })
  }
  try {
    await createOrder({ address_id: selectedAddr.value || undefined, payment_method: 'mock' })
    uni.showToast({ title: '下单成功', icon: 'success' })
    showCheckout.value = false
    setTimeout(() => uni.redirectTo({ url: '/pages/subpackages/shop/orders' }), 1000)
  } catch {}
}

function goShop() { uni.navigateTo({ url: '/pages/subpackages/shop/index' }) }

// 底部按钮：点击"去结算"显示地址，点击"确认下单"提交订单
function handleBottomAction() {
  if (showCheckout.value) handleCheckout()
  else showCheckout.value = true
}
</script>

<style lang="scss" scoped>
.cart-page { padding-bottom: calc(140rpx + $safe-bottom); }
.cart-list { margin-bottom: 24rpx; }
.cart-item { display: flex; gap: 16rpx; padding: 16rpx; margin-bottom: 12rpx; align-items: center; }
.cart-img { width: 120rpx; height: 120rpx; border-radius: $radius-md; background: $bg-page; flex-shrink: 0; }
.cart-info { flex: 1; }
.cart-name { font-size: 28rpx; color: $text-primary; display: block; }
.cart-type { font-size: 22rpx; margin-top: 4rpx; }
.cart-price { font-size: 30rpx; font-weight: 600; color: $error-color; margin-top: 8rpx; display: block; }
.cart-qty { display: flex; align-items: center; gap: 12rpx; font-size: 28rpx; }
.qty-btn { width: 48rpx; height: 48rpx; border-radius: 50%; background: $bg-page; display: flex; align-items: center; justify-content: center; font-size: 28rpx; }
.cart-delete { font-size: 32rpx; padding: 8rpx; }
.address-section { margin-bottom: 24rpx; }
.section-title { font-size: 30rpx; font-weight: 600; color: $text-primary; margin-bottom: 16rpx; display: block; }
.addr-item { padding: 20rpx; background: $bg-page; border-radius: $radius-md; margin-bottom: 8rpx; &.active { background: $primary-light; border: 2rpx solid $primary-color; } }
.addr-name { font-size: 28rpx; color: $text-primary; display: block; }
.addr-detail { font-size: 24rpx; color: $text-muted; margin-top: 4rpx; display: block; }
.form-input { width: 100%; height: 72rpx; background: $bg-page; border-radius: $radius-md; padding: 0 16rpx; font-size: 26rpx; margin-bottom: 8rpx; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; justify-content: space-between; align-items: center; padding: 16rpx 24rpx; background: $bg-card; border-top: 1rpx solid $border-light; }
.total-info { display: flex; align-items: baseline; }
.total-label { font-size: 28rpx; color: $text-secondary; }
.total-price { font-size: 40rpx; font-weight: 700; color: $error-color; }
.checkout-btn { height: 80rpx; padding: 0 40rpx; border-radius: $radius-lg; font-size: 28rpx; }
</style>
