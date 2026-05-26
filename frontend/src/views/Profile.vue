<template>
  <div class="profile-page">
    <div class="profile-shell">
      <header class="profile-hero-card glass-card">
        <div class="profile-hero-card__identity">
          <el-avatar :size="88" :src="avatarSource">{{ avatarText }}</el-avatar>
          <div>
            <span class="section-kicker">Profile</span>
            <h1>{{ displayName }}</h1>
            <p>{{ userInfo.email || '未设置邮箱' }}</p>
            <div class="profile-hero-card__meta">
              <span>角色：{{ userInfo.role || 'user' }}</span>
              <span>状态：愿你今天也能好好照顾自己</span>
            </div>
          </div>
        </div>

        <div class="profile-hero-card__actions">
          <el-tag effect="light" class="profile-hero-card__tag">账号状态正常</el-tag>
          <el-button class="profile-hero-card__button" @click="startEditingProfile">编辑资料</el-button>
          <el-button class="profile-hero-card__button profile-hero-card__button--ghost" @click="scrollToSecurity">
            账号安全
          </el-button>
          <input ref="avatarInputRef" class="hidden-file-input" type="file" accept="image/*" @change="handleAvatarFileChange" />
          <el-button class="profile-hero-card__button profile-hero-card__button--ghost" :loading="uploadingAvatar" @click="chooseAvatarFile">
            更换头像
          </el-button>
        </div>
      </header>

      <section class="profile-grid">
        <article class="profile-card glass-card">
          <div class="profile-card__header">
            <div>
              <span class="section-kicker">Basic Info</span>
              <h2>基础资料</h2>
              <p>先看见，再修改。需要时再进入编辑状态。</p>
            </div>
            <el-button class="profile-card__header-action" @click="startEditingProfile">编辑</el-button>
          </div>

          <el-skeleton v-if="loadingProfile" animated :rows="6" />

          <template v-else>
            <template v-if="!isEditingProfile">
              <div class="profile-info-grid">
                <div class="profile-info-item">
                  <el-icon><UserFilled /></el-icon>
                  <div>
                    <span>用户名</span>
                    <strong>{{ userInfo.username || '未获取到用户名' }}</strong>
                  </div>
                </div>
                <div class="profile-info-item">
                  <el-icon><MessageBox /></el-icon>
                  <div>
                    <span>邮箱</span>
                    <strong>{{ userInfo.email || '未设置' }}</strong>
                  </div>
                </div>
                <div class="profile-info-item">
                  <el-icon><MagicStick /></el-icon>
                  <div>
                    <span>昵称</span>
                    <strong>{{ userInfo.nickname || '未设置昵称' }}</strong>
                  </div>
                </div>
                <div class="profile-info-item">
                  <el-icon><Collection /></el-icon>
                  <div>
                    <span>职业</span>
                    <strong>{{ userInfo.occupation || '未设置职业' }}</strong>
                  </div>
                </div>
                <div class="profile-info-item">
                  <el-icon><ChatDotRound /></el-icon>
                  <div>
                    <span>年龄</span>
                    <strong>{{ userInfo.age === null || userInfo.age === undefined ? '未设置年龄' : userInfo.age }}</strong>
                  </div>
                </div>
                <div class="profile-info-item">
                  <el-icon><User /></el-icon>
                  <div>
                    <span>性别</span>
                    <strong>{{ genderLabel }}</strong>
                  </div>
                </div>
              </div>
            </template>

            <el-form
              v-else
              ref="profileFormRef"
              :model="profileForm"
              :rules="profileRules"
              label-position="top"
              class="edit-form edit-form--compact"
            >
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
              </el-form-item>

              <el-form-item label="昵称" prop="nickname">
                <el-input v-model="profileForm.nickname" maxlength="30" show-word-limit placeholder="请输入昵称" />
              </el-form-item>

              <el-form-item label="职业" prop="occupation">
                <el-input v-model="profileForm.occupation" maxlength="50" show-word-limit placeholder="请输入职业" />
              </el-form-item>

              <el-form-item label="年龄" prop="age">
                <el-input-number v-model="profileForm.age" :min="0" :max="150" :controls="true" class="age-input" placeholder="请输入年龄" />
              </el-form-item>

              <el-form-item label="性别" prop="gender">
                <el-select v-model="profileForm.gender" placeholder="请选择性别" class="gender-select">
                  <el-option label="男" value="male" />
                  <el-option label="女" value="female" />
                  <el-option label="其他" value="other" />
                  <el-option label="未知" value="unknown" />
                </el-select>
              </el-form-item>

              <div class="form-actions form-actions--compact">
                <el-button type="primary" :loading="savingProfile" @click="submitProfile">保存修改</el-button>
                <el-button @click="cancelProfileEditing">取消编辑</el-button>
              </div>
            </el-form>
          </template>
        </article>

        <article ref="securityCardRef" class="profile-card glass-card">
          <div class="profile-card__header">
            <div>
              <span class="section-kicker">Security</span>
              <h2>账号安全</h2>
              <p>定期修改密码可以更好地保护你的账号。</p>
            </div>
            <el-tag effect="light" type="success">当前账号状态正常</el-tag>
          </div>

          <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-position="top" class="edit-form edit-form--compact">
            <div class="password-note">
              <span class="password-note__dot"></span>
              <span>至少 6 位，建议包含字母和数字。</span>
            </div>

            <el-form-item label="旧密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入旧密码" />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码" />
            </el-form-item>

            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="再次输入新密码" />
            </el-form-item>

            <div class="form-actions form-actions--compact">
              <el-button type="primary" :loading="savingPassword" @click="submitPassword">修改密码</el-button>
              <el-button @click="resetPasswordForm">清空</el-button>
            </div>
          </el-form>
        </article>
      </section>

      <LogoutConfirmDialog v-model="logoutDialogVisible" @confirm="confirmLogout" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { changePassword, getProfile, updateProfile, uploadAvatar } from '../api/user'
