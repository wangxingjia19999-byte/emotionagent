import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 120000
})

let isRefreshing = false
let pendingRequests = []

function resolvePending(err) {
  pendingRequests.forEach(({ resolve, reject }) => (err ? reject(err) : resolve()))
  pendingRequests = []
}

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data && typeof data.code !== 'undefined' && data.code !== 0) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
    return data
  },
  async (error) => {
    const status = error.response?.status
    // 优先显示后端返回的 detail 或 message 字段
    let message = error.response?.data?.detail || error.response?.data?.message
    if (!message) {
      if (status === 404) message = '请求的资源不存在'
      else if (status === 401) message = '身份验证失败'
      else if (status === 403) message = '没有访问权限'
      else if (status === 422) message = '请求参数有误'
      else if (status === 423) message = '账户已被锁定'
      else if (status >= 500) message = '服务器内部错误，请稍后重试'
      else if (error.code === 'ERR_NETWORK') message = '无法连接服务器，请检查网络或后端是否启动'
      else message = error.message || '请求失败'
    }

    // 401 → 尝试 refresh token
    if (status === 401 && !error.config._retry) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        if (!isRefreshing) {
          isRefreshing = true
          try {
            const res = await axios.post('http://127.0.0.1:8000/api/auth/refresh', { refresh_token: refreshToken })
            const data = res.data?.data || res.data
            localStorage.setItem('access_token', data.access_token)
            localStorage.setItem('refresh_token', data.refresh_token)
            resolvePending(null)
            // 重试原请求
            error.config._retry = true
            error.config.headers.Authorization = `Bearer ${data.access_token}`
            return request(error.config)
          } catch {
            resolvePending(new Error('refresh_failed'))
            clearAuth()
            router.push('/login')
          } finally {
            isRefreshing = false
          }
        } else {
          await new Promise((resolve, reject) => pendingRequests.push({ resolve, reject }))
          const token = localStorage.getItem('access_token')
          error.config._retry = true
          error.config.headers.Authorization = `Bearer ${token}`
          return request(error.config)
        }
      } else {
        clearAuth()
        router.push('/login')
      }
      return Promise.reject(error)
    }

    if (status === 401) {
      clearAuth()
      router.push('/login')
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

function clearAuth() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
}

export default request
