<template>
  <view class="page-container friends-page">
    <!-- 搜索 -->
    <view class="search-row">
      <input class="search-input" v-model="searchKey" placeholder="搜索用户（账号或昵称）..." confirm-type="search" @confirm="doSearch" />
      <text class="search-icon" @tap="doSearch">🔍</text>
    </view>

    <!-- 好友请求 -->
    <view class="section" v-if="pendingRequests.length">
      <text class="section-title">好友请求 ({{ pendingRequests.length }})</text>
      <view class="request-item" v-for="req in pendingRequests" :key="req.id">
        <image class="req-avatar" :src="req.from_user?.avatar || '/static/tab/profile.png'" mode="aspectFill" />
        <view class="req-info">
          <text class="req-name">{{ req.from_user?.nickname || req.from_user?.username }}</text>
          <text class="req-msg" v-if="req.message">{{ req.message }}</text>
        </view>
        <view class="req-actions">
          <button class="btn-primary small-btn" @tap="handleAccept(req.id)">接受</button>
          <button class="btn-ghost small-btn" @tap="handleReject(req.id)">拒绝</button>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <view class="section" v-if="searchResults.length">
      <text class="section-title">搜索结果</text>
      <view class="user-item" v-for="u in searchResults" :key="u.id">
        <image class="user-avatar" :src="u.avatar || '/static/tab/profile.png'" mode="aspectFill" />
        <view class="user-info">
          <text class="user-name">{{ u.nickname || u.username }}</text>
          <text class="user-account">{{ u.username }}</text>
        </view>
        <button v-if="u.is_friend" class="btn-ghost small-btn" @tap="goPrivateChat(u.id)">发消息</button>
        <button v-else-if="!u.has_pending_request" class="btn-primary small-btn" @tap="sendRequest(u.id)">添加</button>
        <text v-else class="text-muted" style="font-size:26rpx">已发送</text>
      </view>
    </view>

    <!-- 好友列表 -->
    <view class="section">
      <text class="section-title">我的好友 ({{ friends.length }})</text>
      <view class="user-item" v-for="f in friends" :key="f.id">
        <image class="user-avatar" :src="f.avatar || '/static/tab/profile.png'" mode="aspectFill" />
        <view class="user-info">
          <text class="user-name">{{ f.nickname || f.username }}</text>
          <text class="user-account">
            {{ f.occupation || '' }}
            <text v-if="f.unread_count" class="unread-badge">{{ f.unread_count }}</text>
          </text>
        </view>
        <view class="friend-actions">
          <button class="btn-ghost small-btn" @tap="goPrivateChat(f.friend_id)">私聊</button>
          <button class="btn-danger small-btn" @tap="handleDeleteFriend(f.friend_id)">删除</button>
        </view>
      </view>
      <EmptyState v-if="!friends.length && !searchResults.length" title="还没有好友" description="搜索并添加好友吧" />
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { searchFriends, getFriendRequests, acceptFriendRequest, rejectFriendRequest, sendFriendRequest, getFriends, deleteFriend } from '@/api/friends'
import EmptyState from '@/components/empty-state.vue'

const authStore = useAuthStore()
const searchKey = ref('')
const searchResults = ref([])
const pendingRequests = ref([])
const friends = ref([])

onShow(async () => {
  if (!authStore.isLoggedIn) return
  await loadRequests()
  await loadFriends()
})

async function doSearch() {
  if (!searchKey.value.trim()) return
  try {
    const res = await searchFriends(searchKey.value.trim())
    searchResults.value = (res.data || res).items || res.data || []
  } catch {}
}

async function loadRequests() {
  try {
    const res = await getFriendRequests()
    const data = res.data || res
    pendingRequests.value = data.items || data || []
  } catch {}
}

async function loadFriends() {
  try {
    const res = await getFriends()
    const data = res.data || res
    friends.value = data.items || data || []
  } catch {}
}

async function handleAccept(requestId) {
  try { await acceptFriendRequest(requestId); loadRequests(); loadFriends() } catch {}
}
async function handleReject(requestId) {
  try { await rejectFriendRequest(requestId); loadRequests() } catch {}
}
async function sendRequest(userId) {
  try { await sendFriendRequest({ to_user_id: userId }); doSearch() } catch {}
}
async function handleDeleteFriend(friendId) {
  try { await deleteFriend(friendId); loadFriends() } catch {}
}
function goPrivateChat(friendId) {
  uni.navigateTo({ url: `/pages/subpackages/friends/private-chat?friendId=${friendId}` })
}
</script>

<style lang="scss" scoped>
.friends-page { padding-bottom: calc(48rpx + $safe-bottom); }
.search-row { position: relative; margin-bottom: 24rpx; }
.search-input { width: 100%; height: 80rpx; background: $bg-card; border-radius: 40rpx; padding: 0 72rpx 0 28rpx; font-size: 28rpx; box-shadow: $shadow-sm; }
.search-icon { position: absolute; right: 20rpx; top: 50%; transform: translateY(-50%); font-size: 32rpx; }
.section { margin-bottom: 32rpx; }
.section-title { font-size: 30rpx; font-weight: 600; color: $text-primary; margin-bottom: 16rpx; display: block; }
.request-item, .user-item { display: flex; align-items: center; gap: 16rpx; padding: 20rpx; background: $bg-card; border-radius: $radius-lg; margin-bottom: 12rpx; }
.req-avatar, .user-avatar { width: 80rpx; height: 80rpx; border-radius: 50%; background: $primary-light; flex-shrink: 0; }
.req-info, .user-info { flex: 1; }
.req-name, .user-name { font-size: 28rpx; font-weight: 500; color: $text-primary; display: block; }
.req-msg, .user-account { font-size: 24rpx; color: $text-muted; margin-top: 4rpx; display: block; }
.unread-badge { background: $error-color; color: #fff; font-size: 20rpx; padding: 2rpx 10rpx; border-radius: 16rpx; margin-left: 8rpx; }
.req-actions, .friend-actions { display: flex; gap: 8rpx; flex-shrink: 0; }
.small-btn { height: 56rpx; padding: 0 20rpx; font-size: 24rpx; border-radius: 28rpx; }
</style>