import LogoutConfirmDialog from '../components/LogoutConfirmDialog.vue'
import { ChatDotRound, Collection, MagicStick, MessageBox, User, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const profileFormRef = ref()
const passwordFormRef = ref()
const avatarInputRef = ref()
const securityCardRef = ref()
const logoutDialogVisible = ref(false)
const loadingProfile = ref(false)
const savingProfile = ref(false)
const savingPassword = ref(false)
const uploadingAvatar = ref(false)
const isEditingProfile = ref(false)
const avatarPreview = ref('')
const avatarVersion = ref(0)

const userInfo = reactive({
  id: 0,
  username: '',
  email: '',
  nickname: '',
  avatar: '',
  occupation: '',
  age: null,
  gender: '',
  role: ''
})

const profileForm = reactive({
  email: '',
  nickname: '',
  occupation: '',
  age: null,
  gender: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const profileRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  nickname: [{ max: 30, message: '昵称不能超过 30 个字符', trigger: 'blur' }],
  occupation: [{ max: 50, message: '职业不能超过 50 个字符', trigger: 'blur' }],
  age: [{ type: 'number', min: 0, max: 150, message: '年龄范围应在 0 到 150 之间', trigger: 'change' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }]
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少 6 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的新密码不一致'))
          return
        }
        callback()
      },
      trigger: 'blur'
    }
  ]
}

const notifySessionUserUpdated = () => {
  window.dispatchEvent(new CustomEvent('session:user-updated'))
}

const displayName = computed(() => userInfo.nickname || userInfo.username || '朋友')
const avatarText = computed(() => (displayName.value || '朋').slice(0, 1))
const avatarSource = computed(() => {
  const src = avatarPreview.value || userInfo.avatar || ''
  if (!src) return ''
  const separator = src.includes('?') ? '&' : '?'
  return `${src}${separator}v=${avatarVersion.value}`
})
const genderLabel = computed(() => {
  const genderMap = { male: '男', female: '女', other: '其他', unknown: '未知' }
  return genderMap[userInfo.gender] || '未设置性别'
})

