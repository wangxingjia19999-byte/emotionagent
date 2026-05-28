<template>
  <div class="dashboard">
    <div class="stat-grid">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-card__icon">{{ s.icon }}</div>
        <div class="stat-card__body">
          <div class="stat-card__label">{{ s.label }}</div>
          <div class="stat-card__value">{{ s.value }}</div>
          <div class="stat-card__sub" v-if="s.sub">{{ s.sub }}</div>
        </div>
      </div>
    </div>
    <div v-if="loading" style="text-align:center;padding:60px;color:#999;">加载中...</div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getDashboard } from '@/api/admin'

const loading = ref(true)
const stats = ref([])

onMounted(async () => {
  try {
    const res = await getDashboard()
    const d = res.data
    stats.value = [
      { icon: '👥', label: '用户总数', value: d.users.total, sub: `活跃 ${d.users.active} · 本周新增 ${d.users.new_this_week}` },
      { icon: '📦', label: '商品总数', value: d.shop.total_products, sub: `在售 ${d.shop.on_sale}` },
      { icon: '📋', label: '订单总数', value: d.shop.total_orders, sub: `待处理 ${d.shop.pending_orders} · 今日 ${d.shop.today_orders}` },
      { icon: '💰', label: '营收总额', value: `¥${d.shop.revenue.toFixed(2)}`, sub: '已支付订单累计' },
      { icon: '📝', label: '帖子总数', value: d.community.total_posts, sub: `本周新增 ${d.community.new_this_week}` },
      { icon: '📊', label: '问卷记录', value: d.emotion.total_questionnaires, sub: `本周 ${d.emotion.questionnaires_this_week} 次` },
      { icon: '💭', label: '情绪日志', value: d.emotion.total_emotion_logs, sub: `本周 ${d.emotion.emotion_logs_this_week} 条` },
    ]
  } catch (e) {
    stats.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 22px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-card__icon {
  font-size: 32px;
}

.stat-card__label {
  font-size: 13px;
  color: #999;
  margin-bottom: 6px;
}

.stat-card__value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-card__sub {
  font-size: 12px;
  color: #aaa;
  margin-top: 4px;
}
</style>
