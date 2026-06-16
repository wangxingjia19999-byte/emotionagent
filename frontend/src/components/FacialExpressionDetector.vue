<template>
  <div class="face-detector">
    <!-- 摄像头开关按钮 -->
    <button
      class="face-detector__toggle"
      :class="{ active: isActive }"
      @click="toggleCamera"
      :title="isActive ? '关闭摄像头' : '开启摄像头表情识别'"
    >
      <el-icon :size="18"><Camera /></el-icon>
    </button>

    <!-- 检测结果指示器 -->
    <Transition name="fade-slide">
      <div v-if="isActive" class="face-detector__indicator">
        <!-- 加载中 -->
        <span v-if="loading" class="face-detector__status detecting">检测中...</span>
        <!-- 未检测到人脸 -->
        <span v-else-if="!expression" class="face-detector__status no-face">未检测到人脸</span>
        <!-- 有表情结果 -->
        <span v-else class="face-detector__result" :title="`置信度: ${(expression.confidence * 100).toFixed(0)}%`">
          <span class="face-detector__emoji">{{ emojiMap[expression.label] || '😐' }}</span>
          <span class="face-detector__label">{{ expression.label_cn }}</span>
        </span>
      </div>
    </Transition>

    <!-- 隐藏的摄像头视频元素 -->
    <video
      ref="videoRef"
      class="face-detector__video"
      autoplay
      playsinline
      muted
    ></video>

    <!-- 隐藏的画布用于帧捕获 -->
    <canvas ref="canvasRef" class="face-detector__canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onUnmounted, watch } from 'vue'
import { Camera } from '@element-plus/icons-vue'
import { detectFacialExpression } from '@/api/agent'

const emit = defineEmits(['expression-change'])

const isActive = ref(false)
const loading = ref(false)
const expression = ref(null)
const videoRef = ref(null)
const canvasRef = ref(null)
const mediaStream = ref(null)
let captureTimer = null

const emojiMap = {
  neutral: '😐',
  happy: '😊',
  sad: '😢',
  surprised: '😲',
  angry: '😠',
  fearful: '😨',
  disgusted: '🤢',
}

function getUserId() {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return String(u.id || '')
  } catch {
    return ''
  }
}

async function startCamera() {
  try {
    mediaStream.value = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user',
      },
      audio: false,
    })

    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream.value
      // 等待视频元数据加载
      await new Promise((resolve) => {
        videoRef.value.onloadedmetadata = () => resolve()
      })
      await videoRef.value.play()
    }

    // 开始周期性帧捕获
    startCapturing()
    isActive.value = true
  } catch (e) {
    console.error('摄像头访问失败:', e)
    isActive.value = false
    let msg = '无法访问摄像头'
    if (e.name === 'NotAllowedError') {
      msg = '摄像头权限被拒绝，请在浏览器设置中允许摄像头访问'
    } else if (e.name === 'NotFoundError') {
      msg = '未检测到摄像头设备'
    } else if (e.name === 'NotReadableError') {
      msg = '摄像头被其他应用占用'
    }
    // 使用 Element Plus 消息提示
    try {
      const { ElMessage } = await import('element-plus')
      ElMessage.warning(msg)
    } catch {
      alert(msg)
    }
  }
}

function stopCamera() {
  // 清除定时器
  if (captureTimer) {
    clearTimeout(captureTimer)
    captureTimer = null
  }

  // 停止媒体流
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach((track) => track.stop())
    mediaStream.value = null
  }

  // 清理视频源
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }

  isActive.value = false
  expression.value = null
  loading.value = false
}

function toggleCamera() {
  if (isActive.value) {
    stopCamera()
  } else {
    startCamera()
  }
}

function startCapturing() {
  // 等待视频准备好后开始捕获
  const capture = async () => {
    if (!isActive.value || !videoRef.value || !canvasRef.value) return

    const video = videoRef.value
    const canvas = canvasRef.value

    // 确保视频已准备好
    if (video.readyState < 2) {
      captureTimer = setTimeout(capture, 500)
      return
    }

    // 设置画布尺寸 (缩小以加快处理)
    const scale = 0.5
    canvas.width = video.videoWidth * scale
    canvas.height = video.videoHeight * scale

    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // 导出为 base64 JPEG
    const base64 = canvas.toDataURL('image/jpeg', 0.6)
    loading.value = true

    try {
      const res = await detectFacialExpression(base64, getUserId())
      const data = res.data?.data || res.data

      if (data && data.label) {
        const prev = expression.value
        expression.value = {
          label: data.label,
          label_cn: data.label_cn,
          confidence: data.confidence,
        }
        // 表情变化时通知父组件
        if (!prev || prev.label !== data.label) {
          emit('expression-change', expression.value)
        }
      } else {
        expression.value = null
      }
    } catch (e) {
      console.error('表情检测请求失败:', e)
      // 静默处理，不影响用户体验
    } finally {
      loading.value = false
    }

    // 设置下一次捕获 (2秒间隔)
    captureTimer = setTimeout(capture, 2000)
  }

  // 首次延迟500ms让视频稳定
  captureTimer = setTimeout(capture, 500)
}

// 组件卸载时清理
onUnmounted(() => {
  stopCamera()
})
</script>

<style scoped>
.face-detector {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.face-detector__toggle {
  width: 40px;
  height: 40px;
  border: 1px solid #e8ebf3;
  border-radius: 12px;
  background: #fff;
  color: #b0b7c4;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex: none;
}

.face-detector__toggle:hover {
  background: #f8f6ff;
  border-color: #cbc0ff;
  color: #7c6ff6;
}

.face-detector__toggle.active {
  background: linear-gradient(135deg, #7c6ff6, #9b8eff);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 0 0 3px rgba(124, 111, 246, 0.2);
  animation: cam-pulse 2s ease-in-out infinite;
}

@keyframes cam-pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(124, 111, 246, 0.2); }
  50% { box-shadow: 0 0 0 6px rgba(124, 111, 246, 0.08); }
}

/* 表情指示器 */
.face-detector__indicator {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  background: #f4f5fa;
  white-space: nowrap;
}

.face-detector__status {
  color: #b0b7c4;
  font-size: 12px;
}

.face-detector__status.detecting {
  animation: blink 1.2s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.face-detector__result {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #5f6475;
  cursor: default;
}

.face-detector__emoji {
  font-size: 18px;
}

.face-detector__label {
  font-weight: 500;
}

/* 隐藏的视频和画布 */
.face-detector__video,
.face-detector__canvas {
  display: none;
}

/* 过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}
</style>