const normalizePayload = (response) => response?.data ?? response ?? {}

const syncProfileForm = () => {
  profileForm.email = userInfo.email || ''
  profileForm.nickname = userInfo.nickname || ''
  profileForm.occupation = userInfo.occupation || ''
  profileForm.age = userInfo.age ?? null
  profileForm.gender = userInfo.gender || ''
}

const applyUserInfo = (payload = {}) => {
  Object.assign(userInfo, {
    id: payload.id || 0,
    username: payload.username || '',
    email: payload.email || '',
    nickname: payload.nickname || '',
    avatar: payload.avatar || '',
    occupation: payload.occupation || '',
    age: payload.age ?? null,
    gender: payload.gender || '',
    role: payload.role || ''
  })
  if (payload.avatar) {
    avatarPreview.value = ''
    avatarVersion.value += 1
  }
  syncProfileForm()
  localStorage.setItem('user', JSON.stringify(userInfo))
  notifySessionUserUpdated()
}

const chooseAvatarFile = () => {
  avatarInputRef.value?.click()
}

const handleAvatarFileChange = async (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''

  if (!file) return
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('头像图片不能超过 5MB')
    return
  }

  uploadingAvatar.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await uploadAvatar(formData)
    const payload = normalizePayload(response)
    const avatarUrl = payload.data?.avatar || payload.avatar || ''

    if (!avatarUrl) {
      throw new Error('头像上传失败')
    }

    avatarPreview.value = avatarUrl
    userInfo.avatar = avatarUrl
    avatarVersion.value += 1
    localStorage.setItem('user', JSON.stringify(userInfo))
    ElMessage.success('头像已上传并保存')
  } catch (error) {
    const detail = error?.response?.data?.detail || error?.response?.data?.message || '头像上传失败'
    ElMessage.error(detail)
  } finally {
    uploadingAvatar.value = false
  }
}

const loadProfile = async () => {
  loadingProfile.value = true
  try {
    const response = await getProfile()
    const payload = normalizePayload(response)
    applyUserInfo(payload.data || payload)
  } catch (error) {
    const status = error?.response?.status
    if (status === 401) {
      router.replace('/login')
      return
    }
    ElMessage.error('个人资料加载失败，请稍后重试')
  } finally {
    loadingProfile.value = false
  }
}

const refreshProfile = () => loadProfile()

const submitProfile = async () => {
  if (!profileFormRef.value) return
  await profileFormRef.value.validate(async (valid) => {
    if (!valid) return

    savingProfile.value = true
    try {
      const response = await updateProfile({
        email: profileForm.email,
        nickname: profileForm.nickname,
        occupation: profileForm.occupation,
        age: profileForm.age,
        gender: profileForm.gender
      })
      const payload = normalizePayload(response)
      applyUserInfo(payload.data || payload)
      ElMessage.success('个人资料已更新')
      isEditingProfile.value = false
    } catch (error) {
      const detail = error?.response?.data?.detail || error?.response?.data?.message || '资料更新失败'
      ElMessage.error(detail)
    } finally {
      savingProfile.value = false
    }
  })
}

const submitPassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return

    savingPassword.value = true
    try {
      await changePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password,
        confirm_password: passwordForm.confirm_password
      })
      ElMessage.success('密码修改成功')
      resetPasswordForm()
    } catch (error) {
      const detail = error?.response?.data?.detail || error?.response?.data?.message || '密码修改失败'
      ElMessage.error(detail)
    } finally {
      savingPassword.value = false
    }
  })
}

const resetProfileForm = () => {
  cancelProfileEditing()
}

const resetPasswordForm = () => {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordFormRef.value?.clearValidate()
}

const goHome = () => router.push('/home')
const goTo = (path) => router.push(path)

const startEditingProfile = () => {
  syncProfileForm()
  isEditingProfile.value = true
}

