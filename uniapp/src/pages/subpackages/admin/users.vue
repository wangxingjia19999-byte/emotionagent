<template>
  <view class="page-container admin-list-page">
    <text class="page-title">用户管理</text>
    <view class="list-header">
      <input class="search-box" v-model="keyword" placeholder="搜索用户..." @confirm="loadData" />
    </view>
    <view class="list-item card" v-for="u in list" :key="u.id">
      <view class="item-main">
        <image class="item-img" :src="u.avatar || '/static/tab/profile.png'" mode="aspectFill" style="border-radius:50%" />
        <view class="item-info">
          <text class="item-name">{{ u.nickname || u.username }} <text class="text-muted">({{ u.username }})</text></text>
          <text class="item-desc">{{ u.email }} · {{ u.role }}</text>
        </view>
      </view>
      <view class="item-actions">
        <button class="btn-ghost small-btn" @tap="openDialog(u)">编辑</button>
      </view>
    </view>

    <view class="dialog-mask" v-if="showDialog" @tap="showDialog=false">
      <view class="dialog-content" @tap.stop>
        <text class="dialog-title">编辑用户</text>
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
import { getAdminUsers, updateAdminUser } from '@/api/admin'

const list = ref([]); const keyword = ref('')
const showDialog = ref(false)
const editForm = reactive({ id: 0, nickname: '' })

onShow(() => loadData())

async function loadData() {
  try { const params = {}; if (keyword.value) params.keyword = keyword.value; const res = await getAdminUsers(params); list.value = (res.data || res).items || [] } catch {}
}

function openDialog(u) { editForm.id = u.id; editForm.nickname = u.nickname || ''; showDialog.value = true }

async function saveItem() {
  try { await updateAdminUser(editForm.id, { nickname: editForm.nickname }); showDialog.value = false; loadData() } catch {}
}
</script>

<style lang="scss">@import './admin-common.scss';</style>
