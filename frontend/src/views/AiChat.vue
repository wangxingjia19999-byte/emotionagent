<template>
  <div class="ai-chat-page">
    <div class="chat-layout">
      <!-- 对话区（全宽） -->
      <div class="chat-main glass-card">
        <!-- 头部：标题 + 操作按钮 -->
        <div class="chat-header">
          <div class="chat-header__top">
            <div class="chat-header__info">
              <span class="chat-header__badge">AI 情绪陪伴</span>
              <h2>慢慢说也没关系</h2>
              <p>有些情绪不需要马上解决，先被看见也很重要。</p>
            </div>
            <div class="chat-header__actions">
              <button class="header-btn new-chat-btn" @click="startNewChat">
                <el-icon :size="16"><Plus /></el-icon>
                <span>新建会话</span>
              </button>
              <div class="history-dropdown-wrapper" ref="historyDropdownRef">
                <button
                  class="header-btn history-btn"
                  :class="{ active: showHistoryPanel }"
                  @click="toggleHistoryPanel"
                >
                  <el-icon :size="16"><Clock /></el-icon>
                  <span>历史会话</span>
                  <span v-if="sessions.length" class="history-count">{{ sessions.length }}</span>
                </button>
                <!-- 下拉面板 -->
                <Transition name="dropdown-fade">
                  <div v-if="showHistoryPanel" class="history-dropdown">
                    <div class="history-dropdown__header">
                      <h4>历史会话</h4>
                      <span class="history-dropdown__count">{{ sessions.length }} 个会话</span>
                    </div>
                    <div class="history-dropdown__list" v-if="sessions.length > 0">
                      <div
                        v-for="s in sessions"
                        :key="s.id"
                        class="history-dropdown-item"
                        :class="{ active: activeSessionId === s.id }"
                        @click="loadSession(s.id); showHistoryPanel = false"
                      >
                        <div class="history-dropdown-item__icon">
                          <el-icon :size="16"><ChatDotRound /></el-icon>
                        </div>
                        <div class="history-dropdown-item__info">
                          <div class="history-dropdown-item__title">{{ s.title }}</div>
                          <div class="history-dropdown-item__time">{{ formatSessionTime(s.created_at) }}</div>
                        </div>
                        <div v-if="activeSessionId === s.id" class="history-dropdown-item__badge">当前</div>
                      </div>
                    </div>
                    <div v-else class="history-dropdown__empty">
                      <el-icon :size="32"><ChatDotRound /></el-icon>
                      <p>暂无历史会话</p>
                      <span>开始和心语聊天吧</span>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>
          </div>
          <!-- 查看历史时显示返回条 -->
          <div v-if="activeSessionId !== null" class="history-banner">
            <span>📋 正在查看历史会话</span>
            <button class="back-chat-btn" @click="backToCurrentChat">
              <el-icon :size="14"><Back /></el-icon>
              返回当前对话
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="chat-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="chat-empty">
            <div class="chat-empty__icon">
              <el-icon :size="48"><ChatDotRound /></el-icon>
            </div>
            <p>和我说说今天的心情吧</p>
            <div class="quick-prompts">
              <button
                v-for="prompt in quickPrompts"
                :key="prompt"
                class="quick-prompt-btn"
                @click="sendMessage(prompt)"
              >
                {{ prompt }}
              </button>
            </div>
          </div>

          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="chat-bubble"
            :class="msg.role"
          >
            <div class="chat-bubble__avatar">
              <el-avatar v-if="msg.role === 'user'" :size="36" :src="userAvatar">
                {{ userInitial }}
              </el-avatar>
              <span v-else class="ai-avatar">
                <el-icon :size="20"><MagicStick /></el-icon>
              </span>
            </div>
            <div class="chat-bubble__content">
              <div class="chat-bubble__text">{{ msg.content }}</div>

              <!-- 商品推荐卡片 -->
              <div v-if="msg.products && msg.products.length" class="product-cards">
                <div
                  v-for="p in msg.products"
                  :key="p.index"
                  class="product-mini-card"
                  @click="$router.push('/shop')"
                >
                  <div class="product-mini-card__tag">{{ p.category }}</div>
                  <div class="product-mini-card__name">{{ p.name }}</div>
                  <div class="product-mini-card__price">
                    <strong>¥{{ p.price.toFixed(2) }}</strong>
                    <del v-if="p.originalPrice">¥{{ p.originalPrice.toFixed(2) }}</del>
                  </div>
                  <div class="product-mini-card__action">去商城看看 →</div>
                </div>
              </div>

              <div class="chat-bubble__time">{{ msg.time }}</div>
            </div>
          </div>

          <!-- 思考中 -->
          <div v-if="thinking" class="chat-bubble assistant">
            <div class="chat-bubble__avatar">
              <span class="ai-avatar thinking">
                <el-icon :size="20"><MagicStick /></el-icon>
              </span>
            </div>
            <div class="chat-bubble__content">
              <div class="typing-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat-input-area">
          <div class="chat-input-wrapper">
            <FacialExpressionDetector
              @expression-change="onExpressionChange"
            />
            <textarea
              v-model="inputText"
              class="chat-input"
              placeholder="写下你想说的话..."
              rows="2"
              @keydown.enter.exact.prevent="sendMessage()"
              :disabled="thinking"
            ></textarea>
            <el-button
              class="send-btn"
              type="primary"
              :disabled="!inputText.trim() || thinking"
              @click="sendMessage()"
            >
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
          <p class="chat-disclaimer">AI 陪伴仅供参考，紧急情况请拨打心理援助热线 400-161-9995</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, MagicStick, Promotion, Plus, Clock, Back } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { chatWithMultiAgent, getChatSessions, getChatSessionDetail, getExpressionSuggestion } from '@/api/agent'
