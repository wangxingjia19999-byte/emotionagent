<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h3>分类管理</h3>
      <el-button type="primary" @click="openDialog()">添加分类</el-button>
    </div>

    <el-table :data="list" stripe style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="icon" label="图标" width="80" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除此分类？" @confirm="doDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="editing ? '编辑分类' : '添加分类'" v-model="dialogVisible" width="480px">
      <el-form label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="图标"><el-input v-model="form.icon" placeholder="如 toy, aroma" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/admin'

const list = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ name: '', description: '', icon: '', sort_order: 0 })

async function fetchList() {
  const res = await getCategories()
  list.value = res.data
}

function openDialog(row) {
  editing.value = row || null
  if (row) {
    form.value = { name: row.name, description: row.description, icon: row.icon, sort_order: row.sort_order }
  } else {
    form.value = { name: '', description: '', icon: '', sort_order: 0 }
  }
  dialogVisible.value = true
}

async function doSave() {
  try {
    if (editing.value) {
      await updateCategory(editing.value.id, form.value)
      ElMessage.success('已更新')
    } else {
      await createCategory(form.value)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    fetchList()
  } catch {}
}

async function doDelete(id) {
  try {
    await deleteCategory(id)
    ElMessage.success('已删除')
    fetchList()
  } catch {}
}

onMounted(fetchList)
</script>

<style scoped>
.admin-page { background: #fff; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.admin-page__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.admin-page__header h3 { margin: 0; font-size: 17px; color: #1a1a2e; }
</style>
