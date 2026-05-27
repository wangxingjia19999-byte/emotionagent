<template>
  <article class="post-card" role="button" tabindex="0" @click="$emit('click')" @keydown.enter="$emit('click')">
    <div class="post-card__header">
      <div class="post-card__tags">
        <el-tag size="small" effect="light" class="post-card__category">{{ post.category || '其他' }}</el-tag>
        <el-tag v-if="post.mood_tag" size="small" effect="light" :class="['post-card__mood', `mood-${post.mood_tag}`]">
          {{ post.mood_tag }}
        </el-tag>
        <el-tag v-if="post.is_anonymous" size="small" effect="light" class="post-card__anonymous">匿名</el-tag>
      </div>
      <span class="post-card__time">{{ formattedTime }}</span>
    </div>

    <h3 class="post-card__title">{{ post.title }}</h3>
    <div v-if="coverImage" class="post-card__image">
      <div class="post-card__media">
        <img :src="resolveImageUrl(coverImage)" alt="帖子图片" />
      </div>
    </div>
    <p class="post-card__content">{{ summary }}</p>

    <div class="post-card__footer">
      <div class="post-card__author">
        <el-avatar :size="30" :src="post.author?.avatar || ''">{{ authorText }}</el-avatar>
        <div>
          <strong>{{ post.author?.nickname || post.author?.username || '匿名用户' }}</strong>
          <span>{{ post.author?.role || 'user' }}</span>
        </div>
      </div>

      <div class="post-card__stats">
        <span>浏览 {{ post.view_count || 0 }}</span>
        <span>赞 {{ post.like_count || 0 }}</span>
        <span>抱 {{ post.hug_count || 0 }}</span>
        <span>评 {{ post.comment_count || 0 }}</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

defineEmits(['click'])

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const summary = computed(() => {
  const content = String(props.post.content || '').replace(/\s+/g, ' ').trim()
  return content.length > 120 ? `${content.slice(0, 120)}...` : content
})

const authorName = computed(() => props.post.author?.nickname || props.post.author?.username || '匿名用户')
const authorText = computed(() => (authorName.value || '匿').slice(0, 1))
const coverImage = computed(() => {
  const images = Array.isArray(props.post.image_urls) ? props.post.image_urls.filter(Boolean) : []
  return images[0] || props.post.image_url || ''
})

const resolveImageUrl = (value) => {
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  return `http://127.0.0.1:8000${value.startsWith('/') ? '' : '/'}${value}`
}

const formattedTime = computed(() => {
  const value = props.post.created_at
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
})
</script>

<style scoped>
.post-card {
  padding: 20px;
  border-radius: 22px;
  border: 1px solid #edf0f6;
  background: #ffffff;
  box-shadow: 0 12px 24px rgba(44, 52, 73, 0.05);
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.post-card:hover,
.post-card:focus-visible {
  transform: translateY(-2px);
  border-color: #dbe2ee;
  box-shadow: 0 16px 30px rgba(44, 52, 73, 0.08);
  outline: none;
}

.post-card__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.post-card__tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.post-card__category {
  border-radius: 999px;
}

.post-card__mood {
  border-radius: 999px;
}

.post-card__anonymous {
  border-radius: 999px;
  background: #f0edff;
  color: #7c6ff6;
  border-color: #d8d0ff;
}

/* 情绪标签颜色 */
.mood-开心 { background: #fff7e6; color: #d48806; border-color: #ffe7ba; }
.mood-难过 { background: #e6f7ff; color: #1890ff; border-color: #bae7ff; }
.mood-焦虑 { background: #fff1f0; color: #ff4d4f; border-color: #ffccc7; }
.mood-愤怒 { background: #fff0f6; color: #eb2f96; border-color: #ffd6e7; }
.mood-温暖 { background: #fff7e6; color: #fa8c16; border-color: #ffe7ba; }
.mood-平静 { background: #f6ffed; color: #52c41a; border-color: #d9f7be; }
.mood-孤独 { background: #f9f0ff; color: #722ed1; border-color: #efdbff; }
.mood-恐惧 { background: #e6fffb; color: #13c2c2; border-color: #b5f5ec; }
.mood-感激 { background: #fcffe6; color: #7cb305; border-color: #eaff8f; }

.post-card__time {
  font-size: 12px;
  color: #8a90a3;
}

.post-card__title {
  margin: 14px 0 0;
  font-size: 18px;
  line-height: 1.45;
  color: #243042;
}

.post-card__image {
  margin-top: 12px;
}

.post-card__media {
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 16 / 9;
  padding: 10px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f7f9ff 0%, #eef2fb 100%);
  overflow: hidden;
}

.post-card__media img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 12px;
  background: transparent;
}

.post-card__content {
  margin: 10px 0 0;
  color: #5f6677;
  line-height: 1.8;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
  min-height: 5.4em;
}

.post-card__footer {
  margin-top: 18px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 14px;
}

.post-card__author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.post-card__author strong {
  display: block;
  font-size: 13px;
  color: #243042;
}

.post-card__author span {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  color: #8a90a3;
}

.post-card__stats {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  font-size: 12px;
  color: #6a7281;
}

@media (max-width: 640px) {
  .post-card__footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .post-card__stats {
    justify-content: flex-start;
  }
}
</style>