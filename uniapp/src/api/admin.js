import request from './request'

// ── 仪表盘 ────────────────────────────────────
export const getAdminDashboard = () => request.get('/admin/dashboard')

// ── 分类管理 ──────────────────────────────────
export const getAdminCategories = () => request.get('/admin/categories')

export const createAdminCategory = (params) =>
  request.post('/admin/categories', null, { params })

export const updateAdminCategory = (catId, params) =>
  request.put(`/admin/categories/${catId}`, null, { params })

export const deleteAdminCategory = (catId) =>
  request.delete(`/admin/categories/${catId}`)

// ── 商品管理 ──────────────────────────────────
export const getAdminProducts = (params = {}) =>
  request.get('/admin/products', { params })

export const createAdminProduct = (params) =>
  request.post('/admin/products', null, { params })

export const updateAdminProduct = (productId, params) =>
  request.put(`/admin/products/${productId}`, null, { params })

export const deleteAdminProduct = (productId) =>
  request.delete(`/admin/products/${productId}`)

// ── 订单管理 ──────────────────────────────────
export const getAdminOrders = (params = {}) =>
  request.get('/admin/orders', { params })

export const updateAdminOrderStatus = (orderId, statusVal) =>
  request.put(`/admin/orders/${orderId}/status`, null, {
    params: { status_val: statusVal },
  })

// ── 用户管理 ──────────────────────────────────
export const getAdminUsers = (params = {}) =>
  request.get('/admin/users', { params })

export const updateAdminUser = (userId, params) =>
  request.put(`/admin/users/${userId}`, null, { params })

export const getAdminUserDetail = (userId) =>
  request.get(`/admin/users/${userId}/detail`)

// ── 问卷管理 ──────────────────────────────────
export const getAdminQuestionnaires = (params = {}) =>
  request.get('/admin/questionnaires', { params })

// ── 情绪日志 ──────────────────────────────────
export const getAdminEmotionLogs = (params = {}) =>
  request.get('/admin/emotion-logs', { params })

// ── 帖子管理 ──────────────────────────────────
export const getAdminPosts = (params = {}) =>
  request.get('/admin/posts', { params })

export const deleteAdminPost = (postId) =>
  request.delete(`/admin/posts/${postId}`)

export const deleteAdminComment = (commentId) =>
  request.delete(`/admin/comments/${commentId}`)

// ── 管理员管理 ────────────────────────────────
export const getAdmins = () => request.get('/admin/admins')

export const createAdmin = (data) => request.post('/admin/admins', data)

export const updateAdmin = (adminId, data) =>
  request.put(`/admin/admins/${adminId}`, data)

export const deleteAdmin = (adminId) =>
  request.delete(`/admin/admins/${adminId}`)

export const resetAdminPassword = (adminId, newPassword) =>
  request.post(`/admin/admins/${adminId}/reset-password`, { new_password: newPassword })

// ── 危机预警 ──────────────────────────────────
export const getCrisisAlerts = (params = {}) =>
  request.get('/admin/crisis-alerts', { params })

export const deleteCrisisAlert = (alertId) =>
  request.delete(`/admin/crisis-alerts/${alertId}`)

// ── 审计日志 ──────────────────────────────────
export const getAuditLogs = (params = {}) =>
  request.get('/admin/audit-logs', { params })

export const getAuditLogActions = () =>
  request.get('/admin/audit-logs/actions')

// ── 统计分析 ──────────────────────────────────
export const getEmotionTrends = (days = 30) =>
  request.get('/admin/stats/emotion-trends', { params: { days } })

export const getUserGrowth = (days = 30) =>
  request.get('/admin/stats/user-growth', { params: { days } })

export const getRevenueStats = (days = 30) =>
  request.get('/admin/stats/revenue', { params: { days } })

export const getStatsOverview = () =>
  request.get('/admin/stats/overview')
