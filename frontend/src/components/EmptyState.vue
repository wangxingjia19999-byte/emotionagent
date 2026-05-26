<template>
  <div class="empty-state">
    <div class="empty-state__icon" aria-hidden="true">
      <el-icon><Document /></el-icon>
    </div>
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <el-button v-if="actionText" class="empty-state__button" @click="$emit('action')">
      {{ actionText }}
    </el-button>
  </div>
</template>

<script setup>
import { Document } from '@element-plus/icons-vue'

defineProps({
  title: { type: String, default: '暂无内容' },
  description: { type: String, default: '这里还没有数据。' },
  actionText: { type: String, default: '' }
})

defineEmits(['action'])
</script>

<style scoped>
.empty-state {
  padding: 34px 20px;
  border-radius: 20px;
  border: 1px solid #edf0f6;
  background: #ffffff;
  text-align: center;
}

.empty-state__icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 14px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  color: #63708a;
  background: #f5f7fb;
}

.empty-state__icon :deep(svg) {
  width: 22px;
  height: 22px;
}

.empty-state h3 {
  margin: 0;
  font-size: 18px;
  color: #243042;
}

.empty-state p {
  margin: 10px 0 0;
  color: #6a7281;
  line-height: 1.7;
}

.empty-state__button {
  margin-top: 18px;
  min-height: 40px;
  border-radius: 12px;
  border-color: #dbe2ee;
  color: #526073;
}
</style>