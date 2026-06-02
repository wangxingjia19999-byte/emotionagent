<template>
  <view class="page-container check-page">
    <!-- 量表选择 -->
    <view class="scale-select" v-if="!currentScale">
      <text class="page-title">每日情绪打卡</text>
      <text class="page-subtitle">选择一份量表，了解自己的情绪状态</text>
      <view class="scale-card card" v-for="s in scales" :key="s.key" @tap="selectScale(s)">
        <text class="scale-name">{{ s.name }}</text>
        <text class="scale-desc">{{ s.description }}</text>
        <text class="scale-count">{{ s.question_count }} 题</text>
      </view>
    </view>

    <!-- 答题 -->
    <view class="scale-questions" v-if="currentScale && !showResult">
      <text class="page-title">{{ currentScale.name }}</text>
      <view class="question-card card" v-for="(q, qi) in questions" :key="qi">
        <text class="q-num">{{ qi + 1 }} / {{ questions.length }}</text>
        <text class="q-text">{{ q.text || q.question || q.title }}</text>
        <view class="options-row">
          <view
            v-for="(opt, oi) in (q.options || [{text:'从不',value:0},{text:'几天',value:1},{text:'一半以上',value:2},{text:'几乎每天',value:3}])"
            :key="oi"
            class="option"
            :class="{ active: answers[qi] === (opt.value ?? oi) }"
            @tap="answers[qi] = (opt.value ?? oi)"
          >
            {{ opt.text || opt.label || opt }}
          </view>
        </view>
      </view>
      <button class="btn-primary btn-full" :disabled="answers.includes(undefined)" @tap="submit">提交</button>
    </view>

    <!-- 结果 -->
    <view class="scale-result" v-if="showResult">
      <view class="result-card card">
        <text class="result-emoji">{{ resultEmoji }}</text>
        <text class="result-title">{{ result.level || result.result_level || '评估完成' }}</text>
        <text class="result-score">得分：{{ result.total_score }} / {{ result.max_score }}</text>
        <text class="result-desc">{{ result.interpretation || '感谢你的评估，继续关注自己的情绪变化哦~' }}</text>
      </view>
      <button class="btn-outline btn-full" @tap="resetScale">再做一次</button>
      <button class="btn-primary btn-full" style="margin-top:16rpx" @tap="goBack">返回</button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { getScales, getScaleDetail, submitQuestionnaire } from '@/api/questionnaire'

const scales = ref([])
const currentScale = ref(null)
const questions = ref([])
const answers = ref([])
const result = ref(null)
const showResult = ref(false)

const resultEmoji = computed(() => {
  const level = (result.value?.result_level || result.value?.level || '').toLowerCase()
  if (level.includes('正常') || level.includes('良好') || level.includes('轻度')) return '😊'
  if (level.includes('中度')) return '😐'
  return '😢'
})

async function loadScales() {
  try {
    const res = await getScales()
    scales.value = (res.data || res) || []
  } catch {}
}

loadScales()

async function selectScale(s) {
  currentScale.value = s
  try {
    const res = await getScaleDetail(s.key)
    const data = res.data || res
    questions.value = data.questions || data.items || []
    answers.value = new Array(questions.value.length).fill(undefined)
  } catch { currentScale.value = null }
}

async function submit() {
  try {
    const res = await submitQuestionnaire({
      scale_type: currentScale.value.key,
      answers: answers.value.map((a) => parseInt(a)),
    })
    result.value = res.data || res
    showResult.value = true
  } catch {}
}

function resetScale() {
  showResult.value = false
  currentScale.value = null
  result.value = null
}

function goBack() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.check-page { padding-bottom: calc(48rpx + $safe-bottom); }
.page-title { font-size: 36rpx; font-weight: 700; color: $text-primary; margin-bottom: 8rpx; display: block; }
.page-subtitle { font-size: 26rpx; color: $text-muted; display: block; margin-bottom: 32rpx; }
.scale-card { margin-bottom: 16rpx; padding: 28rpx; }
.scale-name { font-size: 30rpx; font-weight: 600; color: $text-primary; display: block; }
.scale-desc { font-size: 26rpx; color: $text-secondary; margin-top: 6rpx; display: block; }
.scale-count { font-size: 24rpx; color: $primary-color; margin-top: 8rpx; display: block; }
.question-card { margin-bottom: 16rpx; padding: 28rpx; }
.q-num { font-size: 24rpx; color: $primary-color; margin-bottom: 12rpx; display: block; }
.q-text { font-size: 30rpx; color: $text-primary; line-height: 1.6; margin-bottom: 20rpx; display: block; }
.options-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12rpx; }
.option { padding: 16rpx; text-align: center; background: $bg-page; border-radius: $radius-md; font-size: 26rpx; color: $text-secondary; &.active { background: $primary-light; color: $primary-color; font-weight: 600; } }
.btn-full { width: 100%; height: 88rpx; border-radius: $radius-lg; font-size: 30rpx; margin-top: 32rpx; }
.result-card { padding: 48rpx 32rpx; text-align: center; }
.result-emoji { font-size: 80rpx; display: block; margin-bottom: 16rpx; }
.result-title { font-size: 36rpx; font-weight: 700; color: $text-primary; display: block; margin-bottom: 8rpx; }
.result-score { font-size: 28rpx; color: $text-secondary; display: block; margin-bottom: 16rpx; }
.result-desc { font-size: 28rpx; color: $text-secondary; line-height: 1.7; display: block; }
</style>
