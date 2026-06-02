<template>
  <view class="page-container admin-list-page">
    <text class="page-title">商品管理</text>
    <view class="list-header">
      <input class="search-box" v-model="keyword" placeholder="搜索商品..." @confirm="loadData" />
      <button class="btn-primary small-btn" @tap="openDialog(null)">+ 新增</button>
    </view>
    <view class="list-item card" v-for="p in list" :key="p.id">
      <view class="item-main">
        <image class="item-img" :src="p.image_url" mode="aspectFill" />
        <view class="item-info">
          <text class="item-name">{{ p.name }}</text>
          <text class="item-price">¥{{ p.price }} {{ p.is_on_sale ? '在售' : '下架' }}</text>
        </view>
      </view>
      <view class="item-actions">
        <button class="btn-ghost small-btn" @tap="openDialog(p)">编辑</button>
        <button class="btn-danger small-btn" @tap="delItem(p.id)">删除</button>
      </view>
    </view>

    <!-- 编辑弹窗 -->
    <view class="dialog-mask" v-if="showDialog" @tap="showDialog=false">
      <view class="dialog-content" @tap.stop>
        <text class="dialog-title">{{ editForm.id ? '编辑商品' : '新增商品' }}</text>
        <input v-model="editForm.name" placeholder="商品名称" class="d-input" />
        <input v-model="editForm.price" placeholder="价格" type="digit" class="d-input" />
        <input v-model="editForm.image_url" placeholder="图片URL" class="d-input" />
        <input v-model="editForm.stock" placeholder="库存" type="number" class="d-input" />
        <view class="dialog-btns">
          <button class="btn-ghost" @tap="showDialog=false">取消</button>
          <button class="btn-primary" @tap="saveItem">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAdminProducts, createAdminProduct, updateAdminProduct, deleteAdminProduct } from '@/api/admin'

const list = ref([])
const keyword = ref('')
const showDialog = ref(false)
const editForm = reactive({ id: 0, name: '', price: '0', image_url: '', stock: '0' })

onShow(() => loadData())

async function loadData() {
  try { const res = await getAdminProducts({ keyword: keyword.value }); list.value = (res.data || res).items || [] } catch {}
}

function openDialog(p) {
  if (p) Object.assign(editForm, { id: p.id, name: p.name, price: String(p.price), image_url: p.image_url || '', stock: String(p.stock || 0) })
  else Object.assign(editForm, { id: 0, name: '', price: '0', image_url: '', stock: '0' })
  showDialog.value = true
}

async function saveItem() {
  try {
    const params = { name: editForm.name, price: editForm.price, image_url: editForm.image_url, stock: Number(editForm.stock), category_id: 1 }
    editForm.id ? await updateAdminProduct(editForm.id, params) : await createAdminProduct(params)
    showDialog.value = false
    loadData()
  } catch {}
}

async function delItem(id) {
  try { await deleteAdminProduct(id); loadData() } catch {}
}
</script>

<style lang="scss">
@import './admin-common.scss';
</style>
