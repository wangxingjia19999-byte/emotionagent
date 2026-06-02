<template>
  <view class="page-container shop-page">
    <!-- 搜索 -->
    <view class="search-row">
      <input class="search-input" v-model="keyword" placeholder="搜索商品..." @confirm="loadProducts" />
    </view>

    <!-- 分类筛选 -->
    <scroll-view class="cat-scroll" scroll-x :show-scrollbar="false">
      <view class="cat-chip" :class="{ active: !activeCat }" @tap="selectCat(0)">全部</view>
      <view class="cat-chip" v-for="c in categories" :key="c.id" :class="{ active: activeCat === c.id }" @tap="selectCat(c.id)">{{ c.name }}</view>
    </scroll-view>

    <!-- 排序 -->
    <view class="sort-row">
      <view class="sort-item" :class="{ active: sortVal === 'default' }" @tap="sortVal='default'; loadProducts()">默认</view>
      <view class="sort-item" :class="{ active: sortVal === 'sales' }" @tap="sortVal='sales'; loadProducts()">销量</view>
      <view class="sort-item" :class="{ active: sortVal === 'price_asc' }" @tap="sortVal='price_asc'; loadProducts()">价格↑</view>
      <view class="sort-item" :class="{ active: sortVal === 'price_desc' }" @tap="sortVal='price_desc'; loadProducts()">价格↓</view>
    </view>

    <!-- 商品列表 -->
    <scroll-view class="product-list" scroll-y @scrolltolower="loadMore">
      <view class="product-grid">
        <view class="product-item card" v-for="p in products" :key="p.id" @tap="goDetail(p.id)">
          <image class="product-img" :src="p.image_url" mode="aspectFill" />
          <view class="product-info">
            <text class="product-name text-ellipsis">{{ p.name }}</text>
            <view class="product-price-row">
              <text class="product-price">¥{{ p.price }}</text>
              <text class="product-original" v-if="p.original_price && p.original_price > p.price">¥{{ p.original_price }}</text>
            </view>
            <text class="product-sales">已售 {{ p.sales_count || 0 }}</text>
          </view>
        </view>
      </view>
      <text class="load-more text-muted" v-if="loading">加载中...</text>
      <text class="load-more text-muted" v-else-if="noMore">— 没有更多了 —</text>
      <EmptyState v-if="!loading && !products.length" title="暂无商品" />
    </scroll-view>

    <!-- 购物车入口 -->
    <view class="cart-fab" @tap="goCart">
      <text>🛒</text>
      <view class="cart-badge" v-if="cartCount > 0">{{ cartCount }}</view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getCategories, getProducts, getCart } from '@/api/shop'
import EmptyState from '@/components/empty-state.vue'

const categories = ref([])
const products = ref([])
const keyword = ref('')
const activeCat = ref(0)
const sortVal = ref('default')
const page = ref(1)
const loading = ref(false)
const noMore = ref(false)
const cartCount = ref(0)

onShow(async () => {
  await Promise.all([loadCategories(), loadProducts(), refreshCart()])
})

async function loadCategories() {
  try { const res = await getCategories(); categories.value = (res.data || res) || [] } catch {}
}

async function loadProducts() {
  loading.value = true; page.value = 1
  try {
    const params = { page: 1, page_size: 10, sort: sortVal.value }
    if (keyword.value) params.keyword = keyword.value
    if (activeCat.value) params.category_id = activeCat.value
    const res = await getProducts(params)
    const data = res.data || res
    products.value = data.items || []
    noMore.value = !data.items?.length
  } catch {} finally { loading.value = false }
}

async function loadMore() {
  if (loading.value || noMore.value) return
  loading.value = true; page.value++
  try {
    const params = { page: page.value, page_size: 10, sort: sortVal.value }
    if (activeCat.value) params.category_id = activeCat.value
    if (keyword.value) params.keyword = keyword.value
    const res = await getProducts(params)
    const items = (res.data || res).items || []
    products.value = [...products.value, ...items]
    noMore.value = !items.length
  } catch { page.value-- } finally { loading.value = false }
}

async function refreshCart() {
  try { const res = await getCart(); cartCount.value = ((res.data || res).items || []).reduce((s, i) => s + i.quantity, 0) } catch {}
}

function selectCat(catId) {
  activeCat.value = catId
  loadProducts()
}

function goDetail(id) { uni.navigateTo({ url: `/pages/subpackages/shop/product?id=${id}` }) }
function goCart() { uni.navigateTo({ url: '/pages/subpackages/shop/cart' }) }
</script>

<style lang="scss" scoped>
.shop-page { padding-bottom: calc(48rpx + $safe-bottom); position: relative; }
.search-row { margin-bottom: 16rpx; }
.search-input { width: 100%; height: 80rpx; background: $bg-card; border-radius: 40rpx; padding: 0 28rpx; font-size: 28rpx; box-shadow: $shadow-sm; }
.cat-scroll { white-space: nowrap; margin-bottom: 16rpx; }
.cat-chip { display: inline-block; padding: 10rpx 24rpx; font-size: 26rpx; color: $text-secondary; background: $bg-card; border-radius: 32rpx; margin-right: 12rpx; &.active { background: $primary-light; color: $primary-color; } }
.sort-row { display: flex; gap: 24rpx; margin-bottom: 16rpx; }
.sort-item { font-size: 26rpx; color: $text-muted; &.active { color: $primary-color; font-weight: 500; } }
.product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16rpx; }
.product-item { padding: 0; overflow: hidden; }
.product-img { width: 100%; height: 320rpx; background: $bg-page; }
.product-info { padding: 16rpx; }
.product-name { font-size: 28rpx; font-weight: 500; color: $text-primary; display: block; }
.product-price-row { display: flex; gap: 8rpx; align-items: baseline; margin-top: 8rpx; }
.product-price { font-size: 32rpx; font-weight: 700; color: $error-color; }
.product-original { font-size: 24rpx; color: $text-muted; text-decoration: line-through; }
.product-sales { font-size: 22rpx; color: $text-muted; margin-top: 4rpx; display: block; }
.load-more { display: flex; justify-content: center; padding: 24rpx; }
.cart-fab { position: fixed; right: 32rpx; bottom: 160rpx; width: 96rpx; height: 96rpx; background: $bg-card; border-radius: 50%; box-shadow: $shadow-lg; display: flex; align-items: center; justify-content: center; font-size: 44rpx; z-index: 50; }
.cart-badge { position: absolute; top: -4rpx; right: -4rpx; background: $error-color; color: #fff; font-size: 20rpx; padding: 2rpx 10rpx; border-radius: 20rpx; min-width: 32rpx; text-align: center; }
</style>
