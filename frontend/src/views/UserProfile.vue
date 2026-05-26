<template>
  <div class="public-profile-page">
    <section class="public-profile-card glass-card">
      <el-skeleton v-if="loading" animated :rows="6" />

      <template v-else-if="profile">
        <div class="public-profile-card__top">
          <el-avatar :size="96" :src="profile.avatar || ''">{{ avatarText }}</el-avatar>
          <div>
            <span class="section-kicker">Profile</span>
            <h1>{{ displayName }}</h1>
            <p>{{ profile.role || 'user' }} · {{ profile.occupation || '未设置职业' }}</p>
          </div>
        </div>

        <div class="public-profile-card__grid">
          <div class="public-profile-item">
            <span>用户名</span>
            <strong>{{ profile.username || '-' }}</strong>
          </div>
          <div class="public-profile-item">
            <span>昵称</span>
            <strong>{{ profile.nickname || '未设置' }}</strong>
          </div>
          <div class="public-profile-item">
            <span>年龄</span>
            <strong>{{ profile.age === null || profile.age === undefined ? '未设置' : profile.age }}</strong>
          </div>
          <div class="public-profile-item">
            <span>性别</span>
            <strong>{{ genderLabel }}</strong>
          </div>
          <div v-if="profile.is_self" class="public-profile-item public-profile-item--wide">
            <span>邮箱</span>
            <strong>{{ profile.email || '未设置' }}</strong>
          </div>
        </div>

        <div class="public-profile-card__actions">
          <el-button v-if="profile.is_self" type="primary" @click="goOwnProfile">编辑个人资料</el-button>
          <el-button v-else type="primary" @click="friendAction">加好友</el-button>
          <el-button class="ghost-button" @click="goBack">返回</el-button>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserProfile } from '../api/user'

const props = defineProps({
  id: {
    type: [String, Number],
    required: true
  }
})

const router = useRouter()
const loading = ref(false)
const profile = ref(null)

const normalizePayload = (response) => response?.data ?? response ?? {}

const displayName = computed(() => profile.value?.nickname || profile.value?.username || '朋友')
const avatarText = computed(() => (displayName.value || '朋').slice(0, 1))
const genderLabel = computed(() => {
  const genderMap = { male: '男', female: '女', other: '其他', unknown: '未知' }
  return genderMap[profile.value?.gender] || '未设置'
})

const loadProfile = async () => {
  loading.value = true
  try {
    const response = await getUserProfile(props.id)
    const payload = normalizePayload(response)
    profile.value = payload.data || payload
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '用户资料加载失败'
    ElMessage.error(message)
    router.back()
  } finally {
    loading.value = false
  }
}

const goOwnProfile = () => router.push('/profile')
const goBack = () => router.back()
const friendAction = () => {
  ElMessage.info('好友功能会在后续好友模块中接入')
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.public-profile-page {
  display: grid;
}

.glass-card {
  padding: 24px;
  border-radius: 22px;
  border: 1px solid #e8ebf3;
  background: #ffffff;
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
}

.public-profile-card__top {
  display: flex;
  gap: 16px;
  align-items: center;
}

.section-kicker {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  padding: 0 10px;
  border-radius: 999px;
  color: #6074df;
  background: #edf2ff;
  font-size: 12px;
}

.public-profile-card__top h1 {
  margin: 10px 0 0;
  color: #243042;
  font-size: 28px;
}

.public-profile-card__top p {
  margin: 8px 0 0;
  color: #6a7281;
}

.public-profile-card__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 24px;
}

.public-profile-item {
  padding: 14px 16px;
  border-radius: 16px;
  background: #f8f9fc;
}

.public-profile-item--wide {
  grid-column: span 2;
}

.public-profile-item span {
  display: block;
  color: #8a90a3;
  font-size: 12px;
}

.public-profile-item strong {
  display: block;
  margin-top: 6px;
  color: #243042;
  font-size: 14px;
}

.public-profile-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.ghost-button {
  color: #526073;
  border-color: #dbe2ee;
}

@media (max-width: 720px) {
  .public-profile-card__top {
    flex-direction: column;
    align-items: flex-start;
  }

  .public-profile-card__grid {
    grid-template-columns: 1fr;
  }

  .public-profile-item--wide {
    grid-column: span 1;
  }
}
</style>