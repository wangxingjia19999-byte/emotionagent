<template>
  <div class="detail-page">
    <div class="detail-page__back">
      <el-button class="back-button" @click="goCommunity">返回社区</el-button>
    </div>

    <section class="detail-shell">
      <el-skeleton v-if="loading" animated :rows="10" />

      <template v-else-if="post">
        <article class="post-main glass-card">
          <div class="post-main__top">
            <div class="post-main__tag-row">
              <el-tag effect="light" class="post-main__category">{{ post.category || '其他' }}</el-tag>
              <el-tag v-if="post.mood_tag" effect="light" :class="['post-main__mood', `mood-${post.mood_tag}`]">
                {{ post.mood_tag }}
              </el-tag>
              <el-tag v-if="post.is_anonymous" effect="light" class="post-main__anonymous">匿名发布</el-tag>
            </div>
            <div class="post-main__meta">浏览 {{ post.view_count || 0 }}</div>
          </div>

          <h1>{{ post.title }}</h1>

          <div class="post-main__author">
            <el-avatar :size="42" :src="post.author?.avatar || ''">{{ authorText }}</el-avatar>
            <div>
              <strong>{{ post.author?.nickname || post.author?.username || '匿名用户' }}</strong>
              <span>{{ formatTime(post.created_at) }}</span>
            </div>
          </div>

          <div
            v-if="postImages.length"
            class="post-main__gallery"
            :class="[`is-count-${galleryColumns}`, { 'is-single': postImages.length === 1 } ]"
            :style="galleryStyle"
          >
            <div
              v-for="(imageUrl, index) in postImages"
              :key="`${imageUrl}-${index}`"
              class="post-main__gallery-item"
            >
              <el-image
                class="post-main__gallery-image"
                :src="resolveImageUrl(imageUrl)"
                fit="contain"
                :preview-src-list="postImageSources"
                :initial-index="index"
                preview-teleported
                hide-on-click-modal
              />
            </div>
          </div>

          <div class="post-main__content">{{ post.content }}</div>

          <div class="post-main__actions">
            <el-button class="action-button" :class="{ 'is-active': liked }" @click="toggleLike">
              {{ liked ? '已点赞' : '点赞' }} · {{ post.like_count || 0 }}
            </el-button>
            <el-button class="action-button" :class="{ 'is-active': hugged }" @click="toggleHug">
              {{ hugged ? '已抱抱' : '抱抱' }} · {{ post.hug_count || 0 }}
            </el-button>
            <el-button class="action-button" :class="{ 'is-active': favorited }" @click="toggleFavorite">
              {{ favorited ? '已收藏' : '收藏' }} · {{ post.favorite_count || 0 }}
            </el-button>
            <el-button class="action-button" @click="scrollToComments">评论 · {{ post.comment_count || 0 }}</el-button>

            <template v-if="isAuthor">
              <el-button class="action-button action-button--ghost" @click="editPost">编辑</el-button>
              <el-button class="action-button action-button--ghost" @click="confirmDeletePost">删除</el-button>
            </template>
          </div>
        </article>

        <article ref="commentSectionRef" class="comment-card glass-card">
          <div class="comment-card__header">
            <div>
              <h2>评论</h2>
              <p>把想法写下来，也许会被认真回应。</p>
            </div>
          </div>

          <div class="comment-form">
            <el-input
              v-model="commentForm.content"
              type="textarea"
              :autosize="{ minRows: 4, maxRows: 8 }"
              maxlength="2000"
              show-word-limit
              placeholder="写下你的评论"
            />
            <div class="comment-form__actions">
              <el-button class="comment-form__button" @click="commentForm.content = ''">清空</el-button>
              <el-button type="primary" :loading="commentSubmitting" @click="submitComment">发布评论</el-button>
            </div>
          </div>

          <el-skeleton v-if="commentsLoading" animated :rows="4" />

          <template v-else-if="comments.length">
            <div class="comment-list">
              <div v-for="comment in comments" :key="comment.id" class="comment-item">
                <el-avatar :size="34" :src="comment.author?.avatar || ''">{{ commentAuthorText(comment) }}</el-avatar>
                <div class="comment-item__body">
                  <button type="button" class="comment-item__author" @click="goUserProfile(comment.author?.id)">
                    <strong>{{ comment.author?.nickname || comment.author?.username || '匿名用户' }}</strong>
                    <span>{{ formatTime(comment.created_at) }}</span>
                  </button>
                  <p>{{ comment.content }}</p>
                </div>
                <el-button
                  v-if="canDeleteComment(comment)"
                  text
                  class="comment-item__delete"
                  @click="removeComment(comment.id)"
                >
                  删除
                </el-button>
              </div>
            </div>

            <div class="comment-pagination" v-if="commentTotal > commentPageSize">
              <el-pagination
                v-model:current-page="commentPage"
                v-model:page-size="commentPageSize"
                :total="commentTotal"
                :page-sizes="[10, 20, 30]"
                layout="prev, pager, next"
                background
                @current-change="loadComments"
              />
            </div>
          </template>

          <EmptyState
            v-else
            title="暂无评论"
            description="这条帖子还没有收到评论，先做第一个认真回应的人吧。"
          />
        </article>
      </template>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import EmptyState from '../components/EmptyState.vue'
