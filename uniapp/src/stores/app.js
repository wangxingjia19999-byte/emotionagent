// ── 全局 UI 状态管理 (Pinia) ──────────────────
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUnreadMessages } from '@/api/privateMessage'
import { getCart } from '@/api/shop'

export const useAppStore = defineStore('app', () => {
  // ── State ────────────────────────────────
  const globalLoading = ref(false)
  const networkStatus = ref(true)
  const unreadMessageCount = ref(0)
  const cartItemCount = ref(0)

  // ── Actions ──────────────────────────────
  function showLoading() {
    globalLoading.value = true
  }

  function hideLoading() {
    globalLoading.value = false
  }

  async function refreshUnreadCount() {
    try {
      const res = await getUnreadMessages()
      const data = res.data || res
      if (data.total !== undefined) {
        unreadMessageCount.value = data.total
        // 更新 Tab 红点
        if (data.total > 0) {
          uni.setTabBarBadge({
            index: 0, // 首页 tab
            text: String(data.total > 99 ? '99+' : data.total),
          })
        } else {
          uni.removeTabBarBadge({ index: 0 })
        }
      }
    } catch {
      // 静默失败
    }
  }

  async function refreshCartCount() {
    try {
      const res = await getCart()
      const data = res.data || res
      if (data.items) {
        cartItemCount.value = data.items.reduce(
          (sum, item) => sum + item.quantity,
          0
        )
      }
    } catch {
      // 静默失败
    }
  }

  return {
    globalLoading,
    networkStatus,
    unreadMessageCount,
    cartItemCount,
    showLoading,
    hideLoading,
    refreshUnreadCount,
    refreshCartCount,
  }
})
