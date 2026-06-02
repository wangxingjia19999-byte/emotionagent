<template>
  <view class="page-container admin-list-page">
    <text class="page-title">分类管理</text>
    <view class="list-header">
      <button class="btn-primary small-btn" @tap="openDialog(null)">+ 新增分类</button>
    </view>
    <view class="list-item card" v-for="c in list" :key="c.id">
      <view class="item-main">
        <text class="item-icon">{{ c.icon || '📂' }}</text>
        <view class="item-info">
          <text class="item-name">{{ c.name }}</text>
          <text class="item-desc">{{ c.description }}</text>
        </view>
      </view>
      <view class="item-actions">
        <button class="btn-ghost small-btn" @tap="openDialog(c)">编辑</button>
        <button class="btn-danger small-btn" @tap="delItem(c.id)">删除</button>
      </view>
    </view>

    <view class="dialog-mask" v-if="showDialog" @tap="showDialog=false">
      <view class="dialog-content" @tap.stop>
        <text class="dialog-title">{{ editForm.id ? '编辑分类' : '新增分类' }}</text>
        <input v-model="editForm.name" placeholder="分类名称" class="d-input" />
        <input v-model="editForm.description" placeholder="描述" class="d-input" />
        <input v-model="editForm.icon" placeholder="图标" class="d-input" />
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
import { getAdminCategories, createAdminCategory, updateAdminCategory, deleteAdminCategory } from '@/api/admin'

const list = ref([])
const showDialog = ref(false)
const editForm = reactive({ id: 0, name: '', description: '', icon: '' })

onShow(() => loadData())

async function loadData() {
  try { const res = await getAdminCategories(); list.value = (res.data || res) || [] } catch {}
}

function openDialog(c) {
  if (c) Object.assign(editForm, { id: c.id, name: c.name, description: c.description || '', icon: c.icon || '' })
  else Object.assign(editForm, { id: 0, name: '', description: '', icon: '' })
  showDialog.value = true
}

async function saveItem() {
  try {
    const params = { name: editForm.name, description: editForm.description, icon: editForm.icon }
    editForm.id ? await updateAdminCategory(editForm.id, params) : await createAdminCategory(params)
    showDialog.value = false; loadData()
  } catch {}
}

async function delItem(id) { try { await deleteAdminCategory(id); loadData() } catch {} }
</script>

<style lang="scss">@import './admin-common.scss';</style>
