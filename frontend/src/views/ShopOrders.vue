<template>
  <div class="orders-page">
    <section class="orders-header glass-card">
      <div>
        <span class="page-kicker">Orders</span>
        <h1>我的订单</h1>
        <p>看看你的解压好物都到哪了。</p>
      </div>
      <el-button class="orders-header__back" @click="$router.push('/shop')">继续逛逛</el-button>
    </section>

    <section class="orders-tabs glass-card">
      <el-radio-group v-model="activeStatus" @change="fetchOrders">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="pending_payment">待付款</el-radio-button>
        <el-radio-button label="paid">已付款</el-radio-button>
        <el-radio-button label="shipped">已发货</el-radio-button>
        <el-radio-button label="completed">已完成</el-radio-button>
        <el-radio-button label="cancelled">已取消</el-radio-button>
      </el-radio-group>
    </section>

    <section class="orders-list glass-card" v-loading="loading">
      <template v-if="orders.length">
        <div v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-card__header">
            <div>
              <span class="order-card__no">订单号：{{ order.order_no }}</span>
              <span class="order-card__time">{{ order.created_at?.slice(0, 10) }}</span>
            </div>
            <el-tag :type="statusTagType(order.status)" size="small" effect="light">
              {{ statusLabel(order.status) }}
            </el-tag>
          </div>

          <div class="order-card__items">
            <div v-for="item in order.items" :key="item.id" class="order-card__item">
              <div class="order-card__item-img">
                <el-image :src="item.product_image" fit="cover">
                  <template #error>
                    <el-icon :size="24"><Present /></el-icon>
                  </template>
                </el-image>
              </div>
              <span class="order-card__item-name">{{ item.product_name }}</span>
              <span class="order-card__item-qty">×{{ item.quantity }}</span>
              <span class="order-card__item-price">¥{{ item.price }}</span>
            </div>
          </div>

          <div v-if="order.address" class="order-card__address">
            <el-icon><Location /></el-icon>
            {{ order.address.receiver_name }} {{ order.address.phone }}
            {{ order.address.province }}{{ order.address.city }}{{ order.address.district }} {{ order.address.detail }}
          </div>

          <div class="order-card__footer">
            <span>共 {{ order.items?.length || 0 }} 件商品，</span>
            <span class="order-card__total">合计：¥{{ order.total_amount }}</span>
            <div class="order-card__actions">
              <el-button
                v-if="order.status === 'pending_payment'"
                size="small" class="order-card__pay"
                @click="handlePay(order)"
                :loading="payingId === order.id"
              >
                去支付
              </el-button>
              <el-button
                v-if="order.status === 'pending_payment'"
                size="small" class="order-card__cancel"
                @click="handleCancel(order)"
              >
                取消订单
              </el-button>
            </div>
          </div>
        </div>

        <div class="orders-pagination">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20]"
            layout="total, prev, pager, next"
            background
            @size-change="fetchOrders"
            @current-change="fetchOrders"
          />
        </div>
      </template>

      <EmptyState
        v-else
        title="暂无订单"
        description="还没有订单，去商城逛逛吧。"
        action-text="逛逛商城"
        @action="$router.push('/shop')"
      />
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Location, Present } from '@element-plus/icons-vue'
import { getOrders, payOrder, cancelOrder } from '../api/shop'
import EmptyState from '../components/EmptyState.vue'

const loading = ref(false)
const orders = ref([])
const activeStatus = ref('')
const payingId = ref(null)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const STATUS_MAP = {
  pending_payment: '待付款', paid: '已付款', shipped: '已发货',
  completed: '已完成', cancelled: '已取消',
}

function statusLabel(s) { return STATUS_MAP[s] || s }

function statusTagType(s) {
  const map = { pending_payment: 'warning', paid: 'success', shipped: '', completed: 'success', cancelled: 'info' }
  return map[s] || 'info'
}

async function fetchOrders() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (activeStatus.value) params.status = activeStatus.value
    const res = await getOrders(params)
    orders.value = res.data.items || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

async function handlePay(order) {
  payingId.value = order.id
  try {
    await payOrder(order.id)
    ElMessage.success('支付成功')
    fetchOrders()
  } finally { payingId.value = null }
}

async function handleCancel(order) {
  try {
    await ElMessageBox.confirm('确定要取消这个订单吗？', '提示', { type: 'warning' })
  } catch { return }
  await cancelOrder(order.id)
  ElMessage.success('订单已取消')
  fetchOrders()
}

onMounted(() => fetchOrders())
</script>

<style scoped>
.orders-page { display: grid; gap: 16px; }

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

.orders-header {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 14px;
}

.orders-header h1 { margin: 10px 0 0; font-size: 24px; color: #243042; }
.orders-header p { margin: 8px 0 0; color: #6a7281; }

.orders-header__back {
  min-height: 40px; border-radius: 12px;
  border: 1px solid #dbe2ee; background: #ffffff; color: #526073;
}

.orders-tabs { padding: 16px 26px; }

.orders-list { min-height: 300px; }

.order-card {
  border-radius: 18px;
  border: 1px solid #e8ebf3;
  background: #ffffff;
  padding: 20px;
  margin-bottom: 16px;
}

.order-card__header {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 14px; border-bottom: 1px solid #f0f2f7;
}

.order-card__no { font-size: 13px; color: #243042; font-weight: 600; margin-right: 14px; }
.order-card__time { font-size: 12px; color: #a9b1be; }

.order-card__items { padding: 12px 0; }

.order-card__item {
  display: flex; align-items: center; gap: 12px; padding: 8px 0;
}

.order-card__item-img {
  width: 48px; height: 48px; border-radius: 10px;
  overflow: hidden; background: #f4f6fb; flex-shrink: 0;
}

.order-card__item-img :deep(.el-image) { width: 100%; height: 100%; }

.order-card__item-name { flex: 1; font-size: 14px; color: #243042; }
.order-card__item-qty { font-size: 13px; color: #8991a2; }
.order-card__item-price { font-size: 14px; font-weight: 600; color: #243042; width: 70px; text-align: right; }

.order-card__address {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 14px; border-radius: 10px;
  background: #f8f9fc; font-size: 13px; color: #8991a2;
}

.order-card__footer {
  display: flex; align-items: center; justify-content: flex-end;
  gap: 10px; padding-top: 14px; border-top: 1px solid #f0f2f7;
  font-size: 14px; color: #526073;
}

.order-card__total { font-size: 16px; font-weight: 700; color: #6074df; margin-right: auto; }

.order-card__pay {
  border: none; color: #ffffff;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
  border-radius: 10px;
}

.order-card__cancel {
  border: 1px solid #dbe2ee; background: #ffffff; color: #8991a2;
  border-radius: 10px;
}

.orders-pagination { margin-top: 20px; display: flex; justify-content: center; }
</style>