import FacialExpressionDetector from '@/components/FacialExpressionDetector.vue'

const router = useRouter()
const inputText = ref('')
const messages = ref([])
const thinking = ref(false)
const messagesContainer = ref(null)
const showHistoryPanel = ref(false)
const historyDropdownRef = ref(null)
const currentExpression = ref(null)  // 摄像头检测到的当前表情

// ── 表情自动建议状态 ──
const exprTrack = {
  label: null,          // 当前跟踪的表情标签
  count: 0,             // 连续检测到同一表情的次数
  threshold: 2,         // 连续多少次后触发建议
  cooldownUntil: 0,     // 冷却期结束时间戳
  cooldownMs: 30000,    // 冷却时长 (30秒)
  lastTriggered: null,  // 上次触发的表情 (避免重复)
}
// 不需要对 neutral 触发的表情列表
const SKIP_SUGGESTION_LABELS = ['neutral']

const quickPrompts = [
  '今天心情不太好，能陪我聊聊吗？',
  '最近压力很大，不知道怎么缓解',
  '我总是控制不住地焦虑，怎么办？',
  '怎么才能更好地接纳自己的情绪？',
  '最近心情有点低落，有什么可以让我开心的东西推荐吗？'
]

// ── 情绪小贴士库（按分类） ──
const tipBank = [
  { text: '深呼吸可以帮助平静情绪', category: 'calm', emoji: '🌿' },
  { text: '说出你的感受本身就有疗愈效果', category: 'calm', emoji: '💬' },
  { text: '每个人都有情绪低落的时候，这很正常', category: 'calm', emoji: '☁️' },
  { text: '尝试 4-7-8 呼吸法：吸气4秒，屏息7秒，呼气8秒', category: 'calm', emoji: '🫁' },
  { text: '闭上眼睛，感受此刻身体与椅子的接触', category: 'calm', emoji: '🧘' },
  { text: '适当的运动能改善情绪状态', category: 'action', emoji: '🏃' },
  { text: '和朋友倾诉可以减轻心理负担', category: 'social', emoji: '🤝' },
  { text: '写日记是整理情绪的好方法', category: 'action', emoji: '📝' },
  { text: '听一首喜欢的歌，让旋律带走烦恼', category: 'action', emoji: '🎵' },
  { text: '去户外散步10分钟，阳光和新鲜空气有帮助', category: 'action', emoji: '☀️' },
  { text: '给自己泡一杯热茶，温暖从手心传到心里', category: 'selfcare', emoji: '🍵' },
  { text: '洗个热水澡，让身体的放松带动心情', category: 'selfcare', emoji: '🛁' },
  { text: '允许自己暂时什么都不做，休息也是一种力量', category: 'selfcare', emoji: '🛋️' },
  { text: '今天做一件让自己开心的小事，哪怕只是吃喜欢的零食', category: 'selfcare', emoji: '🍰' },
  { text: '你不是一个人，社区里有人懂你的感受', category: 'social', emoji: '💙' },
  { text: '给别人一个拥抱，也会温暖自己', category: 'social', emoji: '🫂' },
  { text: '说"不"是保护自己的方式，不需要感到抱歉', category: 'social', emoji: '🛡️' },
  { text: '情绪像波浪，它会来也会走，你只需要等它过去', category: 'calm', emoji: '🌊' },
  { text: '关注当下，而不是陷入"如果……怎么办"的漩涡', category: 'calm', emoji: '🎯' },
  { text: '完成一件小事，比如整理书桌，能带来掌控感', category: 'action', emoji: '✅' },
]

