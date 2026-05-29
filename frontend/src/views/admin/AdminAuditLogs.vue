<template>
  <div class="admin-page">
    <div class="page-header">
      <h3>操作审计日志</h3>
      <div class="header-filters">
        <el-select v-model="actionFilter" placeholder="操作类型" clearable style="width:160px" @change="loadLogs">
          <el-option v-for="a in actions" :key="a" :label="a" :value="a" />
        </el-select>
        <el-input v-model="userIdFilter" placeholder="管理员ID（可选）" clearable style="width:150px" @change="loadLogs" />
      </div>
    </div>

    <el-table :data="logs" stripe v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="admin_name" label="操作人" width="120" />
      <el-table-column prop="action" label="操作类型" width="160">
        <template #default="{ row }">
          <el-tag size="small">{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target_type" label="对象类型" width="100" />
      <el-table-column prop="target_id" label="对象ID" width="80" />
      <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP" width="130" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>

    <el-pagination
      v-if="total > pageSize"
      style="margin-top:18px;justify-content:flex-end"
      layout="prev, pager, next"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="(p) => { page = p; loadLogs() }"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAuditLogs, getAuditActions } from '@/api/admin'

const loading = ref(false)
const logs = ref([])
const actions = ref([])
const actionFilter = ref('')
const userIdFilter = ref('')
const page = ref(1)
const pageSize = 50
const total = ref(0)

async function loadActions() {
  try {
    const res = await getAuditActions()
    actions.value = res.data || []
  } catch { /* ignore */ }
}

async function loadLogs() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (actionFilter.value) params.action = actionFilter.value
    if (userIdFilter.value) params.user_id = parseInt(userIdFilter.value)
    const res = await getAuditLogs(params)
    logs.value = res.data.items
    total.value = res.data.total
  } catch {
    ElMessage.error('加载审计日志失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadActions()
  loadLogs()
})
</script>

<style scoped>
.admin-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.page-header h3 { margin: 0; font-size: 16px; }
.header-filters { display: flex; gap: 10px; }
</style>
