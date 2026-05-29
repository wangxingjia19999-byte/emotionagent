<template>
  <div class="chat-bubble" :class="{ mine: isMine }">
    <template v-if="!isMine">
      <el-avatar :size="34" :src="avatar">{{ initial }}</el-avatar>
    </template>
    <div class="chat-bubble__content">
      <div class="chat-bubble__text">{{ message.content }}</div>
      <span class="chat-bubble__time">{{ time }}</span>
    </div>
    <template v-if="isMine">
      <el-avatar :size="34" :src="avatar">{{ initial }}</el-avatar>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: { type: Object, required: true },
  currentUserId: { type: Number, required: true },
  friendAvatar: { type: String, default: '' },
  friendName: { type: String, default: '' },
  myAvatar: { type: String, default: '' },
  myName: { type: String, default: '' },
})

const isMine = computed(() => Number(props.message.sender_id) === Number(props.currentUserId))

const avatar = computed(() => (isMine.value ? props.myAvatar : props.friendAvatar))
const initial = computed(() => {
  const name = isMine.value ? props.myName : props.friendName
  return (name || '?').slice(0, 1)
})

const time = computed(() => {
  const d = new Date(props.message.created_at)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})
</script>

<style scoped>
.chat-bubble {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  max-width: 80%;
}
.chat-bubble.mine {
  align-self: flex-end;
  flex-direction: row-reverse;
}
.chat-bubble__content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.chat-bubble__text {
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}
.mine .chat-bubble__text {
  background: linear-gradient(135deg, #7c6ff6, #9b8eff);
  color: #fff;
  border-bottom-right-radius: 6px;
}
.chat-bubble:not(.mine) .chat-bubble__text {
  background: #f4f5fa;
  color: #2f3142;
  border-bottom-left-radius: 6px;
}
.chat-bubble__time {
  font-size: 11px;
  color: #b0b7c4;
}
.mine .chat-bubble__time { text-align: right; }
</style>