const displayedTips = ref([])

function shuffleTips() {
  const shuffled = [...tipBank].sort(() => Math.random() - 0.5)
  displayedTips.value = shuffled.slice(0, 5)
}

// ── 每日一言 ──
const quotes = [
  { text: '你不必每天都发光，有时候只是存在着就已经很勇敢了', author: '心语' },
  { text: '每一个情绪都值得被看见，每一个你都值得被温柔对待', author: '心语' },
  { text: '裂缝是光照进来的地方，脆弱也是力量的一部分', author: '心语' },
  { text: '你比自己想象的要坚强，也比自己认为的更值得被爱', author: '心语' },
  { text: '慢慢来，不用急着变好。允许自己按照自己的节奏成长', author: '心语' },
  { text: '世界上最温柔的力量，是允许自己不完美', author: '心语' },
  { text: '今天很难，但你已经走到这里了，这本身就是一种胜利', author: '心语' },
  { text: '有时候"我还在"比"我很好"更需要勇气说出来', author: '心语' },
]

const dailyQuote = ref(quotes[Math.floor(Math.random() * quotes.length)])

// ── 呼吸引导 ──
const breathing = ref(false)
const breathePhase = ref('in')
const breatheCount = ref(0)
let breatheTimer = null

// ── 聊天历史 ──
const sessions = ref([])
const activeSessionId = ref(null)
const savedCurrentMessages = ref([])  // 保存当前对话，切换历史时可恢复

async function loadSessions() {
  try {
    const res = await getChatSessions(1, 20)
    const data = res.data?.data || res.data
    sessions.value = data?.items || data || []
  } catch (e) {
    console.error('加载聊天记录失败:', e)
    sessions.value = []
  }
}

async function loadSession(sessionId) {
  try {
    const res = await getChatSessionDetail(sessionId)
    const detail = res.data?.data || res.data
    if (!detail || !detail.messages) {
      console.warn('会话数据为空:', res.data)
      ElMessage.warning('该会话暂无消息')
      return
    }

    // 保存当前对话（如果不在查看历史中）
    if (activeSessionId.value === null && messages.value.length > 0) {
      savedCurrentMessages.value = [...messages.value]
    }

    // 加载历史消息
    messages.value = detail.messages.map((m, i) => ({
      role: m.role,
      content: m.content,
      time: i === 0 ? (detail.created_at || '') : '',
    }))
    activeSessionId.value = sessionId
    await nextTick()
    scrollToBottom()
  } catch (e) {
    console.error('加载历史消息失败:', e)
    ElMessage.error('加载历史消息失败')
  }
}

function backToCurrentChat() {
  if (savedCurrentMessages.value.length > 0) {
    messages.value = [...savedCurrentMessages.value]
    savedCurrentMessages.value = []
  }
  activeSessionId.value = null
}

