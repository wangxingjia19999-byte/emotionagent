<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h3>用户管理</h3>
      <div style="display:flex;gap:10px;">
        <el-input v-model="keyword" placeholder="搜索昵称/账号/邮箱" style="width:240px" clearable @change="fetchData" />
        <el-select v-model="roleFilter" placeholder="角色" style="width:120px" clearable @change="fetchData">
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
          <el-option label="超级管理员" value="super_admin" />
        </el-select>
      </div>
    </div>

    <el-table :data="list" stripe style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="账号" width="130" />
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="gender" label="性别" width="60" />
      <el-table-column prop="age" label="年龄" width="60" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'super_admin' ? 'danger' : row.role === 'admin' ? 'warning' : 'info'" size="small">
            {{ row.role === 'super_admin' ? '超管' : row.role === 'admin' ? '管理员' : '用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
            {{ row.status === 'active' ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="160" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page" :page-size="pageSize" :total="total"
      layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end"
      @current-change="fetchData"
    />

    <el-dialog title="编辑用户" v-model="dialogVisible" width="440px">
      <el-form label-width="80px">
        <el-form-item label="昵称"><el-input v-model="editForm.nickname" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role" style="width:100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
            <el-option label="超级管理员" value="super_admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width:100%">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers, updateUser } from '@/api/admin'

const list = ref([])
const keyword = ref('')
const roleFilter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const dialogVisible = ref(false)
const editTarget = ref(null)
const editForm = ref({ nickname: '', role: 'user', status: 'active' })

async function fetchData() {
  const res = await getUsers({ keyword: keyword.value, role: roleFilter.value, page: page.value, page_size: pageSize })
  list.value = res.data.items
  total.value = res.data.total
}

function openEdit(row) {
  editTarget.value = row
  editForm.value = { nickname: row.nickname || '', role: row.role, status: row.status }
  dialogVisible.value = true
}

async function doSaveEdit() {
  try {
    await updateUser(editTarget.value.id, editForm.value)
    ElMessage.success('已更新')
    dialogVisible.value = false
    fetchData()
  } catch {}
}

onMounted(fetchData)
</script>

<style scoped>
.admin-page { background: #fff; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.admin-page__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; flex-wrap: wrap; gap: 10px; }
.admin-page__header h3 { margin: 0; font-size: 17px; color: #1a1a2e; }
</style>