import { deleteComment, deletePost, favoritePost, getComments, getPostDetail, hugPost, likePost, unfavoritePost, unhugPost, unlikePost, createComment } from '../api/posts'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const commentsLoading = ref(false)
const commentSubmitting = ref(false)
const post = ref(null)
const comments = ref([])
const commentTotal = ref(0)
const commentPage = ref(1)
const commentPageSize = ref(10)
const commentSectionRef = ref()

const commentForm = reactive({ content: '' })

const currentUser = computed(() => {
  const raw = localStorage.getItem('user')
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
})

const postId = computed(() => Number(route.params.id))
const isAuthor = computed(() => currentUser.value && post.value && Number(currentUser.value.id) === Number(post.value.user_id))
const liked = computed(() => Boolean(post.value?.liked))
const hugged = computed(() => Boolean(post.value?.hugged))
const favorited = computed(() => Boolean(post.value?.favorited))
const authorText = computed(() => (post.value?.author?.nickname || post.value?.author?.username || '匿').slice(0, 1))
const postImages = computed(() => {
  const list = Array.isArray(post.value?.image_urls) ? post.value.image_urls.filter(Boolean) : []
  if (list.length) return list.slice(0, 9)
  if (post.value?.image_url) return [post.value.image_url]
  return []
})
const postImageSources = computed(() => postImages.value.map((value) => resolveImageUrl(value)))
const galleryColumns = computed(() => {
  const count = postImages.value.length
  if (count <= 1) return 1
  if (count === 2) return 2
  return 3
})
const galleryStyle = computed(() => ({
  gridTemplateColumns: `repeat(${galleryColumns.value}, minmax(0, 1fr))`
}))

const normalizePayload = (response) => response?.data ?? response ?? {}

const resolveImageUrl = (value) => {
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  return `http://127.0.0.1:8000${value.startsWith('/') ? '' : '/'}${value}`
}

const formatTime = (value) => {
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
}

const commentAuthorText = (comment) => (comment.author?.nickname || comment.author?.username || '匿').slice(0, 1)

const goUserProfile = (userId) => {
  if (!userId) return
  router.push(`/users/${userId}`)
}

const goCommunity = () => router.push('/community')

const loadPost = async () => {
  loading.value = true
  try {
    const response = await getPostDetail(postId.value)
    const payload = normalizePayload(response)
    post.value = payload.data || payload
    await loadComments(1)
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '帖子加载失败'
    ElMessage.error(message)
    goCommunity()
  } finally {
    loading.value = false
  }
}

const loadComments = async (page = commentPage.value) => {
  commentPage.value = page
  commentsLoading.value = true
  try {
    const response = await getComments(postId.value, { page: commentPage.value, page_size: commentPageSize.value })
    const payload = normalizePayload(response)
    const data = payload.data || payload
    comments.value = Array.isArray(data.items) ? data.items : []
    commentTotal.value = Number(data.total || 0)
    commentPage.value = Number(data.page || commentPage.value)
    commentPageSize.value = Number(data.page_size || commentPageSize.value)
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '评论加载失败'
    ElMessage.error(message)
  } finally {
    commentsLoading.value = false
  }
}

const updatePostState = (data, action) => {
  if (!post.value) return
  post.value = {
    ...post.value,
    like_count: data.like_count ?? post.value.like_count,
    favorite_count: data.favorite_count ?? post.value.favorite_count,
    liked: action === 'like' ? Boolean(data.liked) : post.value.liked,
    favorited: action === 'favorite' ? Boolean(data.favorited) : post.value.favorited
  }
}

