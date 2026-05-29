<template>
  <div class="shop-page">
    <section class="shop-hero glass-card">
      <div>
        <span class="page-kicker">Shop</span>
        <h1>解压商城</h1>
        <p>挑一件喜欢的小物，给紧绷的生活一个温柔的拥抱。</p>
      </div>
      <div class="shop-hero__actions">
        <el-badge :value="cartCount" :hidden="!cartCount" :offset="[-4, 4]">
          <el-button class="shop-hero__cart-btn" @click="$router.push('/shop/cart')">
            <el-icon><ShoppingCart /></el-icon>
            购物车
          </el-button>
        </el-badge>
        <el-button class="shop-hero__order-btn" @click="$router.push('/shop/orders')">我的订单</el-button>
      </div>
    </section>

    <section class="shop-toolbar glass-card">
      <div class="shop-toolbar__search">
        <el-input v-model="filters.keyword" placeholder="搜索你想要的解压好物" clearable @keyup.enter="search" />
      </div>
      <div class="shop-toolbar__filters">
        <el-radio-group v-model="activeCategory" class="shop-categories" @change="switchCategory">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button v-for="c in categories" :key="c.id" :label="c.id">{{ c.name }}</el-radio-button>
        </el-radio-group>
        <el-select v-model="filters.sort" class="shop-sort" @change="fetchProducts" placeholder="排序">
          <el-option label="默认" value="default" />
          <el-option label="销量优先" value="sales" />
          <el-option label="价格从低到高" value="price_asc" />
          <el-option label="价格从高到低" value="price_desc" />
        </el-select>
      </div>
    </section>

    <section class="shop-content glass-card">
      <el-skeleton v-if="loading" animated :rows="6" />

      <template v-else-if="products.length">
        <div class="shop-grid">
          <div v-for="p in products" :key="p.id" class="shop-card" @click="$router.push(`/shop/${p.id}`)">
            <div class="shop-card__image">
              <el-image :src="p.image_url" fit="cover" lazy>
                <template #error>
                  <div class="shop-card__placeholder">
                    <el-icon :size="40"><Present /></el-icon>
                  </div>
                </template>
              </el-image>
              <span v-if="p.product_type === 'service'" class="shop-card__badge">服务</span>
            </div>
            <div class="shop-card__body">
              <h3>{{ p.name }}</h3>
              <p class="shop-card__desc">{{ p.description.slice(0, 48) }}{{ p.description.length > 48 ? '…' : '' }}</p>
              <div class="shop-card__footer">
                <div class="shop-card__price">
                  <span class="shop-card__current">¥{{ p.price }}</span>
                  <span v-if="p.original_price > p.price" class="shop-card__original">¥{{ p.original_price }}</span>
                </div>
                <div class="shop-card__sales">已售 {{ p.sales_count > 999 ? `${(p.sales_count / 1000).toFixed(1)}k` : p.sales_count }}</div>
              </div>
              <el-button class="shop-card__cart-btn" @click.stop="handleAddCart(p)">
                <el-icon><ShoppingCart /></el-icon>
                加入购物车
              </el-button>
            </div>
          </div>
        </div>

        <div class="shop-pagination">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[12, 24, 48]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="fetchProducts"
            @current-change="fetchProducts"
          />
        </div>
      </template>

      <EmptyState v-else title="暂无商品" description="还没有上架的商品，敬请期待。" />
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Present, ShoppingCart } from '@element-plus/icons-vue'
import { getCategories, getProducts, getCart, addToCart } from '../api/shop'
import EmptyState from '../components/EmptyState.vue'

const router = useRouter()
const loading = ref(false)
const categories = ref([])
const products = ref([])
const activeCategory = ref('')
const cartCount = ref(0)
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

const filters = ref({ keyword: '', sort: 'default' })

async function fetchCategories() {
  const res = await getCategories()
  categories.value = res.data || []
}

async function fetchProducts() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value, sort: filters.value.sort }
    if (activeCategory.value) params.category_id = activeCategory.value
    if (filters.value.keyword) params.keyword = filters.value.keyword
    const res = await getProducts(params)
    products.value = res.data.items || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchCartCount() {
  try {
    const res = await getCart()
    const items = res.data.items || []
    cartCount.value = items.reduce((s, i) => s + i.quantity, 0)
  } catch { cartCount.value = 0 }
}

function switchCategory() {
  page.value = 1
  fetchProducts()
}

function search() {
  page.value = 1
  fetchProducts()
}

async function handleAddCart(product) {
  try {
    await addToCart({ product_id: product.id, quantity: 1 })
    ElMessage.success('已加入购物车')
    fetchCartCount()
  } catch { /* error handled by interceptor */ }
}

onMounted(() => {
  fetchCategories()
  fetchProducts()
  fetchCartCount()
})
</script>

<style scoped>
.shop-page {
  display: grid;
  gap: 16px;
}

.glass-card {
  border-radius: 24px;
  border: 1px solid #e8ebf3;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
  padding: 22px 26px;
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

.shop-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.shop-hero h1 { margin: 10px 0 0; font-size: 24px; color: #243042; }
.shop-hero p { margin: 8px 0 0; color: #6a7281; }

.shop-hero__actions { display: flex; gap: 10px; }

.shop-hero__cart-btn,
.shop-hero__order-btn {
  min-height: 40px;
  border-radius: 12px;
  border: 1px solid #dbe2ee;
  background: #ffffff;
  color: #526073;
}

.shop-hero__cart-btn { display: flex; align-items: center; gap: 6px; }

.shop-toolbar { display: grid; gap: 14px; }

.shop-toolbar__search { max-width: 360px; }

.shop-toolbar__filters {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.shop-categories { flex-wrap: wrap; }

.shop-sort { width: 160px; }

.shop-content { min-height: 320px; }

.shop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
}

.shop-card {
  border-radius: 18px;
  border: 1px solid #e8ebf3;
  background: #ffffff;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.shop-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(44, 52, 73, 0.1);
}

.shop-card__image {
  height: 180px;
  position: relative;
  background: #f4f6fb;
}

.shop-card__image :deep(.el-image) { width: 100%; height: 100%; }

.shop-card__placeholder {
  width: 100%; height: 100%;
  display: grid; place-items: center;
  color: #c0c7d2;
}

.shop-card__badge {
  position: absolute; top: 10px; right: 10px;
  padding: 2px 10px; border-radius: 999px;
  font-size: 11px; color: #ffffff;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
}

.shop-card__body { padding: 14px; display: grid; gap: 8px; }

.shop-card__body h3 {
  margin: 0; font-size: 14px; color: #243042;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.shop-card__desc { margin: 0; font-size: 12px; color: #8991a2; line-height: 1.6; }

.shop-card__footer { display: flex; align-items: center; justify-content: space-between; }

.shop-card__current { font-size: 18px; font-weight: 700; color: #6074df; }

.shop-card__original { margin-left: 6px; font-size: 12px; color: #b8bfcd; text-decoration: line-through; }

.shop-card__sales { font-size: 12px; color: #a9b1be; }

.shop-card__cart-btn {
  width: 100%; min-height: 36px;
  border-radius: 10px; border: 1px solid #d8e1ff;
  background: #edf2ff; color: #6074df;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  font-size: 13px;
}

.shop-card__cart-btn:hover { background: #d8e1ff; }

.shop-pagination { margin-top: 22px; display: flex; justify-content: center; }
</style>
