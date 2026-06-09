// 图片上传工具
import { API_BASE_URL } from './constants'

/**
 * 选择并上传单张或多张图片
 * @param {Object} options
 * @param {number} options.count - 最大选择数量，默认 1
 * @param {string} options.uploadUrl - 上传端点，默认 /posts/images
 * @param {boolean} options.compressed - 是否压缩，默认 true
 * @returns {Promise<string[]>} 返回上传后的图片 URL 数组
 */
export function chooseAndUploadImages(options = {}) {
  const { count = 1, uploadUrl = '/posts/images', compressed = true } = options

  return new Promise((resolve, reject) => {
    uni.chooseImage({
      count,
      sizeType: compressed ? ['compressed'] : ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success: async (res) => {
        try {
          const urls = await Promise.all(
            res.tempFilePaths.map((fp) => uploadSingle(fp, uploadUrl))
          )
          resolve(urls)
        } catch (err) {
          reject(err)
        }
      },
      fail: (err) => {
        if (err.errMsg !== 'chooseImage:fail cancel') {
          uni.showToast({ title: '选择图片失败', icon: 'none' })
        }
        reject(err)
      },
    })
  })
}

/**
 * 上传单个文件
 */
function uploadSingle(filePath, uploadUrl) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('access_token') || ''
    uni.uploadFile({
      url: API_BASE_URL + uploadUrl,
      filePath,
      name: 'file',
      header: {
        Authorization: `Bearer ${token}`,
      },
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          if (data.code === 0 && data.data) {
            resolve(data.data.image_url || data.data.avatar || data.data)
          } else {
            uni.showToast({
              title: data.message || '上传失败',
              icon: 'none',
            })
            reject(new Error(data.message || '上传失败'))
          }
        } catch {
          reject(new Error('解析上传响应失败'))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败，请检查网络', icon: 'none' })
        reject(err)
      },
    })
  })
}

/**
 * 直接上传已获取的临时文件路径
 * @param {string} filePath - uni.chooseImage 返回的临时路径
 * @param {string} uploadUrl - 上传端点
 * @returns {Promise<string>} 上传后的 URL
 */
export function uploadFile(filePath, uploadUrl = '/posts/images') {
  return uploadSingle(filePath, uploadUrl)
}