const toggleLike = async () => {
  if (!post.value) return
  try {
    const response = liked.value ? await unlikePost(post.value.id) : await likePost(post.value.id)
    const payload = normalizePayload(response)
    updatePostState(payload.data || payload, 'like')
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '点赞操作失败'
    ElMessage.error(message)
  }
}

const toggleHug = async () => {
  if (!post.value) return
  try {
    const response = hugged.value ? await unhugPost(post.value.id) : await hugPost(post.value.id)
    const payload = normalizePayload(response)
    const data = payload.data || payload
    if (!post.value) return
    post.value = {
      ...post.value,
      hug_count: data.hug_count ?? post.value.hug_count,
      hugged: Boolean(data.hugged)
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '操作失败')
  }
}

const toggleFavorite = async () => {
  if (!post.value) return
  try {
    const response = favorited.value ? await unfavoritePost(post.value.id) : await favoritePost(post.value.id)
    const payload = normalizePayload(response)
    updatePostState(payload.data || payload, 'favorite')
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '收藏操作失败'
    ElMessage.error(message)
  }
}

const submitComment = async () => {
  const content = commentForm.content.trim()
  if (!content) {
    ElMessage.warning('请输入评论内容')
    return
  }

  commentSubmitting.value = true
  try {
    await createComment(post.value.id, { content })
    commentForm.content = ''
    ElMessage.success('评论发布成功')
    post.value.comment_count = (post.value.comment_count || 0) + 1
    await loadComments(1)
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '评论发布失败'
    ElMessage.error(message)
  } finally {
    commentSubmitting.value = false
  }
}

const canDeleteComment = (comment) => currentUser.value && Number(comment.user_id) === Number(currentUser.value.id)

const removeComment = async (commentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '删除评论', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteComment(commentId)
    ElMessage.success('评论已删除')
    post.value.comment_count = Math.max(0, (post.value.comment_count || 0) - 1)
    await loadComments(commentPage.value)
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      const message = error?.response?.data?.detail || error?.message || '删除评论失败'
      ElMessage.error(message)
    }
  }
}

