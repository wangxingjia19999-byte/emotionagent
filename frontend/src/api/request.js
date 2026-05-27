import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 120000
})

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
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
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.detail || error.message || '网络错误'
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.error(message)
      router.push('/login')
      return Promise.reject(error)
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