function startNewChat() {
  savedCurrentMessages.value = []
  messages.value = []
  activeSessionId.value = null
  inputText.value = ''
  showHistoryPanel.value = false
}

function toggleHistoryPanel() {
  showHistoryPanel.value = !showHistoryPanel.value
}

function handleClickOutside(e) {
  if (historyDropdownRef.value && !historyDropdownRef.value.contains(e.target)) {
    showHistoryPanel.value = false
  }
}

function formatSessionTime(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    const now = new Date()
    const diffMs = now - d
    const diffMin = Math.floor(diffMs / 60000)
    const diffHour = Math.floor(diffMs / 3600000)
    const diffDay = Math.floor(diffMs / 86400000)
    if (diffMin < 1) return '刚刚'
    if (diffMin < 60) return `${diffMin} 分钟前`
    if (diffHour < 24) return `${diffHour} 小时前`
    if (diffDay < 7) return `${diffDay} 天前`
    return d.toLocaleDateString('zh-CN')
  } catch { return dateStr }
}

function toggleBreathing() {
  if (breathing.value) {
    stopBreathing()
  } else {
    startBreathing()
  }
}

function startBreathing() {
  breathing.value = true
  breatheCount.value = 0
  breathePhase.value = 'in'
  runBreatheCycle()
}

function stopBreathing() {
  breathing.value = false
  if (breatheTimer) clearTimeout(breatheTimer)
  breatheTimer = null
}

function runBreatheCycle() {
  if (!breathing.value) return
  breathePhase.value = 'in'
  breatheTimer = setTimeout(() => {
    if (!breathing.value) return
    breathePhase.value = 'hold'
    breatheTimer = setTimeout(() => {
      if (!breathing.value) return
      breathePhase.value = 'out'
      breatheTimer = setTimeout(() => {
        if (!breathing.value) return
        breatheCount.value++
        if (breatheCount.value >= 5) {
          stopBreathing()
        } else {
          runBreatheCycle()
        }
      }, 6000)
    }, 2000)
  }, 4000)
}

// ── 解析 AI 回复中的商品信息 ──
function parseProducts(text) {
  const products = []
  // 匹配模式: [数字]. [分类名] 商品名\n     价格: ¥XX.XX (原价 ¥XX.XX)
  const regex = /\s*(\d+)\.\s*\[([^\]]+)\]\s*([^\n]+)\n\s*价格:\s*¥([\d.]+)\s*(?:\(原价\s*¥([\d.]+)\))?/g
  let match
  while ((match = regex.exec(text)) !== null) {
    products.push({
      index: match[1],
      category: match[2],
      name: match[3].trim(),
      price: parseFloat(match[4]),
      originalPrice: match[5] ? parseFloat(match[5]) : null,
    })
  }
  return products
}

// ── 去除 AI 回复中的商品信息，避免重复展示 ──
function cleanProductText(text, products) {
  if (!products.length) return text
  let cleaned = text
  // 移除推荐块标题行及后续商品列表
  cleaned = cleaned.replace(/【为你推荐以下.*?】[\s\S]*$/, '')
  cleaned = cleaned.replace(/={3,}[\s\S]*$/, '')
  // 如果清空后太短，返回原文前部分
  if (cleaned.trim().length < 20) {
    const lines = text.split('\n')
    const usefulLines = []
    for (const line of lines) {
      if (/\s*\d+\.\s*\[/.test(line)) break
      usefulLines.push(line)
    }
    cleaned = usefulLines.join('\n').trim()
  }
  return cleaned
}

const userAvatar = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return u.avatar || ''
  } catch { return '' }
})

const userInitial = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return (u.nickname || u.username || '我').slice(0, 1)
  } catch { return '我' }
})

