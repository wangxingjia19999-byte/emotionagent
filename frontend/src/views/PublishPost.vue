<template>
  <div class="publish-page">
    <section class="publish-hero glass-card">
      <div>
        <span class="page-kicker">Post</span>
        <h1>{{ pageTitle }}</h1>
        <p>把想说的话放在这里，也许会有人认真看见。</p>
      </div>

      <el-button class="publish-hero__back" @click="goCommunity">返回社区</el-button>
    </section>

    <section class="publish-card glass-card">
      <el-skeleton v-if="loading" animated :rows="6" />

      <el-form v-else ref="formRef" :model="form" :rules="rules" label-position="top" class="publish-form">
        <div class="publish-form__grid">
          <el-form-item label="标题" prop="title" class="span-2">
            <el-input v-model="form.title" maxlength="100" show-word-limit placeholder="给帖子起一个清晰的标题" />
          </el-form-item>

          <el-form-item label="分类" prop="category">
            <el-select v-model="form.category" placeholder="请选择分类">
              <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="正文" prop="content" class="span-2">
            <el-input
              v-model="form.content"
              type="textarea"
              :autosize="{ minRows: 10, maxRows: 16 }"
              maxlength="5000"
              show-word-limit
              placeholder="把心情、经历、想法写下来"
            />
          </el-form-item>

          <el-form-item label="图片" class="span-2">
            <div class="image-uploader">
              <input
                ref="imageInputRef"
                class="image-uploader__input"
                type="file"
                accept="image/*"
                multiple
                @change="handleImageChange"
              />

              <div v-if="imagePreviews.length" class="image-uploader__preview">
                <div class="image-uploader__meta">
                  <span>已选择 {{ imagePreviews.length }}/9 张</span>
                  <el-button class="image-uploader__button" :disabled="uploadingImage || imagePreviews.length >= 9" @click="triggerImageSelect">
                    继续添加
                  </el-button>
                </div>

                <div class="image-uploader__grid">
                  <div v-for="(imageUrl, index) in imagePreviews" :key="`${imageUrl}-${index}`" class="image-uploader__tile">
                    <img :src="imageUrl" alt="帖子图片预览" />
                    <button type="button" class="image-uploader__remove" @click="removeImage(index)">×</button>
                  </div>

                  <button
                    v-if="imagePreviews.length < 9"
                    type="button"
                    class="image-uploader__add"
                    :disabled="uploadingImage"
                    @click="triggerImageSelect"
                  >
                    + 添加图片
                  </button>
                </div>
              </div>

              <div v-else class="image-uploader__empty">
                <p>最多可上传 9 张图片，支持 jpg、png、gif、webp 等格式。</p>
                <el-button type="primary" :loading="uploadingImage" @click="triggerImageSelect">选择图片</el-button>
              </div>
            </div>
          </el-form-item>
        </div>

        <div class="publish-actions">
          <el-button class="publish-actions__ghost" @click="goCommunity">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitPost">{{ submitText }}</el-button>
        </div>
      </el-form>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createPost, getPostDetail, updatePost, uploadPostImage } from '../api/posts'

const router = useRouter()
const route = useRoute()
const formRef = ref()
const imageInputRef = ref()
const loading = ref(false)
const submitting = ref(false)
const uploadingImage = ref(false)
const editingPostId = ref(null)

const categoryOptions = [
  { label: '情绪倾诉', value: '情绪倾诉' },
  { label: '学习生活', value: '学习生活' },
  { label: '人际关系', value: '人际关系' },
  { label: '校园日常', value: '校园日常' },
  { label: '其他', value: '其他' }
]

const form = reactive({
  title: '',
  category: '',
  content: '',
  image_url: '',
  image_urls: []
})

const rules = {
  title: [
    { required: true, message: '标题不能为空', trigger: 'blur' },
    { max: 100, message: '标题长度不能超过100个字符', trigger: 'blur' }
  ],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [
    { required: true, message: '正文不能为空', trigger: 'blur' },
    { min: 5, message: '正文建议不少于5个字', trigger: 'blur' }
  ]
}

const pageTitle = computed(() => (editingPostId.value ? '编辑帖子' : '发布帖子'))
const submitText = computed(() => (editingPostId.value ? '保存修改' : '发布帖子'))
const imagePreviews = computed(() => form.image_urls.map((value) => resolveImageUrl(value)))

const normalizePayload = (response) => response?.data ?? response ?? {}

const goCommunity = () => router.push('/community')

const resolveImageUrl = (value) => {
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  return `http://127.0.0.1:8000${value.startsWith('/') ? '' : '/'}${value}`
}

const resetForm = () => {
  form.title = ''
  form.category = ''
  form.content = ''
  form.image_url = ''
  form.image_urls = []
  formRef.value?.clearValidate()
}

const triggerImageSelect = () => {
  imageInputRef.value?.click()
}

const clearImage = () => {
  form.image_url = ''
  form.image_urls = []
  if (imageInputRef.value) {
    imageInputRef.value.value = ''
  }
}

const removeImage = (index) => {
  form.image_urls.splice(index, 1)
  form.image_url = form.image_urls[0] || ''
}

