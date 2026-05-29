<template>
  <div class="ai-chat-page">
    <div class="chat-layout">
      <!-- 左侧：对话区 -->
      <div class="chat-main glass-card">
        <div class="chat-header">
          <span class="chat-header__badge">AI 情绪陪伴</span>
          <h2>慢慢说也没关系</h2>
          <p>有些情绪不需要马上解决，先被看见也很重要。</p>
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
              <div class="chat-bubble__text" v-text="msg.content"></div>
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

      <!-- 右侧：工具与状态面板 -->
      <aside class="chat-sidebar">
        <div class="glass-card sidebar-card">
          <h3>Agent 状态</h3>
          <div class="status-row">
            <span class="status-dot online"></span>
            <span>情绪分析师在线</span>
          </div>
          <div class="status-row">
            <span class="status-label">模型</span>
            <span class="status-value">RAG + MCP 增强</span>
          </div>
          <div class="status-row">
            <span class="status-label">可用工具</span>
            <span class="status-value">{{ toolsCount }} 个</span>
          </div>
          <el-divider />
          <el-button class="config-link" text @click="$router.push('/agent-config')">
            <el-icon><Setting /></el-icon>
            MCP 工具配置
          </el-button>
        </div>

        <div class="glass-card sidebar-card">
          <h3>情绪小贴士</h3>
          <div class="tips-list">
            <div class="tip-item" v-for="tip in tips" :key="tip">
              <el-icon><Sunny /></el-icon>
              <span>{{ tip }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { ChatDotRound, MagicStick, Promotion, Setting, Sunny } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { chatWithEnhancedAgent, getAgentTools } from '@/api/agent'

const inputText = ref('')
const messages = ref([])
const thinking = ref(false)
const messagesContainer = ref(null)
const toolsCount = ref(0)

const quickPrompts = [
  '今天心情不太好，能陪我聊聊吗？',
  '最近压力很大，不知道怎么缓解',
  '我总是控制不住地焦虑，怎么办？',
  '怎么才能更好地接纳自己的情绪？'
]

const tips = [
  '深呼吸可以帮助平静情绪',
  '说出你的感受本身就有疗愈效果',
  '每个人都有情绪低落的时候',
  '适当的运动能改善情绪状态',
  '和朋友倾诉可以减轻心理负担'
]

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

    const res = await chatWithEnhancedAgent(content, userId)
    const reply = res.data?.data?.reply || res.data?.reply || '抱歉，我暂时无法回复，请稍后再试。'
    messages.value.push({ role: 'assistant', content: reply, time: getTime() })
  } catch (e) {
    const errMsg = e.response?.data?.detail || e.message || '请求失败'
    ElMessage.error(errMsg)
    messages.value.push({ role: 'assistant', content: '抱歉，连接出现了问题，请稍后再试。', time: getTime() })
  } finally {
    thinking.value = false
    scrollToBottom()
  }
}

onMounted(async () => {
  try {
    const res = await getAgentTools()
    toolsCount.value = res.data?.data?.length || res.data?.length || 0
  } catch { toolsCount.value = 4 }
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
  display: grid;
  gap: 18px;
  align-content: start;
}

.sidebar-card h3 {
  margin: 0 0 14px;
  font-size: 15px;
  color: #2f3142;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #5f6475;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: none;
}

.status-dot.online {
  background: #43a78d;
  box-shadow: 0 0 0 3px rgba(67, 167, 141, 0.18);
}

.status-label {
  color: #b0b7c4;
  min-width: 56px;
}

.status-value {
  color: #2f3142;
  font-weight: 500;
}

.config-link {
  width: 100%;
  justify-content: center;
  color: #7c6ff6;
}

.tips-list {
  display: grid;
  gap: 10px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #5f6475;
  padding: 8px 12px;
  border-radius: 12px;
  background: #fafbfe;
}

.tip-item .el-icon {
  color: #f0b35b;
  flex: none;
}
</style>