function getTime() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 面部表情变化回调 (来自 FacialExpressionDetector) — 含自动建议逻辑
async function onExpressionChange(expr) {
  currentExpression.value = expr
  console.log('面部表情更新:', expr?.label_cn, expr?.label)

  if (!expr || !expr.label) return

  const label = expr.label

  // ── 稳定性跟踪 ──
  if (exprTrack.label === label) {
    exprTrack.count++
  } else {
    exprTrack.label = label
    exprTrack.count = 1
  }

  // ── 检查是否应该触发建议 ──
  const now = Date.now()

  // neutral 不触发
  if (SKIP_SUGGESTION_LABELS.includes(label)) {
    exprTrack.lastTriggered = null  // 重置，允许下次触发
    return
  }

  // 冷却期内不触发
  if (now < exprTrack.cooldownUntil) return

  // 同一表情不重复触发 (除非上次触发的不是这个)
  if (exprTrack.lastTriggered === label) return

  // 连续检测次数不够不触发
  if (exprTrack.count < exprTrack.threshold) return

  // 正在思考中不触发
  if (thinking.value) return

  // ── 触发! ──
  console.log(`🎯 表情自动触发: ${expr.label_cn} (连续${exprTrack.count}次)`)

  thinking.value = true
  try {
    const res = await getExpressionSuggestion(label, expr.label_cn)
    const data = res.data?.data || res.data || {}
    const reply = data.reply || ''

    if (reply) {
      // 解析商品推荐
      const products = parseProducts(reply)
      const displayText = products.length ? cleanProductText(reply, products) : reply

      messages.value.push({
        role: 'assistant',
        content: displayText,
        time: getTime(),
        agentUsed: data.agent_used || 'emotion_companion',
        crisisDetected: data.crisis_detected || false,
        expressionTriggered: true,  // 标记为表情触发
        expressionLabel: label,
        products,
      })
      scrollToBottom()
    }

    // 设置冷却和去重
    exprTrack.cooldownUntil = now + exprTrack.cooldownMs
    exprTrack.lastTriggered = label
    exprTrack.label = null
    exprTrack.count = 0
  } catch (e) {
    console.error('表情建议请求失败:', e)
    // 静默处理，不打扰用户
  } finally {
    thinking.value = false
  }
}

async function sendMessage(text) {
  const content = (text || inputText.value).trim()
  if (!content || thinking.value) return

  // 如果在查看历史，先回到当前对话
  if (activeSessionId.value !== null) {
    backToCurrentChat()
  }

  messages.value.push({ role: 'user', content, time: getTime() })
  inputText.value = ''
  scrollToBottom()

  thinking.value = true
  try {
    let userId = null
    try {
      const u = JSON.parse(localStorage.getItem('user') || '{}')
      userId = String(u.id || '')
    } catch { /* ignore */ }

    // 使用多 Agent 端点，自动路由到情绪陪伴或商城推荐
    const res = await chatWithMultiAgent(content, userId)
    const data = res.data?.data || res.data || {}
    const reply = data.reply || '抱歉，我暂时无法回复，请稍后再试。'
    const agentUsed = data.agent_used || 'emotion_companion'
    const crisisDetected = data.crisis_detected || false

    // 解析商品推荐
    const products = parseProducts(reply)
    const displayText = products.length ? cleanProductText(reply, products) : reply

    messages.value.push({
      role: 'assistant',
      content: displayText,
      time: getTime(),
      agentUsed,
      crisisDetected,
      products,  // 解析出的商品列表
    })
  } catch (e) {
    const errMsg = e.response?.data?.detail || e.message || '请求失败'
    ElMessage.error(errMsg)
    messages.value.push({ role: 'assistant', content: '抱歉，连接出现了问题，请稍后再试。', time: getTime() })
  } finally {
    thinking.value = false
    scrollToBottom()
    // 刷新历史列表，清除当前选中（新消息意味着新会话）
    activeSessionId.value = null
    loadSessions()
  }
}

