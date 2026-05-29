import request from './request'

export const sendVerifyCode = (data) => request.post('/auth/send-verify-code', data)
export const register = (data) => request.post('/auth/register', data)
export const login = (data) => request.post('/auth/login', data)

// ── 管理员认证 ──
export const adminLogin = (data) => request.post('/auth/admin/login', data)
export const adminLogout = () => request.post('/auth/admin/logout')
export const adminChangePassword = (data) => request.post('/auth/admin/change-password', data)
