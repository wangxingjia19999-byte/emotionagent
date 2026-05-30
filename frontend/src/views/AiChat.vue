<template>
  <div class="ai-chat-page">
    <div class="chat-layout">
      <!-- 左侧：对话区 -->
      <div class="chat-main glass-card">
        <div class="chat-header">
          <span class="chat-header__badge">AI 情绪陪伴</span>
          <h2>慢慢说也没关系</h2>
          <p>有些情绪不需要马上解决，先被看见也很重要。</p>
          <!-- 查看历史时的返回条 -->
          <div v-if="activeSessionId !== null" class="history-banner">
            <span>📋 正在查看历史对话</span>
            <button class="back-chat-btn" @click="backToCurrentChat">
              <el-icon><Back /></el-icon> 返回当前对话
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

      <!-- 右侧：聊天记录 + 小贴士 -->
      <aside class="chat-sidebar">
        <!-- 聊天记录 -->
        <div class="glass-card sidebar-card history-panel">
          <div class="sidebar-card__header">
            <h3>💬 聊天记录</h3>
            <button class="refresh-tips-btn" @click="startNewChat" title="新对话">
              <el-icon><Plus /></el-icon>
            </button>
          </div>
          <div class="history-list" v-if="sessions.length > 0">
            <div
              v-for="s in sessions"
              :key="s.id"
              class="history-item"
              :class="{ active: activeSessionId === s.id }"
              @click="loadSession(s.id)"
            >
              <div class="history-item__title">{{ s.title }}</div>
              <div class="history-item__time">{{ s.created_at }}</div>
            </div>
          </div>
          <div v-else class="history-empty">
            <p>暂无聊天记录</p>
            <p class="history-empty__hint">开始和心语聊天吧</p>
          </div>
        </div>

        <!-- 情绪小贴士卡片 -->
        <div class="glass-card sidebar-card">
          <div class="sidebar-card__header">
            <h3>💡 情绪小贴士</h3>
            <button class="refresh-tips-btn" @click="shuffleTips" title="换一批">
              <el-icon><Refresh /></el-icon>
            </button>
          </div>
          <div class="tips-list">
            <div
              v-for="(tip, i) in displayedTips"
              :key="i"
              class="tip-item"
              :class="'tip-' + tip.category"
            >
              <span class="tip-emoji">{{ tip.emoji }}</span>
              <span>{{ tip.text }}</span>
            </div>
          </div>
        </div>

        <!-- 呼吸引导卡片 -->
        <div class="glass-card sidebar-card breathe-card">
          <h3>🧘 快速放松</h3>
          <p class="breathe-sub">跟着节奏深呼吸</p>
          <div class="breathe-circle" :class="{ inhale: breathePhase === 'in', hold: breathePhase === 'hold', exhale: breathePhase === 'out' }" @click="toggleBreathing">
            <span v-if="!breathing" class="breathe-start">点我开始</span>
            <span v-else class="breathe-text">{{ breathePhase === 'in' ? '吸 气' : breathePhase === 'hold' ? '屏 息' : '呼 气' }}</span>
            <span class="breathe-counter" v-if="breathing">{{ breatheCount }}</span>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, MagicStick, Promotion, Refresh, Plus, Back } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { chatWithMultiAgent, getChatSessions, getChatSessionDetail } from '@/api/agent'

const router = useRouter()
const inputText = ref('')
const messages = ref([])
const thinking = ref(false)
const messagesContainer = ref(null)

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
})
</script>

<style scoped>
.ai-chat-page {
  min-height: auto;
  padding: 0;
}

.chat-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 20px;
  align-items: start;
}

