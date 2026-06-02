<template>
  <view class="page-container admin-list-page">
    <text class="page-title">管理员管理</text>
    <button class="btn-primary small-btn" style="margin-bottom:20rpx" @tap="openCreate">+ 新增管理员</button>
    <view class="list-item card" v-for="a in list" :key="a.id">
      <view class="item-main">
        <view class="item-info">
          <text class="item-name">{{ a.nickname || a.username }} <text class="text-muted">({{ a.role }})</text></text>
          <text class="item-desc">{{ a.username }}</text>
        </view>
      </view>
      <view class="item-actions">
        <button class="btn-ghost small-btn" @tap="openEdit(a)">编辑</button>
        <button class="btn-danger small-btn" @tap="delItem(a.id)">删除</button>
      </view>
    </view>

    <view class="dialog-mask" v-if="showDialog" @tap="showDialog=false">
      <view class="dialog-content" @tap.stop>
        <text class="dialog-title">{{ editForm.id ? '编辑管理员' : '新增管理员' }}</text>
        <input v-model="editForm.username" placeholder="用户名" class="d-input" v-if="!editForm.id" />
        <input v-model="editForm.password" placeholder="密码" type="password" class="d-input" v-if="!editForm.id" />
        <input v-model="editForm.nickname" placeholder="昵称" class="d-input" />
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
import { getAdmins, createAdmin, updateAdmin, deleteAdmin, resetAdminPassword } from '@/api/admin'

const list = ref([]); const showDialog = ref(false)
const editForm = reactive({ id: 0, username: '', password: '', nickname: '' })

onShow(() => loadData())

async function loadData() {
  try { const res = await getAdmins(); list.value = (res.data || res) || [] } catch {}
}

function openCreate() { Object.assign(editForm, { id: 0, username: '', password: '', nickname: '' }); showDialog.value = true }
function openEdit(a) { Object.assign(editForm, { id: a.id, username: a.username, password: '', nickname: a.nickname || '' }); showDialog.value = true }

async function saveItem() {
  try {
    if (editForm.id) {
      await updateAdmin(editForm.id, { nickname: editForm.nickname })
    } else {
      await createAdmin({ username: editForm.username, password: editForm.password, nickname: editForm.nickname })
    }
    showDialog.value = false; loadData()
  } catch {}
}

async function delItem(id) { try { await deleteAdmin(id); loadData() } catch {} }
</script>

<style lang="scss">@import './admin-common.scss';</style>
