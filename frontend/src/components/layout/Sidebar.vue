<template>
  <aside class="app-sidebar">
    <div class="app-sidebar__brand">
      <div class="app-sidebar__brand-mark">
        <el-icon><MagicStick /></el-icon>
      </div>
      <div>
        <strong>心语陪伴</strong>
        <span>让情绪被看见，让陪伴更靠近</span>
      </div>
    </div>

    <nav class="app-sidebar__nav" aria-label="主导航">
      <button
        v-for="item in navigationItems"
        :key="item.route"
        type="button"
        class="app-sidebar__item"
        :class="{ 'app-sidebar__item--active': isActive(item.route) }"
        @click="$emit('navigate', item.route)"
      >
        <span class="app-sidebar__item-icon" :class="`app-sidebar__item-icon--${item.theme}`">
          <el-icon><component :is="item.icon" /></el-icon>
        </span>
        <span class="app-sidebar__item-copy">
          <strong>{{ item.label }}</strong>
          <small>{{ item.description }}</small>
        </span>
      </button>
    </nav>

    <div class="app-sidebar__footer">
      <div class="app-sidebar__user">
        <el-avatar :size="40" :src="user.avatar || ''">
          {{ userText }}
        </el-avatar>
        <div>
          <span>当前用户</span>
          <strong>{{ displayName }}</strong>
        </div>
      </div>

      <el-button class="app-sidebar__logout" @click="$emit('logout')">退出登录</el-button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { Calendar, ChatDotRound, Collection, MagicStick, ShoppingCart, User, UserFilled } from '@element-plus/icons-vue'

defineEmits(['navigate', 'logout'])

const props = defineProps({
  activeRoute: { type: String, default: '/home' },
  user: { type: Object, default: () => ({}) }
})

const navigationItems = [
  { label: '首页概览', description: '看见今天的状态', route: '/home', theme: 'home', icon: MagicStick },
  { label: 'AI 情绪陪伴', description: '慢慢说也没关系', route: '/ai-chat', theme: 'ai', icon: ChatDotRound },
  { label: '每日打卡', description: '关照自己的情绪状态', route: '/daily-check', theme: 'check', icon: Calendar },
  { label: '好友聊天', description: '去和熟悉的人聊聊', route: '/friends', theme: 'friends', icon: UserFilled },
  { label: '社区广场', description: '分享和查看心情', route: '/community', theme: 'community', icon: Collection },
  { label: '解压商城', description: '挑一件解压好物给自己', route: '/shop', theme: 'shop', icon: ShoppingCart },
  { label: '个人中心', description: '资料与账号管理', route: '/profile', theme: 'profile', icon: User }
]

const displayName = computed(() => props.user.nickname || props.user.username || '朋友')
const userText = computed(() => (displayName.value || '朋').slice(0, 1))

const isActive = (route) => props.activeRoute === route || props.activeRoute.startsWith(`${route}/`)
</script>

<style scoped>
.app-sidebar {
  display: grid;
  gap: 18px;
  align-content: start;
  padding: 22px;
  border-radius: 24px;
  border: 1px solid #e8ebf3;
  background: #ffffff;
  box-shadow: 0 16px 36px rgba(44, 52, 73, 0.08);
  position: sticky;
  top: 18px;
}

.app-sidebar__brand {
  display: flex;
  gap: 12px;
  align-items: center;
}

.app-sidebar__brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: #6074df;
  background: #edf2ff;
}

.app-sidebar__brand strong {
  display: block;
  font-size: 16px;
  color: #243042;
}

.app-sidebar__brand span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.5;
  color: #7a8191;
}

.app-sidebar__nav {
  display: grid;
  gap: 10px;
}

.app-sidebar__item {
  width: 100%;
  border: 1px solid transparent;
  border-radius: 18px;
  padding: 13px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
  background: #f8f9fc;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.app-sidebar__item:hover {
  transform: translateY(-1px);
  background: #f4f6fb;
}

.app-sidebar__item--active {
  border-color: #d8e1ff;
  background: #eef3ff;
}

.app-sidebar__item-icon {
  width: 38px;
  height: 38px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  flex: none;
}

.app-sidebar__item-icon--home { color: #6074df; background: #edf2ff; }
.app-sidebar__item-icon--ai { color: #7e71ec; background: #f0edff; }
.app-sidebar__item-icon--check { color: #f0b35b; background: #fff7ed; }
.app-sidebar__item-icon--friends { color: #5f87ff; background: #edf3ff; }
.app-sidebar__item-icon--community { color: #43a78d; background: #edf9f5; }
.app-sidebar__item-icon--shop { color: #e88b5e; background: #fef5f0; }
.app-sidebar__item-icon--profile { color: #6f7c90; background: #f2f5fa; }

.app-sidebar__item-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.app-sidebar__item-copy strong {
  font-size: 14px;
  color: #243042;
}

.app-sidebar__item-copy small {
  font-size: 12px;
  color: #7a8191;
}

.app-sidebar__footer {
  display: grid;
  gap: 12px;
  padding-top: 4px;
}

.app-sidebar__user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 18px;
  background: #f8f9fc;
}

.app-sidebar__user span {
  display: block;
  font-size: 12px;
  color: #7a8191;
}

.app-sidebar__user strong {
  display: block;
  margin-top: 2px;
  color: #243042;
}

.app-sidebar__logout {
  min-height: 40px;
  border-radius: 12px;
  color: #5f6677;
  border: 1px solid #dbe2ee;
  background: #ffffff;
}
</style>