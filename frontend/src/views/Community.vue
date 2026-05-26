<template>
  <div class="community-page">
    <section class="community-hero glass-card">
      <div>
        <span class="page-kicker">Community</span>
        <h1>社区广场</h1>
        <p>在这里分享心情，也接住别人的片刻情绪。</p>
      </div>

      <el-button type="primary" class="community-hero__button" @click="goPublish">发布帖子</el-button>
    </section>

    <section class="community-toolbar glass-card">
      <div class="community-toolbar__search">
        <el-input v-model="filters.keyword" placeholder="搜索标题或正文" clearable @keyup.enter="applyFilters" />
      </div>

      <div class="community-toolbar__filters">
        <el-select v-model="filters.category" class="community-select" @change="applyFilters">
          <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>

        <el-radio-group v-model="filters.sort" class="community-sort" @change="applyFilters">
          <el-radio-button label="latest">最新</el-radio-button>
          <el-radio-button label="hot">最热</el-radio-button>
        </el-radio-group>

        <el-button class="community-toolbar__button" @click="resetFilters">重置</el-button>
      </div>
    </section>

    <section class="community-content glass-card">
      <el-skeleton v-if="loading" animated :rows="8" />

      <template v-else-if="posts.length">
        <div class="community-list">
          <PostCard v-for="post in posts" :key="post.id" :post="post" @click="goDetail(post.id)" />
        </div>

        <div class="community-pagination">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </template>

      <EmptyState
        v-else
        title="还没有帖子"
        description="还没有人发帖，先发布第一条温柔的消息吧。"
        action-text="发布帖子"
        @action="goPublish"
      />
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPosts } from '../api/posts'
import EmptyState from '../components/EmptyState.vue'
import PostCard from '../components/PostCard.vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const posts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  category: '',
  sort: 'latest'
})

const categoryOptions = [
  { label: '全部', value: '' },
  { label: '情绪倾诉', value: '情绪倾诉' },
  { label: '学习生活', value: '学习生活' },
  { label: '人际关系', value: '人际关系' },
  { label: '校园日常', value: '校园日常' },
  { label: '其他', value: '其他' }
]

const normalizePayload = (response) => response?.data ?? response ?? {}

const syncKeywordFromRoute = () => {
  const queryKeyword = String(route.query.q || '').trim()
  filters.keyword = queryKeyword
}

const loadPosts = async () => {
  loading.value = true
  try {
    const response = await getPosts({
      page: page.value,
      page_size: pageSize.value,
      keyword: filters.keyword?.trim() || undefined,
      category: filters.category || undefined,
      sort: filters.sort
    })
    const payload = normalizePayload(response)
    const data = payload.data || payload
    posts.value = Array.isArray(data.items) ? data.items : []
    total.value = Number(data.total || 0)
    page.value = Number(data.page || page.value)
    pageSize.value = Number(data.page_size || pageSize.value)
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '社区帖子加载失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  page.value = 1
  loadPosts()
}

const resetFilters = () => {
  filters.keyword = ''
  filters.category = ''
  filters.sort = 'latest'
  page.value = 1
  loadPosts()
}

const handlePageChange = (value) => {
  page.value = value
  loadPosts()
}

const handlePageSizeChange = (value) => {
  pageSize.value = value
  page.value = 1
  loadPosts()
}

const goPublish = () => router.push('/publish-post')
const goDetail = (id) => router.push(`/community/${id}`)

onMounted(() => {
  syncKeywordFromRoute()
  loadPosts()
})

watch(
  () => route.query.q,
  () => {
    syncKeywordFromRoute()
    page.value = 1
    loadPosts()
  }
)
</script>

<style scoped>
.community-page {
  display: grid;
  gap: 16px;
}

.glass-card {
  border: 1px solid #e8ebf3;
  border-radius: 22px;
  background: #ffffff;
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
}

.community-hero {
  padding: 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-kicker {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  padding: 0 10px;
  border-radius: 999px;
  color: #6074df;
  background: #edf2ff;
  font-size: 12px;
}

.community-hero h1 {
  margin: 10px 0 0;
  font-size: 28px;
  color: #243042;
}

.community-hero p {
  margin: 8px 0 0;
  color: #6a7281;
  line-height: 1.7;
}

.community-hero__button {
  min-height: 40px;
  border-radius: 12px;
}

.community-toolbar {
  padding: 16px 18px;
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.community-toolbar__search {
  flex: 1 1 320px;
}

.community-toolbar__filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.community-select {
  width: 160px;
}

.community-sort :deep(.el-radio-button__inner) {
  border: 1px solid #dbe2ee;
  background: #ffffff;
  color: #526073;
  box-shadow: none;
}

.community-sort :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #edf2ff;
  color: #6074df;
  border-color: #d8e1ff;
}

.community-toolbar__button {
  min-height: 40px;
  border-radius: 12px;
  color: #526073;
  border-color: #dbe2ee;
  background: #ffffff;
}

.community-content {
  padding: 18px;
}

.community-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.community-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

@media (max-width: 980px) {
  .community-hero,
  .community-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .community-list {
    grid-template-columns: 1fr;
  }

  .community-pagination {
    justify-content: center;
  }
}
</style>