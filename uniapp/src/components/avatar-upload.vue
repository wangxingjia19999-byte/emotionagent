<template>
  <view class="avatar-upload" @tap="handleChoose">
    <image
      class="avatar-img"
      :src="currentSrc || defaultAvatar"
      mode="aspectFill"
    />
    <view class="avatar-mask">
      <text class="camera-icon">📷</text>
    </view>
  </view>
</template>

<script setup>
import { uploadFile } from '@/utils/upload'
import { API_BASE_URL } from '@/utils/constants'

const props = defineProps({
  currentSrc: { type: String, default: '' },
  defaultAvatar: {
    type: String,
    default: '/static/tab/profile.png',
  },
})
const emit = defineEmits(['change'])

async function handleChoose() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      try {
        // 上传头像到后端
        const token = uni.getStorageSync('access_token')
        uni.showLoading({ title: '上传中...' })
        const uploadRes = await new Promise((resolve, reject) => {
          uni.uploadFile({
            url: API_BASE_URL + '/user/avatar',
            filePath: res.tempFilePaths[0],
            name: 'file',
            header: { Authorization: `Bearer ${token}` },
            success: (r) => resolve(JSON.parse(r.data)),
            fail: reject,
          })
        })
        uni.hideLoading()
        const avatarUrl =
          uploadRes.data?.avatar || uploadRes.avatar || res.tempFilePaths[0]
        emit('change', avatarUrl)
      } catch {
        uni.hideLoading()
        uni.showToast({ title: '上传失败', icon: 'none' })
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.avatar-upload {
  position: relative;
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.avatar-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 50%;
}

.avatar-upload:active .avatar-mask {
  opacity: 1;
}

.camera-icon {
  font-size: 40rpx;
}
</style>
