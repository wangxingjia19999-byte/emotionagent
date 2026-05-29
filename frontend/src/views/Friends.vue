<template>
  <div class="friends-page">
    <!-- 搜索 -->
    <section class="glass-card search-card">
      <div class="search-row">
        <el-input v-model="searchQuery" placeholder="搜索用户（用户名或昵称）" clearable @keyup.enter="doSearch">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="doSearch" :loading="searching">搜索</el-button>
      </div>
      <div v-if="searchResults.length" class="search-results">
        <div v-for="user in searchResults" :key="user.id" class="user-row">
          <div class="user-row__info" @click="$router.push(`/users/${user.id}`)">
            <el-avatar :size="40" :src="user.avatar">{{ (user.nickname || user.username || '?').slice(0, 1) }}</el-avatar>
            <div>
              <strong>{{ user.nickname || user.username }}</strong>
              <span v-if="user.occupation">{{ user.occupation }}</span>
            </div>
          </div>
          <div class="user-row__actions">
            <el-tag v-if="user.is_friend" type="success" size="small">已是好友</el-tag>
            <el-tag v-else-if="user.has_pending_request" type="warning" size="small">已申请</el-tag>
            <el-button v-else size="small" type="primary" @click="sendRequest(user.id)">添加好友</el-button>
          </div>
        </div>
      </div>
    </section>

    <div class="friends-layout">
      <!-- 好友申请 -->
      <div class="glass-card requests-card" v-if="requests.length">
        <h3>好友申请 <span class="badge">{{ requests.length }}</span></h3>
        <div v-for="req in requests" :key="req.id" class="request-item">
          <div class="request-item__info" @click="$router.push(`/users/${req.from_user_id}`)">
            <el-avatar :size="40" :src="req.from_user?.avatar">{{ (req.from_user?.nickname || '?').slice(0, 1) }}</el-avatar>
            <div>
              <strong>{{ req.from_user?.nickname || req.from_user?.username }}</strong>
              <span v-if="req.message">{{ req.message }}</span>
            </div>
          </div>
          <div class="request-item__actions">
            <el-button size="small" type="primary" @click="handleAccept(req.id)">同意</el-button>
            <el-button size="small" @click="handleReject(req.id)">拒绝</el-button>
          </div>
        </div>
      </div>

      <!-- 好友列表 -->
      <div class="glass-card friends-card">
        <h3>我的好友 <span class="count">({{ friends.length }})</span></h3>
        <div v-if="friends.length === 0" class="empty">暂无好友，快去搜索并添加朋友吧。</div>
        <div v-else class="friend-list">
          <div v-for="f in friends" :key="f.friend_id" class="friend-item" @click="goChat(f.friend_id)">
            <el-avatar :size="44" :src="f.avatar">{{ (f.nickname || f.username || '?').slice(0, 1) }}</el-avatar>
            <div class="friend-item__info">
              <div class="friend-item__name">
                <strong>{{ f.nickname || f.username }}</strong>
                <span v-if="f.unread_count" class="unread">{{ f.unread_count }}</span>
              </div>
              <span class="friend-item__last">{{ f.last_message || '暂无消息' }}</span>
            </div>
            <el-popconfirm title="确定删除该好友？" @confirm="handleRemove(f.friend_id)">
              <template #reference>
                <el-button text type="danger" size="small" @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { searchUsers, sendFriendRequest, getFriendRequests, acceptRequest, rejectRequest, getFriends, removeFriend } from '@/api/friends'

const router = useRouter()
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const requests = ref([])
const friends = ref([])

async function doSearch() {
  const q = searchQuery.value.trim()
  if (!q) return
  searching.value = true
  try {
    const res = await searchUsers(q)
    searchResults.value = res.data || []
    if (!searchResults.value.length) ElMessage.info('未找到用户')
  } catch {
    ElMessage.error('搜索失败')
  } finally { searching.value = false }
}

async function sendRequest(userId) {
  try {
    await sendFriendRequest({ to_user_id: userId })
    ElMessage.success('好友申请已发送')
    doSearch()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发送失败')
  }
}

async function loadRequests() {
  try {
    const res = await getFriendRequests()
    requests.value = res.data?.items || []
  } catch { /* ignore */ }
}

async function handleAccept(id) {
  try {
    await acceptRequest(id)
    ElMessage.success('已同意')
    loadRequests(); loadFriends()
  } catch { ElMessage.error('操作失败') }
}

async function handleReject(id) {
  try {
    await rejectRequest(id)
    ElMessage.success('已拒绝')
    loadRequests()
  } catch { ElMessage.error('操作失败') }
}

async function loadFriends() {
  try {
    const res = await getFriends()
    friends.value = res.data?.items || []
  } catch { /* ignore */ }
}

async function handleRemove(friendId) {
  try {
    await removeFriend(friendId)
    ElMessage.success('已删除')
    loadFriends()
  } catch { ElMessage.error('删除失败') }
}

function goChat(friendId) {
  router.push({ path: '/private-chat', query: { friend_id: String(friendId) } })
}

onMounted(() => { loadRequests(); loadFriends() })
</script>

<style scoped>
.friends-page { display: grid; gap: 16px; }
.glass-card { padding: 20px; border-radius: 22px; border: 1px solid #e8ebf3; background: #fff; box-shadow: 0 14px 30px rgba(44,52,73,0.06); }

.search-row { display: flex; gap: 10px; }
.search-results { margin-top: 12px; display: grid; gap: 8px; }

.user-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border-radius: 14px; background: #fafbfe; }
.user-row__info { display: flex; gap: 10px; align-items: center; cursor: pointer; flex: 1; }
.user-row__info strong { display: block; font-size: 14px; color: #243042; }
.user-row__info span { font-size: 12px; color: #8a90a3; }

.friends-layout { display: grid; grid-template-columns: 1fr 2fr; gap: 16px; align-items: start; }
@media (max-width: 800px) { .friends-layout { grid-template-columns: 1fr; } }

.requests-card h3, .friends-card h3 { margin: 0 0 12px; font-size: 15px; color: #243042; }

.badge { display: inline-flex; min-width: 20px; height: 20px; align-items: center; justify-content: center; border-radius: 99px; background: #ff4d4f; color: #fff; font-size: 11px; padding: 0 6px; vertical-align: middle; }
.count { font-weight: 400; color: #8a90a3; font-size: 13px; }

.request-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-radius: 14px; background: #fafbfe; margin-bottom: 8px; }
.request-item__info { display: flex; gap: 10px; align-items: center; cursor: pointer; }
.request-item__info strong { display: block; font-size: 13px; color: #243042; }
.request-item__info span { font-size: 12px; color: #8a90a3; }
.request-item__actions { display: flex; gap: 6px; }

.friend-list { display: grid; gap: 6px; }
.friend-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 14px; background: #fafbfe; cursor: pointer; transition: background 0.15s; }
.friend-item:hover { background: #f0f2fa; }
.friend-item__info { flex: 1; min-width: 0; }
.friend-item__name { display: flex; align-items: center; gap: 6px; }
.friend-item__name strong { font-size: 14px; color: #243042; }
.friend-item__last { display: block; margin-top: 2px; font-size: 12px; color: #8a90a3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.unread { min-width: 18px; height: 18px; border-radius: 99px; background: #ff4d4f; color: #fff; font-size: 11px; display: grid; place-items: center; padding: 0 5px; }
.empty { text-align: center; padding: 32px; color: #b0b7c4; font-size: 13px; }
</style>
