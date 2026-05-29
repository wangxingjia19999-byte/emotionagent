<template>
  <div class="product-page" v-loading="loading">
    <template v-if="product">
      <section class="product-main glass-card">
        <div class="product-main__image">
          <el-image :src="product.image_url" fit="cover">
            <template #error>
              <div class="product-main__placeholder">
                <el-icon :size="60"><Present /></el-icon>
              </div>
            </template>
          </el-image>
        </div>

        <div class="product-main__info">
          <span class="page-kicker">{{ product.product_type === 'service' ? '服务' : '实物' }}</span>
          <h1>{{ product.name }}</h1>

          <div class="product-main__price">
            <span class="product-main__current">¥{{ product.price }}</span>
            <span v-if="product.original_price > product.price" class="product-main__original">¥{{ product.original_price }}</span>
          </div>

          <div class="product-main__stats">
            <span>已售 {{ product.sales_count }}</span>
            <span v-if="product.product_type === 'physical'">库存 {{ product.stock }}</span>
          </div>

          <p class="product-main__desc">{{ product.description }}</p>

          <div v-if="product.product_type === 'physical'" class="product-main__notice">
            <el-icon><InfoFilled /></el-icon>
            下单时需填写收货地址，我们将尽快为您发货
          </div>

          <div class="product-main__actions">
            <el-input-number v-model="quantity" :min="1" :max="product.product_type === 'physical' ? product.stock : 99" />
            <el-button class="product-main__cart" @click="handleAddCart">
              <el-icon><ShoppingCart /></el-icon>
              加入购物车
            </el-button>
            <el-button class="product-main__buy" @click="handleBuyNow">
              立即购买
            </el-button>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { InfoFilled, Present, ShoppingCart } from '@element-plus/icons-vue'
import { getProduct, addToCart, createOrder } from '../api/shop'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const product = ref(null)
const quantity = ref(1)

async function fetchProduct() {
  loading.value = true
  try {
    const res = await getProduct(route.params.id)
    product.value = res.data
  } finally {
    loading.value = false
  }
}

async function handleAddCart() {
  try {
    await addToCart({ product_id: product.value.id, quantity: quantity.value })
    ElMessage.success('已加入购物车')
  } catch { /* error handled by interceptor */ }
}

async function handleBuyNow() {
  // 加入购物车后直接跳转结算
  try {
    await addToCart({ product_id: product.value.id, quantity: quantity.value })
    router.push('/shop/cart')
  } catch { /* error handled by interceptor */ }
}

onMounted(() => fetchProduct())
</script>

<style scoped>
.product-page { min-height: 400px; }

.glass-card {
  border-radius: 24px;
  border: 1px solid #e8ebf3;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
  padding: 26px;
}

.page-kicker {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #6074df;
  background: #edf2ff;
}

.product-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 36px;
  align-items: start;
}

.product-main__image {
  border-radius: 18px;
  overflow: hidden;
  background: #f4f6fb;
  aspect-ratio: 1;
}

.product-main__image :deep(.el-image) { width: 100%; height: 100%; }

.product-main__placeholder {
  width: 100%; height: 100%; min-height: 360px;
  display: grid; place-items: center; color: #c0c7d2;
}

.product-main__info { display: grid; gap: 14px; }

.product-main__info h1 { margin: 0; font-size: 22px; color: #243042; }

.product-main__current { font-size: 28px; font-weight: 700; color: #6074df; }

.product-main__original { margin-left: 8px; font-size: 16px; color: #b8bfcd; text-decoration: line-through; }

.product-main__stats { display: flex; gap: 18px; font-size: 13px; color: #8991a2; }

.product-main__desc { margin: 0; font-size: 14px; color: #526073; line-height: 1.8; }

.product-main__notice {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 16px; border-radius: 12px;
  background: #fff7ed; color: #e6a23c; font-size: 13px;
}

.product-main__actions { display: flex; align-items: center; gap: 12px; padding-top: 8px; }

.product-main__cart {
  min-height: 40px; border-radius: 12px;
  border: 1px solid #d8e1ff; background: #edf2ff; color: #6074df;
  display: flex; align-items: center; gap: 6px;
}

.product-main__buy {
  min-height: 40px; border-radius: 12px;
  border: none; color: #ffffff;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
}

@media (max-width: 860px) {
  .product-main { grid-template-columns: 1fr; }
}
</style>
