<template>
  <view class="chat-page">
    <!-- 会话历史面板 -->
    <view class="history-panel" v-if="showHistory">
      <view class="history-header">
        <text class="history-title">历史对话</text>
        <text class="history-close" @tap="showHistory = false">✕</text>
      </view>
      <scroll-view class="history-list" scroll-y>
        <view
          class="history-item"
          v-for="s in sessions"
          :key="s.id"
          @tap="loadSession(s)"
        >
          <text class="history-item-title text-ellipsis">
            {{ s.title || '对话记录' }}
          </text>
          <text class="history-item-time">{{ s.created_at }}</text>
        </view>
        <EmptyState v-if="!sessions.length" title="暂无历史对话" />
      </scroll-view>
      <button class="btn-primary new-chat-btn" @tap="startNewChat">
        开始新对话
      </button>
    </view>

    <!-- 聊天消息列表 -->
    <scroll-view
      class="chat-messages"
      scroll-y
      :scroll-with-animation="true"
      :scroll-into-view="scrollToId"
      @scrolltoupper="loadMoreHistory"
    >
      <view class="messages-inner">
        <view class="welcome-area" v-if="messages.length === 0">
          <view class="welcome-icon">💜</view>
          <text class="welcome-title">心语陪伴</text>
          <text class="welcome-desc">Hi，我在这里陪你聊聊</text>
          <view class="quick-prompts">
            <view class="prompt-chip" @tap="sendQuick('今天心情不太好，想找人聊聊')">
              今天心情不太好
            </view>
            <view class="prompt-chip" @tap="sendQuick('最近睡眠很差，总是失眠')">
              最近睡眠很差
            </view>
            <view class="prompt-chip" @tap="sendQuick('给我推荐一些减压好物')">
              推荐减压好物
            </view>
          </view>
        </view>

        <ChatBubble
          v-for="(msg, idx) in messages"
          :key="idx"
          :message="msg"
          :is-mine="msg.role === 'user'"
          :user-avatar="authStore.userAvatar"
        />

        <!-- AI 正在思考 -->
        <view class="thinking-indicator" v-if="thinking">
          <image class="thinking-avatar" src="/static/tab/chat.png" mode="aspectFill" />
          <view class="thinking-dots">
            <view class="dot"></view>
            <view class="dot"></view>
            <view class="dot"></view>
          </view>
        </view>

        <view :id="'msg-bottom'" style="height: 16rpx"></view>
      </view>
    </scroll-view>

    <!-- 底部输入区 -->
    <view class="chat-input-bar safe-bottom">
      <view class="input-row">
        <view class="input-left">
          <button class="icon-btn" @tap="showHistory = !showHistory">
            <text>📋</text>
          </button>
          <button class="icon-btn" @tap="switchMode">
            <text>{{ modeIcon }}</text>
          </button>
        </view>
        <input
          class="chat-input"
          v-model="inputText"
          placeholder="说说你的心情..."
          placeholder-class="input-placeholder"
          :adjust-position="false"
          confirm-type="send"
          @confirm="handleSend"
        />
        <button
          class="send-btn"
          :class="{ active: inputText.trim() }"
          :disabled="!inputText.trim() || thinking"
          @tap="handleSend"
        >
          <text>↑</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import { onShow, onHide } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { chatWithMultiAgent, getChatSessions, getChatSessionDetail } from '@/api/agent'
import ChatBubble from '@/components/chat-bubble.vue'
import EmptyState from '@/components/empty-state.vue'
import { formatChatTime } from '@/utils/time'

const authStore = useAuthStore()

const messages = ref([])
const inputText = ref('')
const thinking = ref(false)
const scrollToId = ref('')
const showHistory = ref(false)
const sessions = ref([])
const sessionPage = ref(1)
const chatMode = ref('multi') // 'basic', 'enhanced', 'multi' — 默认多 Agent

const modeIcon = computed(() => {
  const map = { basic: '💡', enhanced: '🔮', multi: '🤖' }
  return map[chatMode.value]
})

onShow(() => {
  if (!authStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/auth/login' })
    return
  }
})

async function loadSessions() {
  try {
    const res = await getChatSessions(1, 20)
    const data = res.data || res
    sessions.value = data.items || []
  } catch {
    // 静默
  }
}

async function loadSession(session) {
  try {
    const res = await getChatSessionDetail(session.id)
    const data = res.data || res
    if (data.messages) {
      messages.value = data.messages.map((m) => ({
        role: m.role,
        content: m.content,
        time: formatChatTime(session.created_at),
      }))
      showHistory.value = false
      scrollToBottom()
    }
  } catch {
    // 静默
  }
}

function startNewChat() {
  messages.value = []
  showHistory.value = false
}

function sendQuick(text) {
  inputText.value = text
  handleSend()
}

