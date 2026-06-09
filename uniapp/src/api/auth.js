import request from './request'

// ── 用户认证 ──────────────────────────────────
export const sendVerifyCode = (email) =>
  request.post('/auth/send-verify-code', { email })

export const register = (data) => request.post('/auth/register', data)

export const login = (data) => request.post('/auth/login', data)

export const refreshToken = (refresh_token) =>
  request.post('/auth/refresh', { refresh_token })

// ── 管理员认证 ────────────────────────────────
export const adminLogin = (data) => request.post('/auth/admin/login', data)

export const adminRefreshToken = (refresh_token) =>
  request.post('/auth/admin/refresh', { refresh_token })

export const adminLogout = () => request.post('/auth/admin/logout')

export const adminChangePassword = (data) =>
  request.post('/auth/admin/change-password', data)
