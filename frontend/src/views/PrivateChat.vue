<template>
  <div class="chat-page">
    <!-- 左侧好友列表 -->
    <aside class="chat-sidebar glass-card">
      <h3>好友列表</h3>
      <div v-if="friends.length === 0" class="side-empty">暂无好友</div>
      <div
        v-for="f in friends"
        :key="f.friend_id"
        class="side-friend"
        :class="{ active: activeFriendId === f.friend_id }"
        @click="selectFriend(f)"
      >
        <el-avatar :size="40" :src="f.avatar">{{ (f.nickname || f.username || '?').slice(0, 1) }}</el-avatar>
        <div class="side-friend__info">
          <strong>{{ f.nickname || f.username }}</strong>
          <span>{{ f.last_message || '暂无消息' }}</span>
        </div>
        <span v-if="f.unread_count" class="side-badge">{{ f.unread_count }}</span>
      </div>
    </aside>

    <!-- 聊天主区 -->
    <div class="chat-main glass-card" v-if="activeFriend">
      <div class="chat-main__header">
        <el-button text @click="activeFriend = null; activeFriendId = null">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <el-avatar :size="36" :src="activeFriend.avatar">{{ (activeFriend.nickname || '?').slice(0, 1) }}</el-avatar>
        <strong>{{ activeFriend.nickname || activeFriend.username }}</strong>
      </div>

      <div class="chat-messages" ref="msgContainer">
        <div v-if="messages.length === 0" class="chat-empty">开始你们的第一次对话吧</div>
        <ChatBubble
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
          :current-user-id="myId"
          :friend-avatar="activeFriend.avatar"
          :friend-name="activeFriend.nickname || activeFriend.username"
          :my-avatar="myAvatar"
          :my-name="myName"
        />
      </div>

      <div class="chat-input-row">
        <el-input
          v-model="inputText"
          placeholder="输入消息..."
          @keyup.enter.exact="sendMsg"
          :disabled="sending"
        />
        <el-button type="primary" :disabled="!inputText.trim() || sending" @click="sendMsg">发送</el-button>
      </div>
    </div>

    <!-- 未选择好友 -->
    <div class="chat-main glass-card chat-placeholder" v-else>
      <div class="placeholder-content">
        <el-icon :size="48"><ChatDotRound /></el-icon>
        <p>选择一个好友开始聊天</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getFriends } from '@/api/friends'
import { sendMessage, getMessageHistory, markAsRead } from '@/api/privateMessage'
import ChatBubble from '@/components/ChatBubble.vue'

const route = useRoute()

const friends = ref([])
const activeFriend = ref(null)
const activeFriendId = ref(null)
const messages = ref([])
const inputText = ref('')
const sending = ref(false)
const msgContainer = ref(null)
let pollTimer = null

const myId = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || '{}').id || 0 } catch { return 0 }
})
const myAvatar = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || '{}').avatar || '' } catch { return '' }
})
const myName = computed(() => {
  try { const u = JSON.parse(localStorage.getItem('user') || '{}'); return u.nickname || u.username || '' } catch { return '' }
})

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}

async function loadFriends() {
  try {
    const res = await getFriends()
    friends.value = res.data?.items || []
  } catch { /* */ }
}

async function loadMessages(friendId) {
  try {
    const res = await getMessageHistory(friendId)
    messages.value = res.data?.items || []
    scrollToBottom()
    await markAsRead(friendId)
  } catch { /* */ }
}

function selectFriend(friend) {
  activeFriend.value = friend
  activeFriendId.value = friend.friend_id
  loadMessages(friend.friend_id)
}

async function sendMsg() {
  const text = inputText.value.trim()
  if (!text || sending.value || !activeFriendId.value) return
  sending.value = true
  try {
    await sendMessage({ receiver_id: activeFriendId.value, content: text })
    inputText.value = ''
    await loadMessages(activeFriendId.value)
    await loadFriends()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发送失败')
  } finally { sending.value = false }
}

// 轮询刷新消息
function startPolling() {
  pollTimer = setInterval(async () => {
    if (activeFriendId.value) await loadMessages(activeFriendId.value)
    await loadFriends()
  }, 5000)
}

onMounted(async () => {
  await loadFriends()
  startPolling()

  // 从路由参数进入聊天
  const fid = Number(route.query.friend_id)
  if (fid) {
    const f = friends.value.find(x => x.friend_id === fid)
    if (f) selectFriend(f)
  }
})

// 当好友列表加载完成后检查路由参数
watch(() => friends.value.length, () => {
  const fid = Number(route.query.friend_id)
  if (fid && !activeFriendId.value) {
    const f = friends.value.find(x => x.friend_id === fid)
    if (f) selectFriend(f)
  }
})

onBeforeUnmount(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.chat-page { display: grid; grid-template-columns: 260px 1fr; gap: 16px; height: calc(100vh - 120px); min-height: 500px; }

@media (max-width: 750px) {
  .chat-page { grid-template-columns: 1fr; }
  .chat-sidebar { display: none; }
}

.glass-card { border: 1px solid #e8ebf3; border-radius: 22px; background: #fff; box-shadow: 0 14px 30px rgba(44,52,73,0.06); overflow: hidden; }

.chat-sidebar { padding: 18px; overflow-y: auto; display: grid; gap: 6px; align-content: start; }
.chat-sidebar h3 { margin: 0 0 8px; font-size: 15px; color: #243042; }

.side-empty { text-align: center; padding: 24px; color: #b0b7c4; font-size: 13px; }

.side-friend { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 14px; cursor: pointer; transition: background 0.15s; }
.side-friend:hover, .side-friend.active { background: #f0f2fa; }

.side-friend__info { flex: 1; min-width: 0; }
.side-friend__info strong { display: block; font-size: 13px; color: #243042; }
.side-friend__info span { display: block; margin-top: 2px; font-size: 11px; color: #8a90a3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.side-badge { min-width: 18px; height: 18px; border-radius: 99px; background: #ff4d4f; color: #fff; font-size: 11px; display: grid; place-items: center; padding: 0 5px; }

.chat-main { display: flex; flex-direction: column; }
.chat-main__header { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-bottom: 1px solid #f0f1f6; }
.chat-main__header strong { font-size: 15px; color: #243042; }

.chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.chat-empty { text-align: center; padding: 40px; color: #b0b7c4; font-size: 13px; }

.chat-input-row { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid #f0f1f6; }

.chat-placeholder { display: grid; place-items: center; }
.placeholder-content { text-align: center; color: #b0b7c4; }
.placeholder-content p { margin-top: 12px; }
</style>
