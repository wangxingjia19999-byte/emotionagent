<template>
  <view class="page-container profile-page">
    <!-- 用户信息卡片 -->
    <view class="profile-header card-glass">
      <AvatarUpload
        :current-src="authStore.userAvatar"
        @change="handleAvatarChange"
      />
      <view class="profile-info">
        <text class="profile-name">{{ showNickname }}</text>
        <text class="profile-account">账号：{{ authStore.user?.username }}</text>
        <text class="profile-email">{{ authStore.user?.email }}</text>
      </view>
      <view class="edit-btn" @tap="showEditDialog = true">
        <text>✏️</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-item" @tap="goUserDetail(authStore.user?.id)">
        <text class="menu-icon">👤</text>
        <text class="menu-label">个人资料</text>
        <text class="menu-arrow">→</text>
      </view>
      <view class="menu-item" @tap="showPasswordDialog = true">
        <text class="menu-icon">🔒</text>
        <text class="menu-label">修改密码</text>
        <text class="menu-arrow">→</text>
      </view>
      <view class="menu-item" @tap="goFriends">
        <text class="menu-icon">👥</text>
        <text class="menu-label">好友管理</text>
        <view class="menu-badge" v-if="appStore.unreadMessageCount > 0">
          {{ appStore.unreadMessageCount }}
        </view>
        <text class="menu-arrow">→</text>
      </view>
      <view class="menu-item" @tap="goMyPosts">
        <text class="menu-icon">📝</text>
        <text class="menu-label">我的帖子</text>
        <text class="menu-arrow">→</text>
      </view>
      <view class="menu-item" @tap="goMyOrders">
        <text class="menu-icon">📦</text>
        <text class="menu-label">我的订单</text>
        <text class="menu-arrow">→</text>
      </view>
      <view class="menu-item" @tap="goDailyCheck">
        <text class="menu-icon">📋</text>
        <text class="menu-label">情绪打卡</text>
        <text class="menu-arrow">→</text>
      </view>
    </view>

    <!-- 管理后台入口 -->
    <view class="menu-section" v-if="authStore.isAdmin">
      <view class="menu-item" @tap="goAdmin">
        <text class="menu-icon">⚙️</text>
        <text class="menu-label" style="color: $primary-color;">管理后台</text>
        <text class="menu-arrow">→</text>
      </view>
    </view>

    <!-- 退出登录 -->
    <button class="btn-outline logout-btn" @tap="handleLogout">
      退出登录
    </button>

    <!-- 编辑资料弹窗 -->
    <view class="dialog-mask" v-if="showEditDialog" @tap="showEditDialog = false">
      <view class="dialog-content" @tap.stop>
        <text class="dialog-title">编辑资料</text>
        <view class="dialog-form">
          <view class="dialog-item">
            <text class="dialog-label">昵称</text>
            <input
              class="dialog-input"
              v-model="editForm.nickname"
              placeholder="输入昵称"
              maxlength="20"
            />
          </view>
          <view class="dialog-item">
            <text class="dialog-label">职业</text>
            <input
              class="dialog-input"
              v-model="editForm.occupation"
              placeholder="输入职业"
            />
          </view>
          <view class="dialog-item">
            <text class="dialog-label">年龄</text>
            <input
              class="dialog-input"
              v-model.number="editForm.age"
              placeholder="输入年龄"
              type="number"
            />
          </view>
          <view class="dialog-item">
            <text class="dialog-label">性别</text>
            <view class="gender-options">
              <view
                class="gender-opt"
                :class="{ active: editForm.gender === 'male' }"
                @tap="editForm.gender = 'male'"
              >男</view>
              <view
                class="gender-opt"
                :class="{ active: editForm.gender === 'female' }"
                @tap="editForm.gender = 'female'"
              >女</view>
              <view
                class="gender-opt"
                :class="{ active: editForm.gender === 'other' }"
                @tap="editForm.gender = 'other'"
              >其他</view>
            </view>
          </view>
        </view>
        <view class="dialog-actions">
          <button class="btn-ghost" @tap="showEditDialog = false">取消</button>
          <button class="btn-primary" @tap="handleSaveProfile">保存</button>
        </view>
      </view>
    </view>

    <!-- 修改密码弹窗 -->
    <view class="dialog-mask" v-if="showPasswordDialog" @tap="showPasswordDialog = false">
      <view class="dialog-content" @tap.stop>
        <text class="dialog-title">修改密码</text>
        <view class="dialog-form">
          <view class="dialog-item">
            <text class="dialog-label">旧密码</text>
            <input class="dialog-input" v-model="pwForm.oldPassword" type="password" placeholder="输入旧密码" />
          </view>
          <view class="dialog-item">
            <text class="dialog-label">新密码</text>
            <input class="dialog-input" v-model="pwForm.newPassword" type="password" placeholder="至少8位，包含字母和数字" />
          </view>
          <view class="dialog-item">
            <text class="dialog-label">确认密码</text>
            <input class="dialog-input" v-model="pwForm.confirmPassword" type="password" placeholder="再次输入新密码" />
          </view>
        </view>
        <view class="dialog-actions">
          <button class="btn-ghost" @tap="showPasswordDialog = false">取消</button>
          <button class="btn-primary" @tap="handleChangePassword">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { updateProfile, changePassword as changePw, logout } from '@/api/user'
import AvatarUpload from '@/components/avatar-upload.vue'

const authStore = useAuthStore()
const appStore = useAppStore()

const showEditDialog = ref(false)
const showPasswordDialog = ref(false)

const showNickname = computed(
  () => authStore.user?.nickname || authStore.user?.username || '未设置昵称'
)