onMounted(() => {
  shuffleTips()
  loadSessions()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.ai-chat-page {
  min-height: auto;
  padding: 0;
}

.chat-layout {
  max-width: 880px;
  margin: 0 auto;
}

.glass-card {
  padding: 24px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 40px rgba(109, 109, 173, 0.1);
}

/* 主聊天区 */
.chat-main {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  min-height: 560px;
  padding: 0;
  overflow: hidden;
}

.chat-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f1f6;
}

.chat-header__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.chat-header__info {
  flex: 1;
  min-width: 0;
}

.chat-header__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: none;
}

.header-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid #e8ebf3;
  border-radius: 10px;
  background: #fff;
  color: #5f6475;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  font-family: inherit;
}

.header-btn:hover {
  background: #f8f6ff;
  border-color: #cbc0ff;
  color: #7c6ff6;
}

.header-btn.active {
  background: #f0edff;
  border-color: #7c6ff6;
  color: #7c6ff6;
}

.new-chat-btn {
  background: linear-gradient(135deg, #7c6ff6, #9b8eff);
  border-color: transparent;
  color: #fff;
}

.new-chat-btn:hover {
  background: linear-gradient(135deg, #6b5fd4, #8b7ef0);
  border-color: transparent;
  color: #fff;
}

.history-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 99px;
  background: #f0edff;
  color: #7c6ff6;
  font-size: 11px;
  font-weight: 600;
}

.history-btn.active .history-count {
  background: #7c6ff6;
  color: #fff;
}

/* 历史会话下拉面板 */
.history-dropdown-wrapper {
  position: relative;
}

.history-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 340px;
  max-height: 420px;
  background: #fff;
  border: 1px solid #e8ebf3;
  border-radius: 16px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12), 0 4px 12px rgba(0, 0, 0, 0.06);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-dropdown__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px 12px;
  border-bottom: 1px solid #f0f1f6;
  flex: none;
}

.history-dropdown__header h4 {
  margin: 0;
  font-size: 15px;
  color: #2f3142;
}

.history-dropdown__count {
  font-size: 12px;
  color: #b0b7c4;
}

.history-dropdown__list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-dropdown__list::-webkit-scrollbar {
  width: 4px;
}

.history-dropdown__list::-webkit-scrollbar-thumb {
  background: #e0e3f0;
  border-radius: 99px;
}

.history-dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
}

.history-dropdown-item:hover {
  background: #f8f6ff;
}

.history-dropdown-item.active {
  background: #f0edff;
}

.history-dropdown-item__icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #f0edff;
  display: grid;
  place-items: center;
  color: #7c6ff6;
  flex: none;
}

.history-dropdown-item.active .history-dropdown-item__icon {
  background: #e0d8ff;
}

.history-dropdown-item__info {
  flex: 1;
  min-width: 0;
}

.history-dropdown-item__title {
  font-size: 13px;
  font-weight: 500;
  color: #2f3142;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-dropdown-item__time {
  font-size: 11px;
  color: #b0b7c4;
  margin-top: 2px;
}

.history-dropdown-item__badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 99px;
  background: #7c6ff6;
  color: #fff;
  flex: none;
}

.history-dropdown__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  color: #b0b7c4;
  gap: 6px;
}

.history-dropdown__empty p {
  margin: 0;
  font-size: 14px;
  color: #7a8191;
}

.history-dropdown__empty span {
  font-size: 12px;
}

/* 下拉面板过渡动画 */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 0.2s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.chat-header__badge {
  display: inline-flex;
  min-height: 28px;
  padding: 0 10px;
  align-items: center;
  border-radius: 999px;
  font-size: 13px;
  color: #7c6ff6;
  background: rgba(124, 111, 246, 0.1);
}

.chat-header h2 {
  margin: 10px 0 0;
  font-size: 18px;
  color: #2f3142;
}

.chat-header p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #7a8191;
}

.history-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding: 8px 12px;
  border-radius: 10px;
  background: #fdf5e6;
  border: 1px solid #f0d9a0;
  font-size: 13px;
  color: #8b6914;
}

.back-chat-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border: 1px solid #e0c870;
  border-radius: 8px;
  background: #fff;
  color: #7c6ff6;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.back-chat-btn:hover {
  background: #f0edff;
  border-color: #7c6ff6;
}

