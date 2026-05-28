<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h3>商品管理</h3>
      <div style="display:flex;gap:10px;">
        <el-input v-model="keyword" placeholder="搜索商品" style="width:200px" clearable @change="fetchData" />
        <el-select v-model="catFilter" placeholder="分类" style="width:140px" clearable @change="fetchData">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button type="primary" @click="openDialog()">添加商品</el-button>
      </div>
    </div>

    <el-table :data="list" stripe style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="category_id" label="分类" width="80" />
      <el-table-column label="价格" width="100">
        <template #default="{ row }">¥{{ row.price }} / <del style="color:#ccc">¥{{ row.original_price }}</del></template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="70" />
      <el-table-column prop="sales_count" label="销量" width="70" />
      <el-table-column label="类型" width="70">
        <template #default="{ row }">{{ row.product_type === 'service' ? '服务' : '实物' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="70">
        <template #default="{ row }">
          <el-tag :type="row.is_on_sale ? 'success' : 'info'" size="small">{{ row.is_on_sale ? '在售' : '下架' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除？" @confirm="doDelete(row.id)">
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

    <el-dialog :title="editing ? '编辑商品' : '添加商品'" v-model="dialogVisible" width="620px">
      <el-form label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="售价"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="原价"><el-input-number v-model="form.original_price" :min="0" :precision="2" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="8"><el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="类型">
              <el-select v-model="form.product_type"><el-option label="实物" value="physical" /><el-option label="服务" value="service" /></el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="图片URL"><el-input v-model="form.image_url" /></el-form-item>
        <el-form-item label="上架">
          <el-switch v-model="form.is_on_sale" :active-value="1" :inactive-value="0" />
        </el-form-item>
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
import { getProducts, createProduct, updateProduct, deleteProduct } from '@/api/admin'
import { getCategories as fetchCategories } from '@/api/admin'

const list = ref([])
const categories = ref([])
const keyword = ref('')
const catFilter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ category_id: 1, name: '', description: '', price: 0, original_price: 0, image_url: '', stock: 0, product_type: 'physical', is_on_sale: 1, sort_order: 0 })

async function fetchData() {
  const res = await getProducts({ keyword: keyword.value, category_id: catFilter.value, page: page.value, page_size: pageSize })
  list.value = res.data.items
  total.value = res.data.total
}

async function loadCategories() {
  const res = await fetchCategories()
  categories.value = res.data
}

function openDialog(row) {
  editing.value = row || null
  if (row) {
    form.value = {
      category_id: row.category_id, name: row.name, description: row.description,
      price: row.price, original_price: row.original_price, image_url: row.image_url,
      stock: row.stock, product_type: row.product_type, is_on_sale: row.is_on_sale, sort_order: row.sort_order,
    }
  } else {
    form.value = { category_id: categories.value[0]?.id || 1, name: '', description: '', price: 0, original_price: 0, image_url: '', stock: 0, product_type: 'physical', is_on_sale: 1, sort_order: 0 }
  }
  dialogVisible.value = true
}

async function doSave() {
  try {
    if (editing.value) {
      await updateProduct(editing.value.id, form.value)
      ElMessage.success('已更新')
    } else {
      await createProduct(form.value)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    fetchData()
  } catch {}
}

async function doDelete(id) {
  try {
    await deleteProduct(id)
    ElMessage.success('已删除')
    fetchData()
  } catch {}
}

onMounted(() => { loadCategories(); fetchData() })
</script>

<style scoped>
.admin-page { background: #fff; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.admin-page__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; flex-wrap: wrap; gap: 10px; }
.admin-page__header h3 { margin: 0; font-size: 17px; color: #1a1a2e; }
</style>
