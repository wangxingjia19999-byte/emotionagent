<template>
  <div class="admin-page">
    <!-- 概览卡片 -->
    <div class="stat-row">
      <div class="stat-card" v-for="s in overviewCards" :key="s.label">
        <div class="stat-card__label">{{ s.label }}</div>
        <div class="stat-card__value">{{ s.value }}</div>
        <div class="stat-card__sub" v-if="s.sub">{{ s.sub }}</div>
      </div>
    </div>

    <!-- 情绪趋势 -->
    <el-card style="margin-top:18px">
      <template #header>
        <div class="card-header">
          <span>情绪分布趋势（近30天）</span>
        </div>
      </template>
      <el-table :data="emotionData" stripe v-loading="emotionLoading" style="width:100%">
        <el-table-column prop="emotion" label="情绪标签" />
        <el-table-column prop="count" label="记录数" />
        <el-table-column prop="percentage" label="占比">
          <template #default="{ row }">
            <el-progress :percentage="row.percentage" :stroke-width="8" />
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!emotionLoading && !emotionData.length" description="暂无情绪数据" />
    </el-card>

    <!-- 用户增长和营收 -->
    <div class="chart-row">
      <el-card style="flex:1">
        <template #header>
          <div class="card-header"><span>用户增长（近30天）</span></div>
        </template>
        <el-table :data="userGrowthData" stripe v-loading="growthLoading" style="width:100%" max-height="400">
          <el-table-column prop="date" label="日期" />
          <el-table-column prop="new_users" label="新增用户" />
        </el-table>
        <el-empty v-if="!growthLoading && !userGrowthData.length" description="暂无数据" />
      </el-card>

      <el-card style="flex:1">
        <template #header>
          <div class="card-header"><span>营收趋势（近30天）</span></div>
        </template>
        <el-table :data="revenueData" stripe v-loading="revenueLoading" style="width:100%" max-height="400">
          <el-table-column prop="date" label="日期" />
          <el-table-column prop="orders" label="订单数" />
          <el-table-column prop="revenue" label="营收">
            <template #default="{ row }">¥{{ row.revenue.toFixed(2) }}</template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!revenueLoading && !revenueData.length" description="暂无数据" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getStatsOverview, getEmotionTrends, getUserGrowth, getRevenueStats } from '@/api/admin'

const overviewCards = ref([])
const emotionData = ref([])
const emotionLoading = ref(false)
const userGrowthData = ref([])
const growthLoading = ref(false)
const revenueData = ref([])
const revenueLoading = ref(false)

async function loadOverview() {
  try {
    const res = await getStatsOverview()
    const d = res.data.this_week
    overviewCards.value = [
      { label: '本周新增用户', value: d.new_users, sub: `较上周 ${d.new_users_vs_last_week >= 0 ? '+' : ''}${d.new_users_vs_last_week}` },
      { label: '本周营收', value: `¥${d.revenue.toFixed(2)}`, sub: '' },
      { label: '高频情绪', value: d.top_emotion, sub: '本周最多记录的情绪' },
      { label: '危机预警', value: d.crisis_alerts, sub: '本周危机预警次数' },
    ]
  } catch { /* ignore */ }
}

async function loadEmotionTrends() {
  emotionLoading.value = true
  try {
    const res = await getEmotionTrends(30)
    emotionData.value = res.data.distribution || []
  } catch { ElMessage.error('加载情绪趋势失败') }
  finally { emotionLoading.value = false }
}

async function loadUserGrowth() {
  growthLoading.value = true
  try {
    const res = await getUserGrowth(30)
    userGrowthData.value = res.data.daily || []
  } catch { ElMessage.error('加载用户增长失败') }
  finally { growthLoading.value = false }
}

async function loadRevenue() {
  revenueLoading.value = true
  try {
    const res = await getRevenueStats(30)
    revenueData.value = res.data.daily || []
  } catch { ElMessage.error('加载营收数据失败') }
  finally { revenueLoading.value = false }
}

onMounted(() => {
  loadOverview()
  loadEmotionTrends()
  loadUserGrowth()
  loadRevenue()
})
</script>

<style scoped>
.admin-page { padding: 0; }
.stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.stat-card { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.stat-card__label { font-size: 13px; color: #999; margin-bottom: 8px; }
.stat-card__value { font-size: 24px; font-weight: 700; color: #1a1a2e; }
.stat-card__sub { font-size: 12px; color: #aaa; margin-top: 4px; }
.card-header { display: flex; align-items: center; font-weight: 600; }
.chart-row { display: flex; gap: 18px; margin-top: 18px; }
</style>
