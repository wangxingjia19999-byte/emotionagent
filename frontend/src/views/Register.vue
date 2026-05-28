<template>
  <div class="auth-page auth-page--register">
    <div class="floating-orb floating-orb--one soft-pulse"></div>
    <div class="floating-orb floating-orb--two soft-pulse"></div>
    <div class="floating-orb floating-orb--three soft-pulse"></div>

    <section class="auth-shell">
      <aside class="auth-hero auth-hero--register fade-in-left">
        <div class="brand-mark">
          <span class="brand-dot"></span>
          <span>心语陪伴</span>
        </div>

        <div class="hero-copy fade-in-left" style="animation-delay: 0.08s;">
          <p class="eyebrow-pill">情绪陪伴与社交互助平台</p>
          <h1>从今天开始，好好照顾自己的情绪</h1>
          <p class="hero-description">创建一个账号，记录心情、表达感受，也让自己多一个被理解的地方。</p>
        </div>

        <div class="hero-highlights hero-highlights--register">
          <article class="highlight-card stagger-item" style="animation-delay: 0.16s;">
            <span class="highlight-icon highlight-icon--mint"></span>
            <div><h3>安全倾诉</h3><p>在安心的氛围里，慢慢把想说的话讲出来。</p></div>
          </article>
          <article class="highlight-card stagger-item" style="animation-delay: 0.24s;">
            <span class="highlight-icon highlight-icon--blue"></span>
            <div><h3>温柔记录</h3><p>把日常情绪留在时间里，也留给未来的自己。</p></div>
          </article>
          <article class="highlight-card stagger-item" style="animation-delay: 0.32s;">
            <span class="highlight-icon highlight-icon--pink"></span>
            <div><h3>轻松开始</h3><p>只需几步，就能拥有属于你的陪伴空间。</p></div>
          </article>
        </div>

        <p class="hero-footnote fade-in-left" style="animation-delay: 0.4s;">注册后，你会拥有一个可以安放情绪的入口。</p>
      </aside>

      <section class="auth-panel">
        <div class="auth-card auth-card--register fade-in-up card-enter">
          <div class="auth-card__header">
            <span class="section-badge">注册</span>
            <h2>创建账号</h2>
            <p>系统将自动为你分配账号，注册后可在个人中心查看</p>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" class="auth-form" @submit.prevent>
            <el-form-item prop="email" class="stagger-item" style="animation-delay: 0.06s;">
              <el-input v-model="form.email" size="large" placeholder="请输入邮箱" clearable />
            </el-form-item>

            <el-form-item prop="verification_code" class="stagger-item" style="animation-delay: 0.12s;">
              <div class="verify-row">
                <el-input v-model="form.verification_code" size="large" placeholder="验证码" maxlength="6" />
                <el-button
                  class="verify-btn"
                  size="large"
                  :disabled="countdown > 0"
                  :loading="sending"
                  @click="handleSendCode"
                >
                  {{ countdown > 0 ? `${countdown}s 后重发` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>

            <el-form-item prop="nickname" class="stagger-item" style="animation-delay: 0.18s;">
              <el-input v-model="form.nickname" size="large" placeholder="昵称（选填）" clearable />
            </el-form-item>

            <el-form-item prop="password" class="stagger-item" style="animation-delay: 0.24s;">
              <el-input v-model="form.password" size="large" type="password" show-password placeholder="密码（至少8位，含字母和数字）" />
            </el-form-item>

            <el-form-item prop="confirmPassword" class="stagger-item" style="animation-delay: 0.3s;">
              <el-input v-model="form.confirmPassword" size="large" type="password" show-password placeholder="确认密码" />
            </el-form-item>

            <el-button class="primary-btn primary-btn--register" type="primary" size="large" :loading="loading" @click="onRegister">
              注册
            </el-button>

            <div class="auth-link auth-link--animated">
              已有账号？<router-link to="/login">去登录</router-link>
            </div>
          </el-form>
        </div>
      </section>
    </section>

    <!-- 注册成功弹窗 -->
    <el-dialog v-model="showResult" title="注册成功" width="420px" :lock-scroll="true" :close-on-click-modal="false">
      <div class="result-body">
        <p>请妥善保存你的系统账号，可用于登录：</p>
        <div class="result-account">{{ generatedAccount }}</div>
      </div>
      <template #footer>
        <el-button class="checkout-submit" @click="$router.push('/login')">去登录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register, sendVerifyCode } from '../api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const sending = ref(false)
const countdown = ref(0)
const showResult = ref(false)
const generatedAccount = ref('')

const form = reactive({
  email: '',
  verification_code: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

let countdownTimer = null

const validateEmail = (_, value, callback) => {
  if (!value) { callback(new Error('邮箱不能为空')); return }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) { callback(new Error('邮箱格式不正确')); return }
  callback()
}

const validateConfirmPassword = (_, value, callback) => {
  if (!value) { callback(new Error('确认密码不能为空')); return }
  if (value !== form.password) { callback(new Error('两次密码不一致')); return }
  callback()
}

const rules = {
  email: [{ validator: validateEmail, trigger: 'blur' }],
  verification_code: [
    { required: true, message: '验证码不能为空', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ],
  nickname: [],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
    { pattern: /[a-zA-Z]/, message: '密码必须包含至少一个字母', trigger: 'blur' },
    { pattern: /\d/, message: '密码必须包含至少一个数字', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

async function handleSendCode() {
  if (!form.email) { ElMessage.warning('请先输入邮箱'); return }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { ElMessage.warning('邮箱格式不正确'); return }

  sending.value = true
  try {
    await sendVerifyCode({ email: form.email })
    ElMessage.success('验证码已发送，请查收邮件')
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(countdownTimer)
    }, 1000)
  } finally {
    sending.value = false
  }
}

const onRegister = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await register({
        email: form.email,
        verification_code: form.verification_code,
        password: form.password,
        nickname: form.nickname
      })
      generatedAccount.value = res.data.username
      showResult.value = true
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.72s var(--ease-out) both;
}

.auth-shell {
  width: min(1360px, 100%);
  min-height: calc(100vh - 56px);
  display: grid;
  grid-template-columns: 48% 52%;
  border-radius: 32px;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.auth-hero {
  padding: 56px 56px 44px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 28px;
  background: linear-gradient(150deg, rgba(247, 249, 255, 0.92), rgba(238, 243, 255, 0.88) 54%, rgba(255, 246, 250, 0.82));
  backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.72);
  position: relative;
}

.auth-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 16%, rgba(108, 140, 255, 0.12), transparent 26%),
    radial-gradient(circle at 78% 76%, rgba(255, 184, 210, 0.16), transparent 28%);
  pointer-events: none;
}

