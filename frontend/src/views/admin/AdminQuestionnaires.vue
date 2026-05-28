<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h3>问卷记录</h3>
      <div style="display:flex;gap:10px;">
        <el-input v-model="filterUserId" placeholder="按用户ID筛选" style="width:160px" clearable @change="fetchData" />
        <el-select v-model="filterScale" placeholder="量表类型" style="width:160px" clearable @change="fetchData">
          <el-option label="每日快评" value="daily_mood" />
          <el-option label="PHQ-9 抑郁筛查" value="phq9" />
          <el-option label="GAD-7 焦虑筛查" value="gad7" />
        </el-select>
      </div>
    </div>

    <el-table :data="list" stripe style="width:100%" max-height="calc(100vh - 260px)">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column prop="scale_type" label="量表类型" width="140">
        <template #default="{ row }">
          {{ row.scale_type === 'daily_mood' ? '每日快评' : row.scale_type === 'phq9' ? 'PHQ-9' : row.scale_type === 'gad7' ? 'GAD-7' : row.scale_type }}
        </template>
      </el-table-column>
      <el-table-column prop="total_score" label="总分" width="80" />
      <el-table-column prop="result_level" label="等级" width="100">
        <template #default="{ row }">
          <el-tag :type="row.result_level && row.result_level.includes('重') ? 'danger' : row.result_level && row.result_level.includes('中') ? 'warning' : 'info'" size="small">
            {{ row.result_level }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="answers" label="答案" min-width="200">
        <template #default="{ row }">
          <span style="font-size:12px;color:#888;">{{ row.answers }}</span>
        </template>
      </el-table-column>
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
import { getQuestionnaires } from '@/api/admin'

const list = ref([])
const filterUserId = ref('')
const filterScale = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

async function fetchData() {
  const res = await getQuestionnaires({ user_id: filterUserId.value, scale_type: filterScale.value, page: page.value, page_size: pageSize })
  list.value = res.data.items
  total.value = res.data.total
}

onMounted(fetchData)
</script>

<style scoped>
.admin-page { background: #fff; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.admin-page__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; flex-wrap: wrap; gap: 10px; }
.admin-page__header h3 { margin: 0; font-size: 17px; color: #1a1a2e; }
</style>
