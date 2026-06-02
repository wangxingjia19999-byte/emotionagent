<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const authStore = useAuthStore()
const appStore = useAppStore()

onLaunch(() => {
  // 恢复登录会话
  authStore.restoreSession()
  // 检查网络状态
  uni.getNetworkType({
    success: (res) => {
      appStore.networkStatus = res.networkType !== 'none'
    },
  })
  uni.onNetworkStatusChange((res) => {
    appStore.networkStatus = res.isConnected
  })
})

onShow(() => {
  // App 从后台切回前台时刷新未读消息数
  if (authStore.isLoggedIn) {
    appStore.refreshUnreadCount()
  }
})

onHide(() => {
  // App 进入后台
})
</script>

<style lang="scss">
@import '@/uni.scss';

/* 全局样式重置 */
page {
  background-color: $bg-page;
  color: $text-primary;
  font-size: $font-md;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue',
    sans-serif;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

view {
  box-sizing: border-box;
}

image {
  display: block;
}

button {
  padding: 0;
  margin: 0;
  background: none;
  border: none;
  font-size: inherit;
  line-height: inherit;

  &::after {
    border: none;
  }
}

/* 全局工具类 */
.page-container {
  min-height: 100vh;
  padding: $spacing-lg;
  padding-bottom: calc($spacing-lg + $safe-bottom);
}

.card {
  background: $bg-card;
  border-radius: $radius-xl;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
}

.card-glass {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: $radius-xl;
  padding: $spacing-lg;
  box-shadow: $shadow-md;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.flex-col {
  display: flex;
  flex-direction: column;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-muted {
  color: $text-muted;
}

.text-secondary {
  color: $text-secondary;
}

.text-primary {
  color: $primary-color;
}

/* 按钮样式 */
.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  background: $primary-gradient;
  color: #fff;
  border-radius: $radius-lg;
  padding: $spacing-md $spacing-xl;
  font-size: $font-md;
  font-weight: 500;
  transition: all 0.2s;

  &:active {
    opacity: 0.85;
    transform: scale(0.98);
  }
}

.btn-outline {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: $primary-color;
  border: 2rpx solid $primary-color;
  border-radius: $radius-lg;
  padding: $spacing-md $spacing-xl;
  font-size: $font-md;
  font-weight: 500;

  &:active {
    background: $primary-light;
  }
}

.btn-ghost {
  display: flex;
  align-items: center;
  justify-content: center;
  background: $primary-light;
  color: $primary-color;
  border-radius: $radius-lg;
  padding: $spacing-sm $spacing-md;
  font-size: $font-sm;
  font-weight: 500;

  &:active {
    opacity: 0.75;
  }
}

.btn-danger {
  display: flex;
  align-items: center;
  justify-content: center;
  background: $error-color;
  color: #fff;
  border-radius: $radius-lg;
  padding: $spacing-md $spacing-xl;
  font-size: $font-md;
  font-weight: 500;

  &:active {
    opacity: 0.85;
  }
}

/* 安全区占位 */
.safe-bottom {
  padding-bottom: $safe-bottom;
}

/* uni-ui 全局覆盖 */
.uni-easyinput__content {
  border-radius: $radius-md !important;
}

.uni-easyinput__content-input {
  font-size: $font-md !important;
}
</style>
