<template>
  <view class="private-chat-page">
    <scroll-view class="chat-messages" scroll-y :scroll-with-animation="true" :scroll-into-view="scrollToId">
      <view class="messages-inner">
        <ChatBubble
          v-for="(msg, idx) in messages"
          :key="idx"
          :message="msg"
          :is-mine="msg.sender_id === authStore.user?.id"
        />
        <view :id="'msg-bottom'"></view>
      </view>
    </scroll-view>

    <view class="chat-input-bar safe-bottom">
      <input class="msg-input" v-model="inputText" placeholder="发送消息..." confirm-type="send" @confirm="sendMsg" />
      <button class="btn-primary send-btn" :disabled="!inputText.trim()" @tap="sendMsg">发送</button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { onShow, onHide, onLoad } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { getMessageHistory, sendMessage, markMessagesRead } from '@/api/privateMessage'
import { getFriends } from '@/api/friends'
import ChatBubble from '@/components/chat-bubble.vue'
import { formatChatTime } from '@/utils/time'

const authStore = useAuthStore()
const messages = ref([])
const inputText = ref('')
const scrollToId = ref('')
const friendId = ref(0)
const page = ref(1)
let pollTimer = null

onLoad((options) => {
  friendId.value = parseInt(options.friendId) || 0
})

onShow(async () => {
  if (!authStore.isLoggedIn) return
  page.value = 1
  await loadHistory()
  // 轮询新消息
  pollTimer = setInterval(loadNewMessages, 5000)
  markMessagesRead(friendId.value).catch(() => {})
})

onHide(() => {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
})

async function loadHistory() {
  try {
    const res = await getMessageHistory(friendId.value, page.value, 30)
    const data = res.data || res
    const items = (data.items || data || []).map((m) => ({
      ...m,
      time: formatChatTime(m.created_at),
    }))
    messages.value = items.reverse()
    scrollToBottom()
  } catch {}
}

async function loadNewMessages() {
  try {
    const res = await getMessageHistory(friendId.value, 1, 30)
    const data = res.data || res
    const items = (data.items || data || []).map((m) => ({
      ...m,
      time: formatChatTime(m.created_at),
    }))
    const newMsgs = items.filter((m) => !messages.value.find((om) => om.id === m.id))
    if (newMsgs.length) {
      messages.value = [...messages.value, ...newMsgs.reverse()]
      scrollToBottom()
      markMessagesRead(friendId.value).catch(() => {})
    }
  } catch {}
}

async function sendMsg() {
  const text = inputText.value.trim()
  if (!text || !friendId.value) return
  try {
    const res = await sendMessage({ receiver_id: friendId.value, content: text })
    const data = res.data || res
    messages.value.push({ ...data, time: formatChatTime(new Date().toISOString()), sender_id: authStore.user?.id })
    inputText.value = ''
    scrollToBottom()
  } catch {}
}

function scrollToBottom() {
  nextTick(() => { scrollToId.value = 'msg-bottom' })
}
</script>

<style lang="scss" scoped>
.private-chat-page { display: flex; flex-direction: column; height: 100vh; background: $bg-page; }
.chat-messages { flex: 1; padding: 16rpx 0; }
.messages-inner { padding-bottom: 24rpx; }
.chat-input-bar { display: flex; gap: 12rpx; padding: 12rpx 20rpx; background: $bg-card; border-top: 1rpx solid $border-light; align-items: center; padding-bottom: calc(12rpx + $safe-bottom); }
.msg-input { flex: 1; height: 72rpx; background: $bg-page; border-radius: 36rpx; padding: 0 24rpx; font-size: 28rpx; }
.send-btn { height: 72rpx; padding: 0 32rpx; border-radius: 36rpx; font-size: 26rpx; }
</style>
