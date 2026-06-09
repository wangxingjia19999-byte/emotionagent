<template>
  <view class="page-container admin-list-page">
    <text class="page-title">帖子管理</text>
    <view class="list-header">
      <input class="search-box" v-model="keyword" placeholder="搜索帖子..." @confirm="loadData" />
    </view>
    <view class="list-item card" v-for="p in list" :key="p.id">
      <view class="item-main">
        <view class="item-info">
          <text class="item-name">{{ p.title || '无标题' }}</text>
          <text class="item-desc">{{ p.content?.slice(0, 80) }}</text>
          <text class="item-desc">❤️{{ p.like_count }} 💬{{ p.comment_count }} · {{ p.author?.nickname || p.author?.username }}</text>
        </view>
      </view>
      <view class="item-actions">
        <button class="btn-danger small-btn" @tap="delItem(p.id)">删除</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAdminPosts, deleteAdminPost } from '@/api/admin'

const list = ref([]); const keyword = ref('')

onShow(() => loadData())

async function loadData() {
  try { const params = {}; if (keyword.value) params.keyword = keyword.value; const res = await getAdminPosts(params); list.value = (res.data || res).items || [] } catch {}
}

async function delItem(id) { try { await deleteAdminPost(id); loadData() } catch {} }
</script>

<style lang="scss">@import './admin-common.scss';</style>
