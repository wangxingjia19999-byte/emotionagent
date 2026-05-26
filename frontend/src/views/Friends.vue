<template>
  <div class="stub-page">
    <div class="stub-card glass-card">
      <span class="stub-badge">好友聊天</span>
      <h1>好友私聊</h1>
      <p>这里预留为用户之间的普通聊天页面，不接入 AI 分析，也不展示情绪面板。</p>
      <el-button type="primary" class="stub-button" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const goHome = () => router.push('/home')
</script>

<style scoped>
.stub-page {
  min-height: auto;
  padding: 0;
  background: transparent;
}

.glass-card {
  padding: 32px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 18px 40px rgba(109, 109, 173, 0.12);
}

.stub-badge {
  display: inline-flex;
  min-height: 32px;
  padding: 0 12px;
  align-items: center;
  border-radius: 999px;
  color: #7c6ff6;
  background: rgba(124, 111, 246, 0.1);
}

.stub-card h1 {
  margin: 16px 0 0;
  color: #2f3142;
}

.stub-card p {
  margin: 12px 0 0;
  color: #5f6475;
  line-height: 1.8;
}

.stub-button {
  margin-top: 20px;
}
</style>