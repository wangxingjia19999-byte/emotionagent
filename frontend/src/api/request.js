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
    const message = error.response?.data?.detail || error.message || '网络错误'

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