.auth-hero > * { position: relative; z-index: 1; }

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: 0.02em;
}

.brand-dot {
  width: 12px; height: 12px; border-radius: 999px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  box-shadow: 0 0 20px rgba(124, 111, 246, 0.35);
}

.hero-copy { max-width: 560px; margin-top: 20px; }

.eyebrow-pill {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(124, 111, 246, 0.12);
  color: var(--primary);
  font-size: 13px;
  letter-spacing: 0.08em;
  margin: 0 0 18px;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(40px, 4vw, 66px);
  line-height: 1.08;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.hero-description {
  margin: 18px 0 0;
  max-width: 520px;
  font-size: 16px;
  line-height: 2;
  color: var(--text-secondary);
}

.hero-highlights { display: grid; gap: 14px; max-width: 420px; }

.highlight-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(124, 111, 246, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease-out), border-color 0.28s var(--ease-out);
}

.highlight-card:hover {
  transform: translateY(-3px);
  border-color: rgba(124, 111, 246, 0.18);
  box-shadow: 0 16px 30px rgba(124, 111, 246, 0.08);
}

.highlight-card h3 { margin: 0 0 4px; font-size: 15px; color: var(--text-primary); }
.highlight-card p { margin: 0; font-size: 13px; color: var(--text-secondary); line-height: 1.7; }

