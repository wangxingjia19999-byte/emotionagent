<template>
  <div class="admin-login">
    <div class="admin-login__card">
      <div class="admin-login__header">
        <div class="admin-login__logo">⚙</div>
        <h1>管理后台</h1>
        <p>心语陪伴 · 系统管理</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="admin-login__form" @submit.prevent>
        <el-form-item prop="account">
          <el-input
            v-model="form.account"
            size="large"
            placeholder="管理员账号"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            show-password
            placeholder="管理员密码"
          />
        </el-form-item>

        <el-button
          class="admin-login__btn"
          type="primary"
          size="large"
          :loading="loading"
          @click="onLogin"
        >
          登录管理后台
        </el-button>

        <div class="admin-login__back">
          <router-link to="/login">← 返回用户登录</router-link>
        </div>
      </el-form>

      <div class="admin-login__hint">
        管理员账号由系统预设，不支持自主注册
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { adminLogin } from '../api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  account: '',
  password: '',
})

const rules = {
  account: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

const onLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await adminLogin({ account: form.account, password: form.password })
    // 管理员登录返回 data.admin，对齐存储为 user
    const adminData = res.data.admin
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    localStorage.setItem('user', JSON.stringify({
      id: adminData.id,
      username: adminData.username,
      nickname: adminData.nickname,
      role: adminData.role,
    }))
    ElMessage.success('登录成功')
    router.push('/admin')
  } catch {
    // 错误消息由后端返回：管理员账号不存在 / 密码错误，还剩 X 次 / 账户已锁定
  } finally {
    loading.value = false
  }
}
</script>

<style>
.admin-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f0f1a;
}

.admin-login__card {
  width: 420px;
  padding: 48px 40px 36px;
  background: #1a1a2e;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.5);
}

.admin-login__header {
  text-align: center;
  margin-bottom: 32px;
}

.admin-login__logo {
  width: 56px;
  height: 56px;
  margin: 0 auto 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, #1a3a4a, #16213e);
  border: 1px solid rgba(100, 255, 218, 0.2);
  color: #64ffda;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.admin-login__header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #e8e8f0;
}

.admin-login__header p {
  margin: 6px 0 0;
  font-size: 13px;
  color: #5a6a8a;
}

.admin-login__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.admin-login__btn {
  width: 100%;
  height: 46px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  background: linear-gradient(135deg, #1a3a4a, #16213e) !important;
  border: 1px solid rgba(100, 255, 218, 0.25) !important;
  color: #64ffda !important;
  cursor: pointer;
  transition: all 0.2s;
}

.admin-login__btn:hover {
  background: linear-gradient(135deg, #1e4456, #1a2e4a) !important;
  border-color: rgba(100, 255, 218, 0.45) !important;
  box-shadow: 0 4px 20px rgba(100, 255, 218, 0.1);
}

.admin-login__back {
  text-align: center;
  margin-top: 4px;
}

.admin-login__back a {
  color: #5a6a8a;
  font-size: 13px;
  text-decoration: none;
  transition: color 0.2s;
}

.admin-login__back a:hover {
  color: #8892b0;
}

.admin-login__hint {
  text-align: center;
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 12px;
  color: #3a4a5a;
}
</style>
