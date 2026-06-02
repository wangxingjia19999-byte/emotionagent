<template>
  <view class="page-container publish-page">
    <view class="form card">
      <view class="form-group">
        <text class="form-label">标题</text>
        <input class="form-input" v-model="form.title" placeholder="给帖子起个标题吧" maxlength="100" />
      </view>
      <view class="form-group">
        <text class="form-label">内容</text>
        <textarea class="form-textarea" v-model="form.content" placeholder="分享你的想法..." maxlength="5000" />
      </view>
      <view class="form-group">
        <text class="form-label">分类</text>
        <view class="chip-row">
          <view v-for="cat in categories" :key="cat" class="chip" :class="{ active: form.category === cat }" @tap="form.category = form.category === cat ? '' : cat">{{ cat }}</view>
        </view>
      </view>
      <view class="form-group">
        <text class="form-label">心情标签</text>
        <view class="chip-row">
          <view v-for="mood in moodTags" :key="mood" class="chip" :class="{ active: form.mood_tag === mood }" @tap="form.mood_tag = form.mood_tag === mood ? '' : mood">{{ mood }}</view>
        </view>
      </view>
      <view class="form-group">
        <view class="flex-between">
          <text class="form-label">图片 (最多9张)</text>
          <text v-if="images.length > 0" class="text-muted" style="font-size:24rpx">{{ images.length }}/9</text>
        </view>
        <view class="image-grid" v-if="images.length">
          <view class="img-wrap" v-for="(url, i) in images" :key="i">
            <image class="preview-img" :src="url" mode="aspectFill" />
            <view class="img-remove" @tap="removeImage(i)">✕</view>
          </view>
        </view>
        <view class="add-img-btn" v-if="images.length < 9" @tap="uploadImages">
          <text class="add-icon">+</text>
          <text class="add-text">添加图片</text>
        </view>
      </view>
      <view class="form-group">
        <view class="switch-row">
          <text class="form-label">匿名发布</text>
          <switch :checked="form.is_anonymous" @change="form.is_anonymous = !form.is_anonymous" color="#7c6ff6" />
        </view>
      </view>
    </view>

    <button class="btn-primary btn-full" :loading="submitting" @tap="handlePublish">发布帖子</button>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { createPost } from '@/api/posts'
import { chooseAndUploadImages } from '@/utils/upload'
import { MOOD_TAGS, POST_CATEGORIES } from '@/utils/constants'

const categories = POST_CATEGORIES
const moodTags = MOOD_TAGS
const images = ref([])
const submitting = ref(false)

const form = reactive({
  title: '',
  content: '',
  category: '',
  mood_tag: '',
  is_anonymous: false,
})

async function uploadImages() {
  const remain = 9 - images.value.length
  try {
    const urls = await chooseAndUploadImages({ count: remain })
    images.value = [...images.value, ...urls]
  } catch { /* 用户取消 */ }
}

function removeImage(index) {
  images.value.splice(index, 1)
}

async function handlePublish() {
  if (!form.title.trim()) return uni.showToast({ title: '请输入标题', icon: 'none' })
  if (!form.content.trim()) return uni.showToast({ title: '请输入内容', icon: 'none' })
  submitting.value = true
  try {
    await createPost({
      title: form.title.trim(),
      content: form.content.trim(),
      category: form.category || undefined,
      mood_tag: form.mood_tag || undefined,
      is_anonymous: form.is_anonymous,
      image_urls: images.value,
      image_url: images.value[0] || undefined,
    })
    uni.showToast({ title: '发布成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 1000)
  } catch {} finally { submitting.value = false }
}
</script>

<style lang="scss" scoped>
.publish-page { padding-bottom: calc(48rpx + $safe-bottom); }
.form { padding: 32rpx; }
.form-group { margin-bottom: 32rpx; }
.form-label { font-size: 28rpx; font-weight: 500; color: $text-primary; margin-bottom: 12rpx; display: block; }
.form-input { width: 100%; height: 80rpx; background: $bg-page; border-radius: $radius-md; padding: 0 20rpx; font-size: 28rpx; }
.form-textarea { width: 100%; min-height: 200rpx; background: $bg-page; border-radius: $radius-md; padding: 20rpx; font-size: 28rpx; line-height: 1.6; }
.chip-row { display: flex; flex-wrap: wrap; gap: 12rpx; }
.chip { padding: 10rpx 24rpx; font-size: 26rpx; color: $text-secondary; background: $bg-page; border-radius: 32rpx; &.active { background: $primary-light; color: $primary-color; } }
.image-grid { display: flex; flex-wrap: wrap; gap: 12rpx; margin-bottom: 16rpx; }
.img-wrap { position: relative; width: 200rpx; height: 200rpx; }
.preview-img { width: 100%; height: 100%; border-radius: $radius-md; }
.img-remove { position: absolute; top: -8rpx; right: -8rpx; width: 40rpx; height: 40rpx; background: $error-color; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22rpx; }
.add-img-btn { width: 200rpx; height: 200rpx; border: 2rpx dashed $border-color; border-radius: $radius-md; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8rpx; }
.add-icon { font-size: 48rpx; color: $text-muted; }
.add-text { font-size: 24rpx; color: $text-muted; }
.switch-row { display: flex; justify-content: space-between; align-items: center; }
.btn-full { width: 100%; height: 88rpx; border-radius: $radius-lg; font-size: 32rpx; margin-top: 24rpx; }
</style>