@media (max-width: 900px) {
  .chat-layout {
    grid-template-columns: 1fr;
  }
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

/* 右侧面板 */
.chat-sidebar {
  display: flex;
  flex-direction: column;
  gap: 18px;
  height: calc(100vh - 120px);
  min-height: 560px;
}

.chat-sidebar > .sidebar-card {
  flex: none;
}

.chat-sidebar > .history-panel {
  flex: 1;
  min-height: 200px;
  overflow: hidden;
}

.sidebar-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.sidebar-card__header h3 {
  margin: 0;
  font-size: 15px;
  color: #2f3142;
}

.sidebar-card h3 {
  margin: 0 0 14px;
  font-size: 15px;
  color: #2f3142;
}

/* 聊天记录面板 */
.history-panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-panel .sidebar-card__header {
  flex: none;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  display: grid;
  gap: 4px;
  align-content: start;
}

.history-list::-webkit-scrollbar {
  width: 4px;
}

.history-list::-webkit-scrollbar-thumb {
  background: #e0e3f0;
  border-radius: 99px;
}

.history-item {
  padding: 8px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}

.history-item:hover {
  background: #f8f6ff;
}

.history-item.active {
  background: #f0edff;
  border-color: #d5ceff;
}

.history-item__title {
  font-size: 13px;
  font-weight: 500;
  color: #2f3142;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-item__time {
  font-size: 11px;
  color: #b0b7c4;
  margin-top: 2px;
}

.history-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #b0b7c4;
  font-size: 13px;
  gap: 4px;
}

.history-empty__hint {
  font-size: 12px;
  color: #d0d5e0;
}

.refresh-tips-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #e8ebf3;
  border-radius: 8px;
  background: #fff;
  color: #7c6ff6;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.2s;
}

.refresh-tips-btn:hover {
  background: #f0edff;
  border-color: #7c6ff6;
}

.tips-list {
  display: grid;
  gap: 8px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #5f6475;
  padding: 10px 12px;
  border-radius: 12px;
  line-height: 1.5;
  transition: transform 0.15s;
}

.tip-item:hover {
  transform: translateX(2px);
}

.tip-emoji {
  font-size: 15px;
  flex: none;
  line-height: 1.4;
}

.tip-calm { background: #f0f5ff; }
.tip-action { background: #fff8f0; }
.tip-social { background: #f5f0ff; }
.tip-selfcare { background: #f0fff7; }

/* ── 每日一言卡片 ── */
.daily-quote-card {
  background: linear-gradient(135deg, #fdf6ff, #faf5ff) !important;
  border-color: #e8dcf8 !important;
  text-align: center;
  padding: 20px 18px !important;
}

.quote-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.quote-text {
  font-size: 13px;
  color: #5b4a6b;
  line-height: 1.7;
  margin: 0 0 8px;
}

.quote-author {
  font-size: 12px;
  color: #b0a0c0;
  margin: 0;
}

/* ── 呼吸引导卡片 ── */
.breathe-card {
  text-align: center;
}

.breathe-sub {
  font-size: 12px;
  color: #b0b7c4;
  margin: -8px 0 16px;
}

.breathe-circle {
  width: 100px;
  height: 100px;
  margin: 0 auto;
  border-radius: 50%;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.4s ease;
  background: #f0edff;
  border: 3px solid #e0d8ff;
  position: relative;
}

.breathe-circle.inhale {
  transform: scale(1.25);
  background: #e0d8ff;
  border-color: #b4a0f0;
  box-shadow: 0 0 24px rgba(124, 111, 246, 0.2);
}

.breathe-circle.hold {
  transform: scale(1.25);
  background: #e8e0ff;
  border-color: #c4b0ff;
}

.breathe-circle.exhale {
  transform: scale(0.85);
  background: #f0edff;
  border-color: #d8d0f0;
}

.breathe-start {
  font-size: 13px;
  color: #7c6ff6;
  font-weight: 500;
}

.breathe-text {
  font-size: 14px;
  color: #5b4ab0;
  font-weight: 600;
  letter-spacing: 2px;
}

.breathe-counter {
  position: absolute;
  bottom: 6px;
  right: 14px;
  font-size: 11px;
  color: #b0a0d0;
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