const editForm = reactive({
  nickname: '',
  occupation: '',
  age: null,
  gender: '',
})

const pwForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

onShow(() => {
  if (!authStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/auth/login' })
  }
})

function initEditForm() {
  editForm.nickname = authStore.user?.nickname || ''
  editForm.occupation = authStore.user?.occupation || ''
  editForm.age = authStore.user?.age || null
  editForm.gender = authStore.user?.gender || ''
}

async function handleSaveProfile() {
  try {
    const data = {}
    if (editForm.nickname) data.nickname = editForm.nickname
    if (editForm.occupation) data.occupation = editForm.occupation
    if (editForm.age) data.age = editForm.age
    if (editForm.gender) data.gender = editForm.gender
    await updateProfile(data)
    authStore.updateUser(data)
    showEditDialog.value = false
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch {
    // 错误已处理
  }
}

async function handleChangePassword() {
  if (!pwForm.oldPassword || !pwForm.newPassword || !pwForm.confirmPassword) {
    uni.showToast({ title: '请填写所有字段', icon: 'none' })
    return
  }
  if (pwForm.newPassword.length < 8) {
    uni.showToast({ title: '新密码至少8位', icon: 'none' })
    return
  }
  if (pwForm.newPassword !== pwForm.confirmPassword) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' })
    return
  }
  try {
    await changePw({
      old_password: pwForm.oldPassword,
      new_password: pwForm.newPassword,
      confirm_password: pwForm.confirmPassword,
    })
    showPasswordDialog.value = false
    Object.assign(pwForm, { oldPassword: '', newPassword: '', confirmPassword: '' })
    uni.showToast({ title: '密码修改成功', icon: 'success' })
  } catch {
    // 错误已处理
  }
}

function handleAvatarChange(url) {
  authStore.updateUser({ avatar: url })
}

async function handleLogout() {
  try {
    await logout()
  } catch {
    // 静默
  }
  authStore.clearAllSessions()
  uni.reLaunch({ url: '/pages/auth/login' })
}

// 导航
function goUserDetail(id) {
  initEditForm()
  showEditDialog.value = true
}

function goFriends() {
  uni.navigateTo({ url: '/pages/subpackages/friends/list' })
}

function goMyPosts() {
  uni.navigateTo({ url: '/pages/subpackages/posts/detail?my=1' })
}

function goMyOrders() {
  uni.navigateTo({ url: '/pages/subpackages/shop/orders' })
}

function goDailyCheck() {
  uni.navigateTo({ url: '/pages/subpackages/questionnaire/daily-check' })
}

function goAdmin() {
  uni.navigateTo({ url: '/pages/subpackages/admin/dashboard' })
}
</script>

<style lang="scss" scoped>
.profile-page {
  padding-bottom: calc(48rpx + $safe-bottom);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-bottom: 24rpx;
  position: relative;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 36rpx;
  font-weight: 600;
  color: $text-primary;
  display: block;
}

.profile-account {
  font-size: 24rpx;
  color: $text-muted;
  display: block;
  margin-top: 4rpx;
}

.profile-email {
  font-size: 24rpx;
  color: $text-muted;
  display: block;
  margin-top: 2rpx;
}

.edit-btn {
  position: absolute;
  top: 24rpx;
  right: 24rpx;
  font-size: 36rpx;
}

.menu-section {
  background: $bg-card;
  border-radius: $radius-xl;
  margin-bottom: 24rpx;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 32rpx 24rpx;
  border-bottom: 1rpx solid $border-light;
  gap: 16rpx;

  &:last-child {
    border-bottom: none;
  }
}

.menu-icon {
  font-size: 36rpx;
  width: 48rpx;
  text-align: center;
}

.menu-label {
  flex: 1;
  font-size: 28rpx;
  color: $text-primary;
}

.menu-badge {
  background: $error-color;
  color: #fff;
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  min-width: 36rpx;
  text-align: center;
}

.menu-arrow {
  font-size: 24rpx;
  color: $text-muted;
}

.logout-btn {
  width: 100%;
  height: 88rpx;
  border-radius: $radius-lg;
  margin-top: 32rpx;
  color: $text-muted;
  border-color: $border-color;
}

// 弹窗样式
.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-end;
  z-index: 1000;
}

.dialog-content {
  width: 100%;
  background: #fff;
  border-radius: $radius-xl $radius-xl 0 0;
  padding: 40rpx 32rpx;
  padding-bottom: calc(40rpx + $safe-bottom);
}

.dialog-title {
  font-size: 34rpx;
  font-weight: 600;
  color: $text-primary;
  text-align: center;
  margin-bottom: 32rpx;
  display: block;
}

.dialog-form {
  margin-bottom: 32rpx;
}

.dialog-item {
  margin-bottom: 24rpx;
}

.dialog-label {
  font-size: 26rpx;
  color: $text-secondary;
  margin-bottom: 8rpx;
  display: block;
}

.dialog-input {
  width: 100%;
  height: 80rpx;
  background: $bg-page;
  border-radius: $radius-md;
  padding: 0 20rpx;
  font-size: 28rpx;
}

.gender-options {
  display: flex;
  gap: 16rpx;
}

.gender-opt {
  flex: 1;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-page;
  border-radius: $radius-md;
  font-size: 28rpx;
  color: $text-secondary;

  &.active {
    background: $primary-light;
    color: $primary-color;
    font-weight: 600;
  }
}

.dialog-actions {
  display: flex;
  gap: 16rpx;
}

.dialog-actions button {
  flex: 1;
  height: 80rpx;
  border-radius: $radius-lg;
  font-size: 28rpx;
}
</style>
