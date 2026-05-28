<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h3>情绪日志</h3>
      <el-input v-model="filterUserId" placeholder="按用户ID筛选" style="width:200px" clearable @change="fetchData" />
    </div>
    <el-table :data="list" stripe style="width:100%" max-height="calc(100vh - 260px)">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column prop="emotion_label" label="情绪标签" width="100" />
      <el-table-column prop="intensity" label="强度" width="80">
        <template #default="{ row }">{{ '●'.repeat(row.intensity) }}{{ '○'.repeat(5 - row.intensity) }}</template>
      </el-table-column>
      <el-table-column prop="raw_text" label="原始文本" min-width="200" />
      <el-table-column prop="suggestion" label="建议" min-width="150" />
      <el-table-column prop="created_at" label="时间" width="160" />
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
import { getEmotionLogs } from '@/api/admin'

const list = ref([])
const filterUserId = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

async function fetchData() {
  const res = await getEmotionLogs({ user_id: filterUserId.value, page: page.value, page_size: pageSize })
  list.value = res.data.items
  total.value = res.data.total
}

onMounted(fetchData)
</script>

<style scoped>
.admin-page { background: #fff; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.admin-page__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.admin-page__header h3 { margin: 0; font-size: 17px; color: #1a1a2e; }
</style>
