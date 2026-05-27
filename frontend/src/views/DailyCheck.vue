<template>
  <div class="check-page">
    <!-- 顶部 -->
    <section class="page-hero glass-card">
      <div>
        <span class="page-badge">Daily Check</span>
        <h1>每日情绪打卡</h1>
        <p>花两分钟关照一下自己的情绪，看见本身就是一种疗愈。</p>
      </div>
      <div v-if="todayStatus" class="today-badge">
        <span v-if="todayStatus.all_completed" class="done">今日已完成</span>
        <span v-else>已完成 {{ todayStatus.completed_scales.length }}/{{ todayStatus.total_scales }} 项</span>
      </div>
    </section>

    <!-- 量表选择 + 答题 -->
    <div class="check-layout">
      <div class="check-main">
        <!-- 量表卡片 -->
        <div class="glass-card scale-picker">
          <h3>选择量表</h3>
          <div class="scale-cards">
            <button
              v-for="scale in scales"
              :key="scale.key"
              class="scale-card"
              :class="{ active: activeScale === scale.key }"
              @click="selectScale(scale.key)"
            >
              <span class="scale-card__name">{{ scale.name }}</span>
              <span class="scale-card__desc">{{ scale.description }}</span>
              <span class="scale-card__count">{{ scale.question_count }} 题</span>
            </button>
          </div>
        </div>

        <!-- 答题区 -->
        <div v-if="currentScale && !showResult" class="glass-card question-card">
          <div class="question-header">
            <h3>{{ currentScale.name }}</h3>
            <p>{{ currentScale.instruction }}</p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
          </div>

          <div class="question-list">
            <div v-for="(q, idx) in currentScale.questions" :key="q.id" class="question-item">
              <div class="question-num">{{ idx + 1 }}</div>
              <div class="question-body">
                <p class="question-text">{{ q.text }}</p>
                <div class="question-options">
                  <button
                    v-for="(opt, oi) in (q.options || currentScale.options || ['完全没有', '有几天', '一半以上天数', '几乎每天'])"
                    :key="oi"
                    class="option-btn"
                    :class="{ selected: answers[idx] === oi }"
                    @click="setAnswer(idx, oi)"
                  >
                    {{ opt }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="question-actions">
            <span class="answered-count">{{ answeredCount }}/{{ currentScale.questions.length }} 已答</span>
            <el-button type="primary" :disabled="answeredCount < currentScale.questions.length" :loading="submitting" @click="submitAnswers">
              提交问卷
            </el-button>
          </div>
        </div>

        <!-- 结果展示 -->
        <div v-if="showResult" class="glass-card result-card">
          <div class="result-header">
            <span class="result-badge">{{ result.result_level }}</span>
            <h3>{{ currentScale?.name }} · 测评结果</h3>
          </div>
          <div class="result-score">
            <div class="score-circle" :class="scoreLevelClass">
              <span class="score-num">{{ result.total_score }}</span>
              <span class="score-max">/ {{ result.max_score }}</span>
            </div>
            <p class="result-text">{{ result.interpretation }}</p>
          </div>
          <div class="result-actions">
            <el-button @click="resetQuiz">再做一次</el-button>
            <el-button type="primary" @click="showResult = false; resetQuiz()">换一个量表</el-button>
          </div>
        </div>
      </div>

      <!-- 右侧：历史 + 趋势 -->
      <aside class="check-sidebar">
        <div class="glass-card history-card">
          <div class="history-header">
            <h3>历史记录</h3>
            <el-select v-model="historyFilter" size="small" @change="loadHistory">
              <el-option label="全部" value="" />
              <el-option v-for="s in scales" :key="s.key" :label="s.name" :value="s.key" />
            </el-select>
          </div>

          <div v-if="history.length === 0" class="history-empty">
            <p>暂无问卷记录</p>
          </div>

          <div v-else class="history-list">
            <div v-for="item in history" :key="item.id" class="history-item">
              <div class="history-item__head">
                <span class="history-scale">{{ item.scale_name }}</span>
                <span class="history-level" :class="levelClass(item.result_level)">
                  {{ item.result_level }}
                </span>
              </div>
              <div class="history-item__score">得分 {{ item.total_score }}</div>
              <div class="history-item__time">{{ formatDate(item.created_at) }}</div>
            </div>
            <el-pagination
              v-if="historyTotal > 10"
              v-model:current-page="historyPage"
              :total="historyTotal"
              :page-size="10"
              layout="prev, next"
              small
              @current-change="loadHistory"
            />
          </div>
        </div>

        <!-- 趋势简图 -->
        <div v-if="trends.length >= 2" class="glass-card trend-card">
          <h3>情绪趋势 (近30天)</h3>
          <div class="trend-chart">
            <div
              v-for="(point, idx) in trends"
              :key="idx"
              class="trend-bar-wrapper"
            >
              <div
                class="trend-bar"
                :style="{ height: (point.score / maxTrendScore * 100) + '%' }"
                :class="trendBarClass(point.score)"
                :title="`${point.date} ${point.score}分 ${point.level}`"
              ></div>
              <span v-if="idx % Math.ceil(trends.length / 10) === 0" class="trend-label">{{ point.date }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getScales, getScaleDetail, submitQuestionnaire, getHistory, getTrends, getTodayStatus } from '@/api/questionnaire'

const scales = ref([])
const activeScale = ref('')
const currentScale = ref(null)
const answers = reactive([])
const showResult = ref(false)
const result = ref({})
const submitting = ref(false)
const todayStatus = ref(null)

const history = ref([])
const historyTotal = ref(0)
const historyPage = ref(1)
const historyFilter = ref('')
const trends = ref([])

const answeredCount = computed(() => answers.filter(a => a !== undefined).length)
const progressPercent = computed(() => {
  if (!currentScale.value) return 0
  return Math.round(answeredCount.value / currentScale.value.questions.length * 100)
})

const scoreLevelClass = computed(() => {
  const level = result.value.result_level || ''
  if (level.includes('良好') || level.includes('无')) return 'good'
  if (level.includes('轻')) return 'mild'
  if (level.includes('中')) return 'moderate'
  return 'severe'
})

const maxTrendScore = computed(() => {
  const max = Math.max(...trends.value.map(t => t.score), 1)
  return Math.ceil(max / 5) * 5
})

function levelClass(level) {
  if (!level) return ''
  if (level.includes('良好') || level.includes('无')) return 'level-good'
  if (level.includes('轻')) return 'level-mild'
  if (level.includes('中')) return 'level-moderate'
  return 'level-severe'
}

function trendBarClass(score) {
  if (score <= 3) return 'bar-good'
  if (score <= 8) return 'bar-mild'
  if (score <= 14) return 'bar-moderate'
  return 'bar-severe'
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function setAnswer(idx, value) {
  answers[idx] = value
}

async function selectScale(key) {
  activeScale.value = key
  showResult.value = false
  try {
    const res = await getScaleDetail(key)
    currentScale.value = res.data
    answers.length = 0
    for (let i = 0; i < res.data.questions.length; i++) {
      answers.push(undefined)
    }
  } catch {
    ElMessage.error('加载量表失败')
  }
}

async function submitAnswers() {
  submitting.value = true
  try {
    const res = await submitQuestionnaire({
      scale_type: activeScale.value,
      answers: [...answers]
    })
    result.value = res.data
    showResult.value = true
    ElMessage.success('提交成功')
    loadTodayStatus()
    loadHistory()
    loadTrends()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

function resetQuiz() {
  if (currentScale.value) {
    answers.length = 0
    for (let i = 0; i < currentScale.value.questions.length; i++) {
      answers.push(undefined)
    }
  }
  showResult.value = false
}

async function loadHistory() {
  try {
    const params = { page: historyPage.value, page_size: 10 }
    if (historyFilter.value) params.scale_type = historyFilter.value
    const res = await getHistory(params)
    const data = res.data
    history.value = data.items || []
    historyTotal.value = data.total || 0
  } catch { /* ignore */ }
}

async function loadTrends() {
  try {
    const params = { days: 30 }
    if (historyFilter.value) params.scale_type = historyFilter.value
    const res = await getTrends(params)
    trends.value = res.data || []
  } catch { /* ignore */ }
}

async function loadTodayStatus() {
  try {
    const res = await getTodayStatus()
    todayStatus.value = res.data
  } catch { /* ignore */ }
}

onMounted(async () => {
  try {
    const res = await getScales()
    scales.value = res.data || []
  } catch { /* ignore */ }
  loadHistory()
  loadTrends()
  loadTodayStatus()
})
</script>

<style scoped>
.check-page { display: grid; gap: 18px; }

.glass-card {
  padding: 22px;
  border-radius: 22px;
  border: 1px solid #e8ebf3;
  background: #ffffff;
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.page-badge {
  display: inline-flex;
  min-height: 28px;
  padding: 0 10px;
  align-items: center;
  border-radius: 999px;
  color: #6074df;
  background: #edf2ff;
  font-size: 12px;
}

.page-hero h1 { margin: 10px 0 0; font-size: 24px; color: #243042; }
.page-hero p { margin: 6px 0 0; color: #6a7281; }

.today-badge {
  padding: 8px 16px;
  border-radius: 12px;
  background: #f6ffed;
  color: #52c41a;
  font-size: 13px;
  white-space: nowrap;
}
.today-badge .done { font-weight: 600; }

.check-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 18px;
  align-items: start;
}

@media (max-width: 900px) {
  .check-layout { grid-template-columns: 1fr; }
}

/* 量表选择 */
.scale-picker h3 { margin: 0 0 12px; font-size: 15px; color: #243042; }

.scale-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }

.scale-card {
  padding: 14px;
  border: 1px solid #eef0f6;
  border-radius: 16px;
  background: #fafbfe;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.scale-card:hover { border-color: #d8dff0; }
.scale-card.active { border-color: #b8c4ff; background: #f0f3ff; }

.scale-card__name { font-weight: 600; font-size: 14px; color: #243042; }
.scale-card__desc { font-size: 12px; color: #7a8191; }
.scale-card__count { font-size: 11px; color: #b0b7c4; margin-top: auto; }

@media (max-width: 600px) {
  .scale-cards { grid-template-columns: 1fr; }
}

/* 答题区 */
.question-header h3 { margin: 0; font-size: 16px; color: #243042; }
.question-header p { margin: 4px 0 12px; font-size: 13px; color: #7a8191; }

.progress-bar {
  height: 4px;
  border-radius: 2px;
  background: #eef0f6;
  margin-bottom: 18px;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #7c6ff6, #9b8eff);
  transition: width 0.3s;
}

.question-list { display: grid; gap: 18px; }

.question-item {
  display: flex;
  gap: 12px;
  padding: 14px;
  border-radius: 14px;
  background: #fafbfe;
}

.question-num {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: #edf2ff;
  color: #6074df;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 600;
  flex: none;
}

.question-body { flex: 1; }

.question-text {
  margin: 0 0 10px;
  font-size: 14px;
  color: #2f3142;
  line-height: 1.6;
}

.question-options { display: flex; gap: 8px; flex-wrap: wrap; }

.option-btn {
  padding: 6px 14px;
  border: 1px solid #e0e3f0;
  border-radius: 99px;
  background: #fff;
  color: #5f6475;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.option-btn:hover { border-color: #b8c4ff; color: #6074df; }
.option-btn.selected { border-color: #7c6ff6; background: #f0edff; color: #7c6ff6; font-weight: 500; }

.question-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid #f0f1f6;
}

.answered-count { font-size: 13px; color: #b0b7c4; }

/* 结果 */
.result-header { margin-bottom: 14px; }
.result-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 13px;
  font-weight: 600;
  background: #f0edff;
  color: #7c6ff6;
}

.result-score {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: none;
}

.score-circle.good { background: #f6ffed; color: #52c41a; }
.score-circle.mild { background: #fff7e6; color: #fa8c16; }
.score-circle.moderate { background: #fff1f0; color: #ff4d4f; }
.score-circle.severe { background: #fff0f6; color: #cf1322; }

.score-num { font-size: 28px; font-weight: 700; }
.score-max { font-size: 12px; opacity: 0.7; }

.result-text { flex: 1; margin: 0; font-size: 14px; color: #5f6475; line-height: 1.8; }
.result-actions { margin-top: 16px; display: flex; gap: 10px; }

/* 历史 */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-header h3 { margin: 0; font-size: 15px; color: #243042; }

.history-empty { text-align: center; padding: 24px; color: #b0b7c4; font-size: 13px; }

.history-list { display: grid; gap: 8px; }

.history-item {
  padding: 10px 14px;
  border-radius: 12px;
  background: #fafbfe;
  font-size: 13px;
}

.history-item__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-scale { color: #243042; font-weight: 500; }
.history-level { font-size: 11px; padding: 2px 8px; border-radius: 99px; }

.level-good { background: #f6ffed; color: #52c41a; }
.level-mild { background: #fff7e6; color: #fa8c16; }
.level-moderate { background: #fff1f0; color: #ff4d4f; }
.level-severe { background: #fff0f6; color: #cf1322; }

.history-item__score { color: #7a8191; margin-top: 2px; }
.history-item__time { color: #b0b7c4; font-size: 11px; margin-top: 2px; }

/* 趋势图 */
.trend-card h3 { margin: 0 0 12px; font-size: 15px; color: #243042; }

.trend-chart {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 100px;
  padding-bottom: 16px;
  position: relative;
}

.trend-bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}

.trend-bar {
  width: 100%;
  max-width: 20px;
  border-radius: 4px 4px 0 0;
  min-height: 2px;
  transition: height 0.3s;
}

.bar-good { background: #b7eb8f; }
.bar-mild { background: #ffd591; }
.bar-moderate { background: #ffa39e; }
.bar-severe { background: #ff7875; }

.trend-label {
  font-size: 9px;
  color: #b0b7c4;
  margin-top: 4px;
  white-space: nowrap;
}
</style>
