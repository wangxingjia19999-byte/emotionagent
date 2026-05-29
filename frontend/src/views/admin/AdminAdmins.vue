<template>
  <div class="admin-page">
    <div class="page-header">
      <h3>管理员管理</h3>
      <el-button type="primary" @click="openCreate">+ 新增管理员</el-button>
    </div>

    <el-table :data="admins" stripe v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="nickname" label="昵称" />
      <el-table-column prop="role" label="角色" width="120">
        <template #default="{ row }">
          <el-tag :type="row.role === 'super_admin' ? 'danger' : 'primary'" size="small">
            {{ row.role === 'super_admin' ? '超级管理员' : '管理员' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="280">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="openResetPwd(row)">重置密码</el-button>
          <el-popconfirm title="确定删除该管理员？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑管理员' : '新增管理员'" width="460px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" v-if="!isEdit">
          <el-input v-model="form.password" type="password" placeholder="请输入密码（至少8位）" show-password />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="超级管理员" value="super_admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-select v-model="form.status">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">{{ isEdit ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog v-model="pwdDialogVisible" title="重置管理员密码" width="400px">
      <el-form :model="pwdForm" label-width="80px">
        <el-form-item label="管理员">
          <span>{{ pwdForm.username }}</span>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.newPassword" type="password" placeholder="请输入新密码（至少8位）" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdSaving" @click="handleResetPwd">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdmins, createAdmin, updateAdmin, deleteAdmin, resetAdminPassword } from '@/api/admin'

const loading = ref(false)
const saving = ref(false)
const pwdSaving = ref(false)
const admins = ref([])
const dialogVisible = ref(false)
const pwdDialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)

const form = reactive({ username: '', password: '', nickname: '', role: 'admin', status: 'active' })
const pwdForm = reactive({ adminId: null, username: '', newPassword: '' })

async function loadAdmins() {
  loading.value = true
  try {
    const res = await getAdmins()
    admins.value = res.data
  } catch {
    ElMessage.error('加载管理员列表失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.username = ''
  form.password = ''
  form.nickname = ''
  form.role = 'admin'
  form.status = 'active'
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editId.value = row.id
  form.username = row.username
  form.nickname = row.nickname
  form.role = row.role
  form.status = row.status
  dialogVisible.value = true
}

async function handleSave() {
  if (!isEdit.value && !form.password) {
    ElMessage.warning('请输入密码')
    return
  }
  if (!isEdit.value && form.password.length < 8) {
    ElMessage.warning('密码长度不能少于8位')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateAdmin(editId.value, { nickname: form.nickname, role: form.role, status: form.status })
      ElMessage.success('管理员已更新')
    } else {
      await createAdmin({ username: form.username, password: form.password, nickname: form.nickname || form.username, role: form.role })
      ElMessage.success('管理员已创建')
    }
    dialogVisible.value = false
    await loadAdmins()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteAdmin(id)
    ElMessage.success('管理员已删除')
    await loadAdmins()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

function openResetPwd(row) {
  pwdForm.adminId = row.id
  pwdForm.username = row.username
  pwdForm.newPassword = ''
  pwdDialogVisible.value = true
}

async function handleResetPwd() {
  if (!pwdForm.newPassword || pwdForm.newPassword.length < 8) {
    ElMessage.warning('密码长度不能少于8位')
    return
  }
  pwdSaving.value = true
  try {
    await resetAdminPassword(pwdForm.adminId, pwdForm.newPassword)
    ElMessage.success('密码已重置')
    pwdDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '重置失败')
  } finally {
    pwdSaving.value = false
  }
}

onMounted(loadAdmins)
</script>

<style scoped>
.admin-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.page-header h3 { margin: 0; font-size: 16px; }
</style>
