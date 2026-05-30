<template>
  <div class="admin-page">
    <div class="page-header">
      <h3>危机预警记录</h3>
      <el-select v-model="riskFilter" placeholder="风险等级筛选" clearable style="width:150px" @change="loadAlerts">
        <el-option label="高风险" value="high" />
        <el-option label="中风险" value="medium" />
        <el-option label="低风险" value="low" />
      </el-select>
    </div>

    <el-table :data="alerts" stripe v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户" width="120" />
      <el-table-column prop="risk_type" label="风险类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.risk_type === 'suicide' ? 'danger' : 'warning'" size="small">
            {{ row.risk_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="risk_level" label="风险等级" width="100">
        <template #default="{ row }">
          <el-tag :type="row.risk_level === 'high' ? 'danger' : row.risk_level === 'medium' ? 'warning' : 'info'" size="small">
            {{ row.risk_level }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="raw_text" label="触发内容" min-width="250" show-overflow-tooltip />
      <el-table-column prop="guidance" label="干预建议" min-width="200" show-overflow-tooltip />
      <el-table-column prop="created_at" label="触发时间" width="180" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-popconfirm title="确定删除该预警记录？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > pageSize"
      style="margin-top:18px;justify-content:flex-end"
      layout="prev, pager, next"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="(p) => { page = p; loadAlerts() }"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getCrisisAlerts, deleteCrisisAlert } from '@/api/admin'

const loading = ref(false)
const alerts = ref([])
const riskFilter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

async function loadAlerts() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (riskFilter.value) params.risk_level = riskFilter.value
    const res = await getCrisisAlerts(params)
    alerts.value = res.data.items
    total.value = res.data.total
  } catch {
    ElMessage.error('加载预警记录失败')
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteCrisisAlert(id)
    ElMessage.success('已删除')
    await loadAlerts()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(loadAlerts)
</script>

<style scoped>
.admin-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.page-header h3 { margin: 0; font-size: 16px; }
</style>