const handleImageChange = async (event) => {
  const files = Array.from(event?.target?.files || [])
  event.target.value = ''
  if (!files.length) return

  const remainingSlots = 9 - form.image_urls.length
  if (remainingSlots <= 0) {
    ElMessage.warning('最多只能上传 9 张图片')
    return
  }

  uploadingImage.value = true
  try {
    const selectedFiles = files.slice(0, remainingSlots)
    if (files.length > remainingSlots) {
      ElMessage.warning(`已超过限制，系统只会上传前 ${remainingSlots} 张图片`)
    }

    const uploadedUrls = []
    for (const file of selectedFiles) {
      if (!file.type.startsWith('image/')) {
        continue
      }
      const response = await uploadPostImage(file)
      const payload = normalizePayload(response)
      const imageUrl = payload?.data?.image_url || payload?.image_url || ''
      if (imageUrl) {
        uploadedUrls.push(imageUrl)
      }
    }

    if (!uploadedUrls.length) {
      ElMessage.warning('请选择图片文件')
      return
    }

    form.image_urls = [...form.image_urls, ...uploadedUrls].slice(0, 9)
    form.image_url = form.image_urls[0] || ''
    ElMessage.success(`已上传 ${uploadedUrls.length} 张图片`)
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '图片上传失败'
    ElMessage.error(message)
  } finally {
    uploadingImage.value = false
    if (event?.target) {
      event.target.value = ''
    }
  }
}

const loadPostForEdit = async (id) => {
  loading.value = true
  try {
    const response = await getPostDetail(id)
    const payload = normalizePayload(response)
    const data = payload.data || payload
    form.title = data.title || ''
    form.category = data.category || ''
    form.content = data.content || ''
    form.image_urls = Array.isArray(data.image_urls) && data.image_urls.length ? data.image_urls.slice(0, 9) : (data.image_url ? [data.image_url] : [])
    form.image_url = form.image_urls[0] || ''
    editingPostId.value = Number(id)
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '帖子加载失败'
    ElMessage.error(message)
    goCommunity()
  } finally {
    loading.value = false
  }
}

const submitPost = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const payload = {
        title: form.title.trim(),
        category: form.category,
        content: form.content.trim(),
        image_url: form.image_urls[0] || null,
        image_urls: form.image_urls
      }

      let response
      if (editingPostId.value) {
        response = await updatePost(editingPostId.value, payload)
      } else {
        response = await createPost(payload)
      }

      const result = normalizePayload(response)
      const postId = result?.data?.id || result?.id || editingPostId.value
      ElMessage.success(editingPostId.value ? '帖子已更新' : '帖子已发布')
      if (postId) {
        router.push(`/community/${postId}`)
      } else {
        goCommunity()
      }
    } catch (error) {
      const message = error?.response?.data?.detail || error?.message || '发布失败'
      ElMessage.error(message)
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  const postId = route.query.id
  if (postId) {
    loadPostForEdit(postId)
    return
  }
  resetForm()
})
</script>

<style scoped>
.publish-page {
  display: grid;
  gap: 16px;
}

.glass-card {
  border: 1px solid #e8ebf3;
  border-radius: 22px;
  background: #ffffff;
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
}

.publish-hero {
  padding: 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-kicker {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  padding: 0 10px;
  border-radius: 999px;
  color: #6074df;
  background: #edf2ff;
  font-size: 12px;
}

.publish-hero h1 {
  margin: 10px 0 0;
  font-size: 28px;
  color: #243042;
}

.publish-hero p {
  margin: 8px 0 0;
  color: #6a7281;
  line-height: 1.7;
}

.publish-hero__back {
  min-height: 40px;
  border-radius: 12px;
  color: #526073;
  border-color: #dbe2ee;
}

.publish-card {
  padding: 22px;
}

.publish-form__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
}

.span-2 {
  grid-column: span 2;
}

.publish-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.publish-actions__ghost {
  min-height: 40px;
  border-radius: 12px;
  color: #526073;
  border-color: #dbe2ee;
}

.image-uploader {
  width: 100%;
  padding: 16px;
  border: 1px dashed #d7deea;
  border-radius: 18px;
  background: #f8faff;
}

.image-uploader__input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.image-uploader__empty {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.image-uploader__empty p {
  margin: 0;
  color: #6a7281;
  line-height: 1.7;
}

.image-uploader__preview {
  display: grid;
  gap: 12px;
}

.image-uploader__meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  color: #6a7281;
  font-size: 13px;
}

.image-uploader__media {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 220px;
  padding: 12px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f7f9ff 0%, #eef2fb 100%);
  overflow: hidden;
}

.image-uploader__media img {
  width: 100%;
  height: 100%;
  max-height: 320px;
  object-fit: contain;
  border-radius: 16px;
  background: transparent;
}

.image-uploader__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}

.image-uploader__tile,
.image-uploader__add {
  position: relative;
  min-height: 120px;
  border: 1px solid #dbe2ee;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #f7f9ff 0%, #eef2fb 100%);
}

.image-uploader__tile img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-uploader__remove {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 26px;
  height: 26px;
  border: 0;
  border-radius: 50%;
  background: rgba(36, 48, 66, 0.78);
  color: #ffffff;
  cursor: pointer;
}

.image-uploader__add {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6074df;
  font-weight: 600;
  cursor: pointer;
}

.image-uploader__preview-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-uploader__button {
  min-height: 36px;
  border-radius: 12px;
  color: #526073;
  border-color: #dbe2ee;
}

@media (max-width: 860px) {
  .publish-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .publish-form__grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: span 1;
  }

  .publish-actions {
    flex-direction: column-reverse;
  }

  .publish-actions :deep(.el-button) {
    width: 100%;
  }

  .image-uploader__empty {
    flex-direction: column;
    align-items: stretch;
  }

  .image-uploader__meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>