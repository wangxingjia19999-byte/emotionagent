<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h3>帖子管理</h3>
      <el-input v-model="keyword" placeholder="搜索标题或内容" style="width:240px" clearable @change="fetchData" />
    </div>

    <el-table :data="list" stripe style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column label="内容" min-width="200">
        <template #default="{ row }">
          <span style="font-size:12px;color:#666;">{{ row.content?.substring(0, 80) }}{{ row.content?.length > 80 ? '...' : '' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="80" />
      <el-table-column prop="mood_tag" label="情绪标签" width="90" />
      <el-table-column label="浏览" width="60"><template #default="{row}">{{ row.view_count }}</template></el-table-column>
      <el-table-column label="赞" width="50"><template #default="{row}">{{ row.like_count }}</template></el-table-column>
      <el-table-column label="评论" width="60"><template #default="{row}">{{ row.comment_count }}</template></el-table-column>
      <el-table-column label="匿名" width="60">
        <template #default="{row}">{{ row.is_anonymous ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="发布时间" width="160" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-popconfirm title="确认删除此帖子？" @confirm="doDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page" :page-size="pageSize" :total="total"
      layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end"
      @current-change="fetchData"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getPosts, deletePost } from '@/api/admin'

const list = ref([])
const keyword = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

async function fetchData() {
  const res = await getPosts({ keyword: keyword.value, page: page.value, page_size: pageSize })
  list.value = res.data.items
  total.value = res.data.total
}

async function doDelete(id) {
  try {
    await deletePost(id)
    ElMessage.success('已删除')
    fetchData()
  } catch {}
}

onMounted(fetchData)
</script>

<style scoped>
.admin-page { background: #fff; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.admin-page__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.admin-page__header h3 { margin: 0; font-size: 17px; color: #1a1a2e; }
</style>
