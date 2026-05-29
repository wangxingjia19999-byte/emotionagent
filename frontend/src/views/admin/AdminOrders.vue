<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h3>订单管理</h3>
      <el-select v-model="statusFilter" placeholder="按状态筛选" style="width:160px" clearable @change="fetchData">
        <el-option label="待付款" value="pending_payment" />
        <el-option label="已付款" value="paid" />
        <el-option label="已发货" value="shipped" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
    </div>

    <el-table :data="list" stripe style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="order_no" label="订单号" width="180" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column label="金额" width="100">
        <template #default="{ row }">¥{{ row.total_amount }}</template>
      </el-table-column>
      <el-table-column label="商品" min-width="200">
        <template #default="{ row }">
          <span v-for="(item, i) in row.items" :key="i">
            {{ item.product_name }} x{{ item.quantity }}<template v-if="i < row.items.length - 1">, </template>
          </span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="下单时间" width="160" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-select
            :model-value="row.status"
            size="small"
            style="width:130px"
            @change="(val) => doUpdateStatus(row.id, val)"
          >
            <el-option label="待付款" value="pending_payment" />
            <el-option label="已付款" value="paid" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page" :page-size="pageSize" :total="total"
      layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end"
      @current-change="fetchData"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getOrders, updateOrderStatus } from '@/api/admin'

const list = ref([])
const statusFilter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

const statusMap = { pending_payment: '待付款', paid: '已付款', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
const statusTypeMap = { pending_payment: 'warning', paid: 'success', shipped: '', completed: 'info', cancelled: 'danger' }

function statusLabel(s) { return statusMap[s] || s }
function statusType(s) { return statusTypeMap[s] || 'info' }

async function fetchData() {
  const res = await getOrders({ status_filter: statusFilter.value, page: page.value, page_size: pageSize })
  list.value = res.data.items
  total.value = res.data.total
}

async function doUpdateStatus(id, val) {
  try {
    await updateOrderStatus(id, val)
    ElMessage.success('已更新')
    fetchData()
  } catch {}
}

onMounted(fetchData)
</script>

<style scoped>
.admin-page { background: #fff; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.admin-page__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.admin-page__header h3 { margin: 0; font-size: 17px; color: #1a1a2e; }
</style>
