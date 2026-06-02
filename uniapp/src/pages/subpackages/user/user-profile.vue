<template>
  <view class="page-container profile-page">
    <view v-if="user.id" class="profile card">
      <image class="avatar" :src="user.avatar || '/static/tab/profile.png'" mode="aspectFill" />
      <text class="name">{{ user.nickname || user.username }}</text>
      <text class="account">账号：{{ user.username }}</text>
      <view class="info-grid" v-if="user.occupation || user.age || user.gender">
        <text v-if="user.occupation" class="info-item">职业：{{ user.occupation }}</text>
        <text v-if="user.age" class="info-item">年龄：{{ user.age }}</text>
        <text v-if="user.gender" class="info-item">性别：{{ genderLabel }}</text>
      </view>
      <text class="self-tag" v-if="user.is_self">这是你的主页</text>
      <button v-if="!user.is_self" class="btn-primary" @tap="sendReq" style="margin-top:24rpx">发送好友请求</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { getUserById } from '@/api/user'
import { sendFriendRequest } from '@/api/friends'

const authStore = useAuthStore()
const user = ref({})
const genderLabels = { male: '男', female: '女', other: '其他' }
const genderLabel = computed(() => genderLabels[user.value.gender] || '')

onLoad(async (options) => {
  if (!options.id) return uni.navigateBack()
  try {
    const res = await getUserById(options.id)
    user.value = (res.data || res)
  } catch {}
})

async function sendReq() {
  try {
    await sendFriendRequest({ to_user_id: user.value.id })
    uni.showToast({ title: '已发送好友请求', icon: 'success' })
  } catch {}
}
</script>

<style lang="scss" scoped>
.profile-page { padding-top: 48rpx; }
.profile { display: flex; flex-direction: column; align-items: center; padding: 48rpx 32rpx; }
.avatar { width: 160rpx; height: 160rpx; border-radius: 50%; margin-bottom: 24rpx; }
.name { font-size: 36rpx; font-weight: 600; color: $text-primary; }
.account { font-size: 26rpx; color: $text-muted; margin-top: 8rpx; }
.info-grid { display: flex; flex-wrap: wrap; gap: 8rpx 24rpx; margin-top: 24rpx; }
.info-item { font-size: 26rpx; color: $text-secondary; }
.self-tag { margin-top: 16rpx; font-size: 24rpx; color: $primary-color; background: $primary-light; padding: 4rpx 16rpx; border-radius: $radius-sm; }
</style>