function switchMode() {
  const modes = ['basic', 'enhanced', 'multi']
  const idx = modes.indexOf(chatMode.value)
  chatMode.value = modes[(idx + 1) % modes.length]
  uni.showToast({
    title: `切换到${modeIcon.value}模式`,
    icon: 'none',
    duration: 1000,
  })
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || thinking.value) return

  // 添加用户消息
  const userMsg = {
    role: 'user',
    content: text,
    time: formatChatTime(new Date().toISOString()),
  }
  messages.value.push(userMsg)
  inputText.value = ''
  scrollToBottom()

  // AI 回复
  thinking.value = true
  try {
    let res
    if (chatMode.value === 'multi') {
      res = await chatWithMultiAgent(text)
    } else if (chatMode.value === 'enhanced') {
      res = await chatWithMultiAgent(text) // 增强模式也用多 Agent
    } else {
      // basic — import 基础 chat
      const { chatWithAgent } = await import('@/api/agent')
      res = await chatWithAgent(text)
    }

    const data = res.data || res
    const reply = data.reply || data.data?.reply || '抱歉，我暂时无法回复'

    // 解析可能的商品推荐（格式: [[PRODUCT:name|price|category]]）
    const products = []
    const productRegex = /\[\[PRODUCT:(.+?)\|(.+?)\|?(.+?)?\]\]/g
    let match
    const cleanReply = reply.replace(productRegex, (m, name, price, cat) => {
      products.push({
        index: String(products.length + 1),
        name,
        price: parseFloat(price) || 0,
        originalPrice: null,
        category: cat || '',
      })
      return ''
    })

    messages.value.push({
      role: 'assistant',
      content: cleanReply.trim() || reply,
      time: formatChatTime(new Date().toISOString()),
      crisisDetected: data.crisis_detected || false,
      products,
      agentUsed: data.agent_used,
    })
  } catch {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，请稍后再试 😢',
      time: formatChatTime(new Date().toISOString()),
    })
  } finally {
    thinking.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    scrollToId.value = 'msg-bottom'
  })
}

function loadMoreHistory() {
  // 预留：可以加载更多历史消息
}
</script>

<style lang="scss" scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: $bg-page;
  position: relative;
}

// 历史面板
.history-panel {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.97);
  z-index: 100;
  display: flex;
  flex-direction: column;
  padding: 24rpx;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 24rpx;
  border-bottom: 1rpx solid $border-light;
}

.history-title {
  font-size: 34rpx;
  font-weight: 600;
  color: $text-primary;
}

.history-close {
  font-size: 36rpx;
  color: $text-muted;
  padding: 8rpx;
}

.history-list {
  flex: 1;
}

.history-item {
  padding: 24rpx 0;
  border-bottom: 1rpx solid $border-light;
}

.history-item-title {
  font-size: 28rpx;
  color: $text-primary;
  display: block;
}

.history-item-time {
  font-size: 24rpx;
  color: $text-muted;
  margin-top: 6rpx;
}

.new-chat-btn {
  height: 80rpx;
  border-radius: $radius-lg;
  margin-top: 16rpx;
  font-size: 28rpx;
}

// 消息列表
.chat-messages {
  flex: 1;
  padding-top: 16rpx;
}

.messages-inner {
  padding-bottom: 24rpx;
}

.welcome-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 48rpx;
}

.welcome-icon {
  font-size: 80rpx;
  margin-bottom: 16rpx;
}

.welcome-title {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 8rpx;
}

.welcome-desc {
  font-size: 28rpx;
  color: $text-muted;
  margin-bottom: 48rpx;
}

.quick-prompts {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  width: 100%;
}

.prompt-chip {
  background: $bg-card;
  border: 1rpx solid $border-color;
  border-radius: $radius-lg;
  padding: 16rpx 24rpx;
  font-size: 28rpx;
  color: $text-secondary;
  text-align: center;

  &:active {
    background: $primary-light;
    border-color: $primary-color;
  }
}

// 思考指示器
.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 0 16rpx;
  margin-bottom: 24rpx;
}

.thinking-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: $primary-light;
}

.thinking-dots {
  display: flex;
  gap: 8rpx;
  padding: 16rpx 24rpx;
  background: $bg-card;
  border-radius: $radius-lg;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: $primary-color;
  opacity: 0.4;
  animation: pulse 1.4s infinite;

  &:nth-child(2) {
    animation-delay: 0.2s;
  }
  &:nth-child(3) {
    animation-delay: 0.4s;
  }
}

@keyframes pulse {
  0%, 80%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

// 输入栏
.chat-input-bar {
  background: $bg-card;
  border-top: 1rpx solid $border-light;
  padding: 12rpx 16rpx;
  padding-bottom: calc(12rpx + $safe-bottom);
}

.input-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.input-left {
  display: flex;
  gap: 8rpx;
}

.icon-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-page;
  border-radius: 50%;
  font-size: 28rpx;
}

.chat-input {
  flex: 1;
  height: 72rpx;
  background: $bg-page;
  border-radius: 36rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: $text-primary;
}

.input-placeholder {
  color: $text-placeholder;
}

.send-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: $border-color;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #fff;
  transition: all 0.2s;

  &.active {
    background: $primary-gradient;
  }
}
</style>
