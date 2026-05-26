<template>
  <el-dialog
    v-model="dialogVisible"
    class="logout-confirm-dialog"
    modal-class="logout-confirm-dialog__modal"
    align-center
    :show-close="false"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    :width="dialogWidth"
    transition="logout-confirm-dialog-scale-fade"
  >
    <div class="logout-confirm-card">
      <button class="logout-confirm-card__close" type="button" aria-label="关闭弹窗" @click="hideDialog">
        <el-icon><Close /></el-icon>
      </button>

      <div class="logout-confirm-card__hero">
        <div class="logout-confirm-card__art" aria-hidden="true">
          <div class="logout-confirm-card__art-glow"></div>
          <div class="logout-confirm-card__art-shell">
            <el-icon><SwitchButton /></el-icon>
          </div>
        </div>

        <div class="logout-confirm-card__copy">
          <span class="logout-confirm-card__eyebrow">温柔确认</span>
          <h2>{{ title }}</h2>
          <p>{{ description }}</p>
        </div>
      </div>

      <div class="logout-confirm-card__note">
        <span class="logout-confirm-card__note-dot"></span>
        <span>{{ note }}</span>
      </div>

      <div class="logout-confirm-card__actions">
        <el-button class="logout-confirm-card__button logout-confirm-card__button--cancel" @click="cancelLogout">
          {{ cancelText }}
        </el-button>
        <el-button
          class="logout-confirm-card__button logout-confirm-card__button--confirm"
          type="primary"
          @click="confirmLogout"
        >
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
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '退出登录'
  },
  description: {
    type: String,
    default: '确定要暂时离开心语陪伴吗？退出后需要重新登录才能继续使用。'
  },
  note: {
    type: String,
    default: '你随时都可以再回来，之前的记录也会继续保留。'
  },
  confirmText: {
    type: String,
    default: '退出登录'
  },
  cancelText: {
    type: String,
    default: '取消'
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const dialogWidth = '440px'

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
:global(.logout-confirm-dialog-scale-fade-enter-active),
:global(.logout-confirm-dialog-scale-fade-leave-active) {
  transition: opacity 0.24s ease, transform 0.24s ease;
}

:global(.logout-confirm-dialog-scale-fade-enter-from),
:global(.logout-confirm-dialog-scale-fade-leave-to) {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}

:deep(.logout-confirm-dialog) {
  border-radius: 30px;
  overflow: hidden;
}

:deep(.logout-confirm-dialog .el-dialog) {
  border-radius: 30px;
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0.88) 36%, rgba(247, 242, 255, 0.94) 100%);
  box-shadow: 0 28px 70px rgba(109, 109, 173, 0.24);
  overflow: hidden;
}

:deep(.logout-confirm-dialog__modal) {
  background: rgba(83, 92, 120, 0.28);
  backdrop-filter: blur(8px);
}

.logout-confirm-card {
  position: relative;
  padding: 30px 30px 26px;
}

.logout-confirm-card__close {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #7c6ff6;
  background: rgba(124, 111, 246, 0.1);
  cursor: pointer;
  transition: transform 0.22s ease, background 0.22s ease, color 0.22s ease;
}

.logout-confirm-card__close:hover {
  transform: rotate(8deg) scale(1.04);
  color: #6557e8;
  background: rgba(124, 111, 246, 0.16);
}

.logout-confirm-card__hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 18px;
  align-items: center;
  padding-right: 48px;
}

.logout-confirm-card__art {
  position: relative;
  width: 84px;
  height: 84px;
  display: grid;
  place-items: center;
}

.logout-confirm-card__art-glow {
  position: absolute;
  inset: 0;
  border-radius: 28px;
  background: linear-gradient(145deg, rgba(169, 156, 255, 0.2), rgba(124, 111, 246, 0.08));
  filter: blur(1px);
}

.logout-confirm-card__art-shell {
  position: relative;
  width: 68px;
  height: 68px;
  border-radius: 24px;
  display: grid;
  place-items: center;
  color: #7c6ff6;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(243, 238, 255, 0.92));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8), 0 16px 28px rgba(124, 111, 246, 0.14);
}

.logout-confirm-card__art-shell :deep(svg) {
  width: 28px;
  height: 28px;
}

.logout-confirm-card__copy {
  display: grid;
  gap: 8px;
}

.logout-confirm-card__eyebrow {
  width: fit-content;
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 0.04em;
  color: #8c7ef5;
  background: rgba(124, 111, 246, 0.1);
}

.logout-confirm-card__copy h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.2;
  color: #2f3142;
}

.logout-confirm-card__copy p {
  margin: 0;
  color: #5f6475;
  line-height: 1.75;
  font-size: 14px;
}

.logout-confirm-card__note {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 18px;
  color: #6c7184;
  background: rgba(124, 111, 246, 0.07);
}

.logout-confirm-card__note-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a99cff 0%, #7c6ff6 100%);
  box-shadow: 0 0 0 6px rgba(124, 111, 246, 0.12);
  flex: none;
}

.logout-confirm-card__actions {
  margin-top: 22px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.logout-confirm-card__button {
  min-width: 118px;
  min-height: 44px;
  padding: 0 20px;
  border-radius: 16px;
  font-weight: 600;
  transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.22s ease, color 0.22s ease;
}

.logout-confirm-card__button:hover {
  transform: translateY(-1px);
}

.logout-confirm-card__button--cancel {
  color: #6f7284;
  border: 1px solid rgba(124, 111, 246, 0.16);
  background: rgba(124, 111, 246, 0.06);
}

.logout-confirm-card__button--cancel:hover {
  color: #5f6475;
  background: rgba(124, 111, 246, 0.1);
}

.logout-confirm-card__button--confirm {
  color: #ffffff;
  border: 0;
  background: linear-gradient(135deg, #8d80f6 0%, #a99cff 100%);
  box-shadow: 0 16px 26px rgba(124, 111, 246, 0.2);
}

.logout-confirm-card__button--confirm:hover {
  background: linear-gradient(135deg, #8374f4 0%, #9f91ff 100%);
  box-shadow: 0 18px 30px rgba(124, 111, 246, 0.24);
}

@media (max-width: 560px) {
  .logout-confirm-card {
    padding: 24px 20px 20px;
  }

  .logout-confirm-card__hero {
    grid-template-columns: 1fr;
    justify-items: start;
    padding-right: 40px;
  }

  .logout-confirm-card__art {
    width: 72px;
    height: 72px;
  }

  .logout-confirm-card__art-shell {
    width: 60px;
    height: 60px;
  }

  .logout-confirm-card__copy h2 {
    font-size: 22px;
  }

  .logout-confirm-card__actions {
    flex-direction: column-reverse;
  }

  .logout-confirm-card__button {
    width: 100%;
  }
}
</style>