.highlight-icon {
  width: 42px; height: 42px; border-radius: 16px; flex: 0 0 42px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
}

.highlight-icon--mint { background: linear-gradient(135deg, rgba(168, 230, 207, 0.22), rgba(196, 240, 224, 0.34)); }
.highlight-icon--blue { background: linear-gradient(135deg, rgba(108, 140, 255, 0.18), rgba(184, 198, 255, 0.32)); }
.highlight-icon--pink { background: linear-gradient(135deg, rgba(255, 184, 210, 0.22), rgba(255, 210, 230, 0.34)); }

.hero-footnote { margin: 0; color: var(--text-secondary); font-size: 14px; }

.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  background: linear-gradient(180deg, rgba(250, 251, 255, 0.72), rgba(247, 248, 255, 0.82));
}

.auth-card {
  width: min(460px, 100%);
  padding: 40px 40px 36px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 24px 64px rgba(111, 123, 211, 0.15);
  backdrop-filter: blur(18px);
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out), border-color 0.3s var(--ease-out);
}

.auth-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 30px 72px rgba(111, 123, 211, 0.18);
  border-color: rgba(124, 111, 246, 0.12);
}

.auth-card__header h2 { margin: 12px 0 6px; font-size: 30px; line-height: 1.15; color: var(--text-primary); }
.auth-card__header p { margin: 0; color: var(--text-secondary); font-size: 14px; line-height: 1.8; }

.section-badge {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(124, 111, 246, 0.1);
  color: var(--primary);
  font-size: 12px;
  letter-spacing: 0.06em;
}

.auth-form { display: flex; flex-direction: column; gap: 14px; }

.verify-row { display: flex; gap: 10px; width: 100%; }
.verify-row .el-input { flex: 1; }

.verify-btn {
  flex-shrink: 0;
  min-width: 120px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid #d8e1ff;
  background: #edf2ff;
  color: #6074df;
  font-size: 13px;
}

.verify-btn:hover { background: #d8e1ff; }
.verify-btn:disabled { color: #b8bfcd; background: #f4f6fb; border-color: #e8ebf3; }

.primary-btn--register {
  margin-top: 6px;
  background-size: 200% 200%;
  animation: flowGradient 10s ease infinite;
}

.primary-btn--register:hover { transform: translateY(-2px); }

.auth-link { text-align: center; color: var(--text-secondary); font-size: 14px; margin-top: 2px; }

.auth-link--animated a {
  position: relative;
  display: inline-block;
}

.auth-link--animated a::after {
  content: '';
  position: absolute;
  left: 0; bottom: -3px;
  width: 100%; height: 1px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 0.24s var(--ease-out);
}

.auth-link--animated a:hover::after { transform: scaleX(1); }

.result-body { text-align: center; padding: 16px 0; }
.result-body p { color: #526073; margin: 0 0 16px; }

.result-account {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 4px;
  color: #6074df;
  background: #edf2ff;
  border-radius: 14px;
  padding: 16px 24px;
  display: inline-block;
}

.checkout-submit {
  border: none; color: #ffffff;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
  border-radius: 12px;
  min-height: 40px;
}

@media (max-width: 1180px) {
  .auth-shell { grid-template-columns: 1fr; min-height: auto; }
  .auth-hero { padding-bottom: 34px; }
  .auth-panel { padding-top: 0; }
}

@media (max-width: 640px) {
  .auth-page { padding: 16px; }
  .auth-hero, .auth-panel { padding-left: 20px; padding-right: 20px; }
  .auth-hero { padding-top: 24px; }
  .hero-copy h1 { font-size: 34px; }
  .auth-card { padding: 28px 22px 24px; width: min(100%, 460px); }
  .hero-highlights { max-width: none; }
}
</style>