const scrollToComments = () => {
  commentSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const editPost = () => {
  if (!post.value) return
  router.push({ path: '/publish-post', query: { id: String(post.value.id) } })
}

const confirmDeletePost = async () => {
  if (!post.value) return
  try {
    await ElMessageBox.confirm('确定要删除这条帖子吗？删除后将无法恢复。', '删除帖子', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deletePost(post.value.id)
    ElMessage.success('帖子已删除')
    goCommunity()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      const message = error?.response?.data?.detail || error?.message || '删除帖子失败'
      ElMessage.error(message)
    }
  }
}

watch(postId, () => {
  if (Number.isFinite(postId.value) && postId.value > 0) {
    loadPost()
  }
})

onMounted(() => {
  if (Number.isFinite(postId.value) && postId.value > 0) {
    loadPost()
  } else {
    goCommunity()
  }
})
</script>

<style scoped>
.detail-page {
  display: grid;
  gap: 16px;
}

.detail-page__back {
  display: flex;
}

.back-button {
  min-height: 40px;
  border-radius: 12px;
  color: #526073;
  border-color: #dbe2ee;
  background: #ffffff;
}

.detail-shell {
  display: grid;
  gap: 16px;
}

.glass-card {
  border: 1px solid #e8ebf3;
  border-radius: 22px;
  background: #ffffff;
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
}

.post-main {
  padding: 22px;
}

.post-main__top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.post-main__tag-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.post-main__category {
  border-radius: 999px;
}

.post-main__mood {
  border-radius: 999px;
}

.post-main__anonymous {
  border-radius: 999px;
  background: #f0edff;
  color: #7c6ff6;
  border-color: #d8d0ff;
}

.mood-开心 { background: #fff7e6; color: #d48806; border-color: #ffe7ba; }
.mood-难过 { background: #e6f7ff; color: #1890ff; border-color: #bae7ff; }
.mood-焦虑 { background: #fff1f0; color: #ff4d4f; border-color: #ffccc7; }
.mood-愤怒 { background: #fff0f6; color: #eb2f96; border-color: #ffd6e7; }
.mood-温暖 { background: #fff7e6; color: #fa8c16; border-color: #ffe7ba; }
.mood-平静 { background: #f6ffed; color: #52c41a; border-color: #d9f7be; }
.mood-孤独 { background: #f9f0ff; color: #722ed1; border-color: #efdbff; }
.mood-恐惧 { background: #e6fffb; color: #13c2c2; border-color: #b5f5ec; }
.mood-感激 { background: #fcffe6; color: #7cb305; border-color: #eaff8f; }

.post-main__meta {
  color: #8a90a3;
  font-size: 12px;
}

.post-main h1 {
  margin: 14px 0 0;
  font-size: 42px;
  color: #243042;
  line-height: 1.35;
}

.post-main__author {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.post-main__author strong {
  display: block;
  color: #243042;
  font-size: 19px;
}

.post-main__author span {
  display: block;
  margin-top: 4px;
  color: #8a90a3;
  font-size: 16px;
}

.post-main__content {
  margin-top: 18px;
  color: #394355;
  line-height: 2;
  font-size: 21px;
  white-space: pre-wrap;
  word-break: break-word;
}

.post-main__gallery {
  margin-top: 18px;
  display: grid;
  gap: 8px;
}

.post-main__gallery.is-count-1 {
  max-width: 300px;
  margin-left: auto;
  margin-right: auto;
}

.post-main__gallery.is-count-2 {
  max-width: 440px;
  margin-left: auto;
  margin-right: auto;
}

.post-main__gallery.is-count-3 {
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
}

.post-main__gallery-item {
  min-height: 82px;
  padding: 4px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f7f9ff 0%, #eef2fb 100%);
  overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(141, 155, 180, 0.08);
}

.post-main__gallery.is-count-1 .post-main__gallery-item {
  min-height: 100px;
}

.post-main__gallery.is-count-2 .post-main__gallery-item {
  min-height: 100px;
}

.post-main__gallery.is-count-3 .post-main__gallery-item {
  min-height: 96px;
}

.post-main__gallery-image {
  display: block;
  width: 100%;
  height: 100%;
}

.post-main__gallery-image :deep(img) {
  object-fit: contain;
  border-radius: 12px;
  background: transparent;
}

.post-main__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.action-button {
  min-height: 40px;
  border-radius: 12px;
  border: 1px solid #dbe2ee;
  background: #ffffff;
  color: #526073;
  font-size: 18px;
}

.action-button.is-active {
  border-color: #d8e1ff;
  background: #edf2ff;
  color: #6074df;
}

.action-button--ghost {
  color: #6a7281;
}

.comment-card {
  padding: 22px;
}

.comment-card__header h2 {
  margin: 0;
  font-size: 34px;
  color: #243042;
}

.comment-card__header p {
  margin: 8px 0 0;
  color: #6a7281;
  font-size: 18px;
}

.comment-form {
  margin-top: 16px;
  display: grid;
  gap: 12px;
}

.comment-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.comment-form__button {
  min-height: 40px;
  border-radius: 12px;
  color: #526073;
  border-color: #dbe2ee;
  background: #ffffff;
}

.comment-list {
  margin-top: 18px;
  display: grid;
  gap: 12px;
}

.comment-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px;
  border-radius: 16px;
  background: #f8f9fc;
}

.comment-item__body {
  flex: 1;
}

.comment-item__author {
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  cursor: pointer;
  text-align: left;
}

.comment-item__author strong {
  color: #243042;
  font-size: 18px;
}

.comment-item__author span {
  color: #8a90a3;
  font-size: 16px;
}

.comment-item p {
  margin: 8px 0 0;
  color: #394355;
  line-height: 1.9;
  font-size: 19px;
  white-space: pre-wrap;
}

.comment-item__delete {
  color: #7a8191;
}

.comment-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

@media (max-width: 720px) {
  .post-main,
  .comment-card {
    padding: 18px;
  }

  .post-main h1 {
    font-size: 38px;
  }

  .post-main__content {
    font-size: 19px;
  }

  .post-main__top {
    flex-direction: column;
    align-items: flex-start;
  }

  .post-main__gallery,
  .post-main__gallery.is-count-1,
  .post-main__gallery.is-count-2,
  .post-main__gallery.is-count-3 {
    grid-template-columns: 1fr !important;
    max-width: 100%;
  }

  .comment-item {
    flex-direction: column;
  }

  .comment-form__actions {
    flex-direction: column-reverse;
  }

  .comment-form__actions :deep(.el-button) {
    width: 100%;
  }
}
</style>