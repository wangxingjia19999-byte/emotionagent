// ── uni.request 封装 + 拦截器 + Token 刷新 ──────────────
import { API_BASE_URL } from '@/utils/constants'

let isRefreshing = false
let pendingRequests = []

// ── 核心请求函数 ──────────────────────────────
function baseRequest(config) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: API_BASE_URL + config.url,
      method: config.method || 'GET',
      data: config.data,
      header: config.header || {},
      timeout: config.timeout || 120000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject({
            status: res.statusCode,
            data: res.data,
            message: res.data?.detail || res.data?.message || '请求失败',
          })
        }
      },
      fail: (err) => {
        reject({
          networkError: true,
          message: err.errMsg || '网络连接失败，请检查网络',
        })
      },
    })
  })
}

// ── 请求拦截器 ──────────────────────────────────
function buildConfig(config) {
  const header = { ...config.header }
  const token = uni.getStorageSync('access_token')
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  // 清理空 query params（防止 FastAPI 422）
  if (config.params) {
    const cleanParams = {}
    for (const [key, value] of Object.entries(config.params)) {
      if (value !== null && value !== undefined && value !== '') {
        cleanParams[key] = value
      }
    }
    config.params = cleanParams
  }

  return { ...config, header }
}

// ── 响应拦截器 ──────────────────────────────────
async function handleResponse(config, response) {
  const data = response

  // 后端统一 code 检查
  if (data && data.code !== undefined && data.code !== 0) {
    uni.showToast({
      title: data.message || '操作失败',
      icon: 'none',
      duration: 2000,
    })
    throw new Error(data.message || '操作失败')
  }
  return data
}

async function handleError(config, error) {
  // Token 过期 → 尝试刷新
  if (error.status === 401 && !config._retry) {
    return handleTokenRefresh(config)
  }

  // 格式化错误提示
  const messages = {
    400: '请求参数有误',
    403: '没有操作权限',
    404: '请求的资源不存在',
    422: '请求参数校验失败',
    423: '账户已被锁定，请稍后再试',
    429: '操作过于频繁，请稍后再试',
  }
  const msg =
    messages[error.status] ||
    error.message ||
    `服务器错误(${error.status})`

  if (!error._silent) {
    uni.showToast({ title: msg, icon: 'none', duration: 2000 })
  }
  throw error
}

// ── Token 刷新（与 Web 版逻辑一致） ─────────────
function handleTokenRefresh(originalConfig) {
  const refreshToken = uni.getStorageSync('refresh_token')
  if (!refreshToken) {
    clearAuthAndGoLogin()
    return Promise.reject(new Error('登录已过期，请重新登录'))
  }

  if (!isRefreshing) {
    isRefreshing = true
    return baseRequest({
      url: '/auth/refresh',
      method: 'POST',
      data: { refresh_token: refreshToken },
    })
      .then((res) => {
        const accessToken = res.access_token || res.data?.access_token
        const newRefreshToken = res.refresh_token || res.data?.refresh_token
        if (accessToken) {
          uni.setStorageSync('access_token', accessToken)
        }
        if (newRefreshToken) {
          uni.setStorageSync('refresh_token', newRefreshToken)
        }
        // 解决排队的请求
        pendingRequests.forEach((cb) => cb.resolve())
        pendingRequests = []
        return accessToken
      })
      .catch(() => {
        pendingRequests.forEach((cb) => cb.reject(new Error('刷新失败')))
        pendingRequests = []
        clearAuthAndGoLogin()
        throw new Error('登录已过期，请重新登录')
      })
      .finally(() => {
        isRefreshing = false
      })
      .then(() => {
        // 重试原请求
        const retryConfig = buildConfig({ ...originalConfig, _retry: true })
        return baseRequest(retryConfig).then((res) =>
          handleResponse(retryConfig, res)
        )
      })
  }

  // 已有刷新在进行中 → 排队等待
  return new Promise((resolve, reject) => {
    pendingRequests.push({
      resolve: () => {
        const retryConfig = buildConfig({ ...originalConfig, _retry: true })
        baseRequest(retryConfig)
          .then((res) => handleResponse(retryConfig, res).then(resolve))
          .catch(reject)
      },
      reject,
    })
  })
}

function clearAuthAndGoLogin() {
  uni.removeStorageSync('access_token')
  uni.removeStorageSync('refresh_token')
  uni.removeStorageSync('user')
  // 跳转到登录页
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  if (currentPage && currentPage.route !== 'pages/auth/login') {
    uni.reLaunch({ url: '/pages/auth/login' })
  }
}

// ── 公共请求方法 ───────────────────────────────
const request = {
  async get(url, config = {}) {
    const fullConfig = buildConfig({ ...config, url, method: 'GET' })
    try {
      const res = await baseRequest(fullConfig)
      return handleResponse(fullConfig, res)
    } catch (err) {
      return handleError(fullConfig, err)
    }
  },

  async post(url, data = {}, config = {}) {
    const fullConfig = buildConfig({ ...config, url, method: 'POST', data })
    try {
      const res = await baseRequest(fullConfig)
      return handleResponse(fullConfig, res)
    } catch (err) {
      return handleError(fullConfig, err)
    }
  },

  async put(url, data = {}, config = {}) {
    const fullConfig = buildConfig({ ...config, url, method: 'PUT', data })
    try {
      const res = await baseRequest(fullConfig)
      return handleResponse(fullConfig, res)
    } catch (err) {
      return handleError(fullConfig, err)
    }
  },

  async delete(url, config = {}) {
    const fullConfig = buildConfig({ ...config, url, method: 'DELETE' })
    try {
      const res = await baseRequest(fullConfig)
      return handleResponse(fullConfig, res)
    } catch (err) {
      return handleError(fullConfig, err)
    }
  },

  /**
   * 静默请求（不弹出 toast 错误提示）
   */
  async silent(config) {
    return this.get(config.url, { ...config, _silent: true })
  },
}

export default request
