<template>
  <div class="stub-page">
    <div class="stub-card glass-card">
      <span class="stub-badge">AI 情绪陪伴</span>
      <h1>AI 聊天模块</h1>
      <p>这里预留为正式的 AI 聊天入口。首页不会在这里直接生成回复，只负责跳转和概览。</p>
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