const cancelProfileEditing = () => {
  syncProfileForm()
  isEditingProfile.value = false
  profileFormRef.value?.clearValidate()
}

const scrollToSecurity = () => {
  securityCardRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const openLogoutDialog = () => {
  logoutDialogVisible.value = true
}

const confirmLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.replace('/login')
}

onMounted(() => {
  const cache = localStorage.getItem('user')
  if (cache) {
    try {
      applyUserInfo(JSON.parse(cache))
    } catch {
      // ignore invalid cache
    }
  }
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 28px;
  background:
    radial-gradient(circle at 18% 15%, rgba(124, 111, 246, 0.12), transparent 22%),
    radial-gradient(circle at 82% 12%, rgba(138, 124, 255, 0.12), transparent 18%),
    radial-gradient(circle at 84% 82%, rgba(169, 156, 255, 0.14), transparent 20%),
    linear-gradient(135deg, #f7f8fc 0%, #f4f0ff 45%, #eef7ff 100%);
}

.profile-shell {
  width: min(1320px, 100%);
  margin: 0 auto;
  display: grid;
  gap: 22px;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(20px);
  box-shadow: 0 18px 46px rgba(109, 109, 173, 0.12);
  border-radius: 26px;
}

.profile-hero {
  padding: 24px 26px;
  display: flex;
  justify-content: space-between;
  gap: 22px;
  align-items: center;
}

.profile-hero__left h1,
.panel__header h2,
.shortcut-card strong {
  margin: 0;
  color: #2f3142;
}

.profile-hero__left h1 {
  margin-top: 10px;
  font-size: clamp(28px, 3vw, 42px);
}

.profile-hero__left p {
  margin: 14px 0 0;
  color: #5f6475;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

.soft-button,
.logout-button {
  min-height: 42px;
  padding: 0 18px;
  border-radius: 14px;
}

.soft-button {
  color: #7c6ff6;
  border: 1px solid rgba(124, 111, 246, 0.16);
  background: rgba(124, 111, 246, 0.08);
}

.logout-button {
  color: #ffffff;
  border-color: transparent;
  background: linear-gradient(135deg, #8d80f6 0%, #a99cff 100%);
  box-shadow: 0 14px 22px rgba(124, 111, 246, 0.18);
}

.profile-hero__right {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 22px;
  background: rgba(124, 111, 246, 0.08);
}

.hero-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.hidden-file-input {
  display: none;
}

.avatar-button {
  width: fit-content;
  margin-top: 6px;
}

.avatar-hint {
  font-size: 12px;
  line-height: 1.6;
  color: #8a8fa3;
}

.age-input,
.gender-select {
  width: 100%;
}

.hero-meta strong {
  font-size: 22px;
  color: #2f3142;
}

.hero-meta span {
  font-size: 13px;
  color: #5f6475;
}

.role-pill {
  width: fit-content;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #7c6ff6;
  background: rgba(124, 111, 246, 0.08);
}

.profile-grid,
.shortcut-grid {
  display: grid;
  gap: 16px;
}

.profile-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.panel {
  padding: 24px;
}

.panel__header h2 {
  margin-top: 8px;
  font-size: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 18px 0 18px;
}

.info-item {
  padding: 16px;
  border-radius: 18px;
  background: rgba(124, 111, 246, 0.06);
}

.info-item span {
  display: block;
  font-size: 12px;
  color: #8a8fa3;
}

.info-item strong {
  display: block;
  margin-top: 8px;
  font-size: 15px;
  color: #2f3142;
  word-break: break-all;
}

.edit-form {
  margin-top: 12px;
}

.form-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.shortcut-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.shortcut-card {
  padding: 20px;
  min-height: 150px;
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.shortcut-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 48px rgba(109, 109, 173, 0.16);
}

.shortcut-card__icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 14px;
  font-size: 18px;
  margin-bottom: 12px;
  color: #ffffff;
}

.shortcut-card__icon--violet { background: linear-gradient(135deg, #7c6ff6, #a99cff); }
.shortcut-card__icon--mint { background: linear-gradient(135deg, #6cc7b2, #a8e6cf); }
.shortcut-card__icon--blue { background: linear-gradient(135deg, #6c8cff, #8fbcff); }
.shortcut-card__icon--peach { background: linear-gradient(135deg, #ff9d8f, #ffc7ad); }

.shortcut-card p {
  margin: 10px 0 0;
  color: #5f6475;
  line-height: 1.7;
}

.section-kicker {
  display: inline-flex;
  min-height: 32px;
  padding: 0 12px;
  align-items: center;
  border-radius: 999px;
  color: #7c6ff6;
  background: rgba(124, 111, 246, 0.1);
}

@media (max-width: 1100px) {
  .profile-hero,
  .profile-grid,
  .shortcut-grid {
    grid-template-columns: 1fr;
  }

  .profile-hero {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 720px) {
  .profile-page {
    padding: 18px;
  }

  .panel,
  .profile-hero {
    padding: 18px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

.profile-page {
  min-height: auto;
  padding: 0;
  background: transparent;
}

.profile-shell {
  width: 100%;
  display: grid;
  gap: 18px;
}

.profile-hero-card,
.profile-card {
  border-radius: 22px;
  border: 1px solid #e8ebf3;
  background: #ffffff;
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
}

.profile-hero-card {
  padding: 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.profile-hero-card__identity {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-hero-card__identity h1 {
  margin: 10px 0 0;
  font-size: clamp(26px, 2.4vw, 36px);
  color: #243042;
}

.profile-hero-card__identity p {
  margin: 8px 0 0;
  color: #5f6677;
}

.profile-hero-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  margin-top: 12px;
  color: #6a7281;
  font-size: 13px;
}

.profile-hero-card__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.profile-hero-card__tag {
  border-radius: 999px;
}

.profile-hero-card__button {
  min-height: 40px;
  border-radius: 12px;
  border: 1px solid transparent;
  color: #ffffff;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
}

.profile-hero-card__button--ghost {
  color: #526073;
  border-color: #dbe2ee;
  background: #ffffff;
}

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.95fr);
  gap: 18px;
}

.profile-card {
  padding: 22px;
}

.profile-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.profile-card__header h2 {
  margin: 8px 0 0;
  font-size: 22px;
  color: #243042;
}

.profile-card__header p {
  margin: 8px 0 0;
  color: #6a7281;
  line-height: 1.6;
}

.profile-card__header-action {
  min-height: 38px;
  border-radius: 12px;
  border: 1px solid #dbe2ee;
  background: #ffffff;
  color: #526073;
}

.profile-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.profile-info-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border-radius: 16px;
  background: #f8f9fc;
}

.profile-info-item :deep(.el-icon) {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #6f84e8;
  background: #edf2ff;
  flex: none;
}

.profile-info-item span {
  display: block;
  font-size: 12px;
  color: #7a8191;
}

.profile-info-item strong {
  display: block;
  margin-top: 6px;
  color: #243042;
  word-break: break-all;
}

.edit-form--compact :deep(.el-form-item) {
  margin-bottom: 14px;
}

.edit-form--compact :deep(.el-input__wrapper),
.edit-form--compact :deep(.el-select__wrapper),
.edit-form--compact :deep(.el-input-number) {
  min-height: 40px;
}

.form-actions--compact {
  margin-top: 8px;
}

.password-note {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 14px;
  background: #f8f9fc;
  color: #6a7281;
  margin-bottom: 14px;
}

.password-note__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6f84e8;
  flex: none;
}

@media (max-width: 1100px) {
  .profile-hero-card,
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .profile-hero-card {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 720px) {
  .profile-card {
    padding: 18px;
  }

  .profile-info-grid {
    grid-template-columns: 1fr;
  }

  .profile-hero-card__identity {
    align-items: flex-start;
  }
}
</style>