/* 消息区 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.chat-messages::-webkit-scrollbar {
  width: 5px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #e0e3f0;
  border-radius: 99px;
}

.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 40px 20px;
}

.chat-empty__icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f0edff;
  display: grid;
  place-items: center;
  color: #7c6ff6;
}

.chat-empty p {
  color: #7a8191;
  font-size: 15px;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  max-width: 440px;
}

.quick-prompt-btn {
  padding: 8px 16px;
  border: 1px solid #eae6ff;
  border-radius: 99px;
  background: #f8f6ff;
  color: #6b5fd4;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-prompt-btn:hover {
  background: #ece6ff;
  border-color: #cbc0ff;
}

/* 聊天气泡 */
.chat-bubble {
  display: flex;
  gap: 10px;
  max-width: 85%;
}

.chat-bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.chat-bubble.assistant {
  align-self: flex-start;
}

.chat-bubble__avatar {
  flex: none;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, #e8e4ff, #d5ceff);
  display: grid;
  place-items: center;
  color: #7c6ff6;
}

.ai-avatar.thinking {
  animation: pulse-glow 1.6s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(124, 111, 246, 0.25); }
  50% { box-shadow: 0 0 0 8px rgba(124, 111, 246, 0); }
}

.chat-bubble__content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-bubble__text {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.chat-bubble.user .chat-bubble__text {
  background: linear-gradient(135deg, #7c6ff6, #9b8eff);
  color: #fff;
  border-bottom-right-radius: 6px;
}

.chat-bubble.assistant .chat-bubble__text {
  background: #f4f5fa;
  color: #2f3142;
  border-bottom-left-radius: 6px;
}

.chat-bubble__time {
  font-size: 11px;
  color: #b0b7c4;
  padding: 0 4px;
}

.chat-bubble.user .chat-bubble__time {
  text-align: right;
}

/* 打字动画 */
.typing-dots {
  display: flex;
  gap: 5px;
  padding: 12px 16px;
  background: #f4f5fa;
  border-radius: 18px;
  border-bottom-left-radius: 6px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c5bfe6;
  animation: dot-bounce 1.2s ease-in-out infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.15s; }
.typing-dots span:nth-child(3) { animation-delay: 0.3s; }

@keyframes dot-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* 输入区 */
.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid #f0f1f6;
}

.chat-input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  border: 1px solid #e8ebf3;
  border-radius: 16px;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  outline: none;
  background: #fafbfd;
  color: #2f3142;
  font-family: inherit;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #b4a9f0;
  background: #fff;
}

.chat-input::placeholder {
  color: #c0c6d4;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  flex: none;
}

.send-btn:not(:disabled) {
  background: linear-gradient(135deg, #7c6ff6, #9b8eff);
  border-color: transparent;
}

.chat-disclaimer {
  margin: 8px 0 0;
  font-size: 11px;
  color: #c0c6d4;
  text-align: center;
}

/* ── 商品推荐卡片 ── */
.product-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

.product-mini-card {
  background: #fff;
  border: 1px solid #e8e4f6;
  border-radius: 14px;
  padding: 12px 16px;
  width: 200px;
  cursor: pointer;
  transition: all 0.2s;
}

.product-mini-card:hover {
  border-color: #7c6ff6;
  box-shadow: 0 4px 16px rgba(124, 111, 246, 0.12);
  transform: translateY(-2px);
}

.product-mini-card__tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 11px;
  background: #f0edff;
  color: #7c6ff6;
  margin-bottom: 6px;
}

.product-mini-card__name {
  font-size: 13px;
  font-weight: 600;
  color: #2f3142;
  margin-bottom: 4px;
  line-height: 1.4;
}

.product-mini-card__price {
  font-size: 13px;
  color: #e8654a;
  margin-bottom: 6px;
}

.product-mini-card__price del {
  font-size: 11px;
  color: #c0c6d4;
  margin-left: 4px;
}

.product-mini-card__action {
  font-size: 12px;
  color: #7c6ff6;
  font-weight: 500;
}
</style>
