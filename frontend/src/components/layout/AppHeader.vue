<template>
  <header class="app-header">
    <div class="app-header__copy">
      <span class="app-header__kicker">{{ pageTag }}</span>
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
    </div>

    <div class="app-header__actions">
      <template v-if="pageKey === 'home'">
        <el-button class="app-header__chip" @click="$emit('shortcut', 'notifications')">今日概览</el-button>
        <el-button class="app-header__chip" @click="$emit('shortcut', 'notifications')">通知</el-button>
      </template>

      <template v-else-if="pageKey === 'ai-chat'">
        <el-button class="app-header__chip" @click="$emit('shortcut', 'new-chat')">新建对话</el-button>
        <el-button class="app-header__chip" @click="$emit('shortcut', 'history')">历史记录</el-button>
      </template>

      <template v-else-if="pageKey === 'friends'">
        <el-input
          class="app-header__search"
          size="small"
          placeholder="搜索好友"
          clearable
          @keyup.enter="$emit('shortcut', 'search', searchKeyword)"
          v-model="searchKeyword"
        />
        <el-button class="app-header__chip" @click="$emit('shortcut', 'notifications')">消息通知</el-button>
      </template>

      <template v-else-if="pageKey === 'community'">
        <el-input
          class="app-header__search"
          size="small"
          placeholder="搜索帖子"
          clearable
          v-model="searchKeyword"
          @keyup.enter="$emit('shortcut', 'search', searchKeyword)"
        />
        <el-button class="app-header__chip app-header__chip--primary" @click="$emit('shortcut', 'publish')">
          发布动态
        </el-button>
      </template>

      <template v-else-if="pageKey === 'profile'">
        <el-button class="app-header__chip" @click="$emit('shortcut', 'security')">账号安全</el-button>
        <el-button class="app-header__chip app-header__chip--primary" @click="$emit('shortcut', 'logout')">退出登录</el-button>
      </template>

      <el-dropdown trigger="click" @command="$emit('command', $event)">
        <button class="app-header__user" type="button">
          <el-avatar :size="34" :src="user.avatar || ''">{{ userText }}</el-avatar>
          <div>
            <strong>{{ displayName }}</strong>
            <span>当前账号</span>
          </div>
        </button>

        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="home">首页概览</el-dropdown-item>
            <el-dropdown-item command="profile">个人中心</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'

defineEmits(['shortcut', 'command'])

const props = defineProps({
  pageKey: { type: String, default: 'home' },
  pageTag: { type: String, default: '当前页面' },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  user: { type: Object, default: () => ({}) }
})

const searchKeyword = ref('')
const displayName = computed(() => props.user.nickname || props.user.username || '朋友')
const userText = computed(() => (displayName.value || '朋').slice(0, 1))
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 20px 24px;
  border-radius: 24px;
  border: 1px solid #e8ebf3;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
}

.app-header__copy h1 {
  margin: 10px 0 0;
  font-size: 24px;
  color: #243042;
}

.app-header__copy p {
  margin: 8px 0 0;
  color: #6a7281;
  line-height: 1.6;
}

.app-header__kicker {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #6074df;
  background: #edf2ff;
}

.app-header__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
}

.app-header__chip {
  min-height: 40px;
  border-radius: 12px;
  border: 1px solid #dbe2ee;
  background: #ffffff;
  color: #526073;
}

.app-header__chip--primary {
  color: #ffffff;
  border-color: transparent;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
}

.app-header__search {
  width: 180px;
}

.app-header__user {
  height: 44px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #dbe2ee;
  border-radius: 999px;
  background: #ffffff;
  cursor: pointer;
}

.app-header__user strong {
  display: block;
  text-align: left;
  font-size: 13px;
  color: #243042;
}

.app-header__user span {
  display: block;
  text-align: left;
  font-size: 12px;
  color: #7a8191;
}

@media (max-width: 980px) {
  .app-header {
    flex-direction: column;
  }

  .app-header__actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>