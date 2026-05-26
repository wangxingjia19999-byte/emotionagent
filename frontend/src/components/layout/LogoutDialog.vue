<template>
  <el-dialog
    v-model="dialogVisible"
    class="logout-dialog"
    modal-class="logout-dialog__modal"
    align-center
    :show-close="false"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    width="392px"
    transition="logout-dialog-scale-fade"
  >
    <div class="logout-dialog__body">
      <button class="logout-dialog__close" type="button" aria-label="关闭弹窗" @click="hideDialog">
        <el-icon><Close /></el-icon>
      </button>

      <div class="logout-dialog__icon" aria-hidden="true">
        <el-icon><SwitchButton /></el-icon>
      </div>

      <div class="logout-dialog__copy">
        <h2>{{ title }}</h2>
        <p>{{ description }}</p>
      </div>

      <div class="logout-dialog__actions">
        <el-button class="logout-dialog__button logout-dialog__button--ghost" @click="cancelLogout">
          {{ cancelText }}
        </el-button>
        <el-button class="logout-dialog__button logout-dialog__button--primary" type="primary" @click="confirmLogout">
          {{ confirmText }}
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { Close, SwitchButton } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '退出登录' },
  description: {
    type: String,
    default: '确定要退出当前账号吗？退出后需要重新登录才能继续使用。'
  },
  confirmText: { type: String, default: '确认退出' },
  cancelText: { type: String, default: '取消' }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const hideDialog = () => {
  dialogVisible.value = false
}

const cancelLogout = () => {
  emit('cancel')
  hideDialog()
}

const confirmLogout = () => {
  emit('confirm')
  hideDialog()
}
</script>

<style scoped>
:global(.logout-dialog-scale-fade-enter-active),
:global(.logout-dialog-scale-fade-leave-active) {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

:global(.logout-dialog-scale-fade-enter-from),
:global(.logout-dialog-scale-fade-leave-to) {
  opacity: 0;
  transform: translateY(10px) scale(0.97);
}

:deep(.logout-dialog .el-dialog) {
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 22px 60px rgba(44, 52, 73, 0.16);
}

:deep(.logout-dialog__modal) {
  background: rgba(76, 84, 101, 0.26);
  backdrop-filter: blur(6px);
}

.logout-dialog__body {
  position: relative;
  padding: 22px 22px 18px;
}

.logout-dialog__close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #7b8192;
  background: #f5f7fb;
  cursor: pointer;
}

.logout-dialog__icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: #5670da;
  background: #edf2ff;
}

.logout-dialog__icon :deep(svg) {
  width: 20px;
  height: 20px;
}

.logout-dialog__copy {
  margin-top: 14px;
}

.logout-dialog__copy h2 {
  margin: 0;
  font-size: 20px;
  line-height: 1.25;
  color: #243042;
}

.logout-dialog__copy p {
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: #5f6677;
}

.logout-dialog__actions {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.logout-dialog__button {
  min-width: 108px;
  min-height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  font-weight: 600;
}

.logout-dialog__button--ghost {
  color: #5f6677;
  border: 1px solid #dbe2ee;
  background: #ffffff;
}

.logout-dialog__button--ghost:hover {
  background: #f7f9fd;
}

.logout-dialog__button--primary {
  border: 0;
  color: #ffffff;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
  box-shadow: 0 12px 22px rgba(111, 132, 232, 0.2);
}

.logout-dialog__button--primary:hover {
  background: linear-gradient(135deg, #677ddd 0%, #7188e7 100%);
}
</style>