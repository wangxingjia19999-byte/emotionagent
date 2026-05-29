import request from './request'

// ── 仪表盘 ──
export function getDashboard() {
  return request.get('/admin/dashboard')
}

// ── 商品分类 ──
export function getCategories() {
  return request.get('/admin/categories')
}
export function createCategory(data) {
  return request.post('/admin/categories', null, { params: data })
}
export function updateCategory(id, data) {
  return request.put(`/admin/categories/${id}`, null, { params: data })
}
export function deleteCategory(id) {
  return request.delete(`/admin/categories/${id}`)
}

// ── 商品 ──
export function getProducts(params) {
  return request.get('/admin/products', { params })
}
export function createProduct(data) {
  return request.post('/admin/products', null, { params: data })
}
export function updateProduct(id, data) {
  return request.put(`/admin/products/${id}`, null, { params: data })
}
export function deleteProduct(id) {
  return request.delete(`/admin/products/${id}`)
}

// ── 订单 ──
export function getOrders(params) {
  return request.get('/admin/orders', { params })
}
export function updateOrderStatus(id, status) {
  return request.put(`/admin/orders/${id}/status`, null, { params: { status_val: status } })
}

// ── 用户 ──
export function getUsers(params) {
  return request.get('/admin/users', { params })
}
export function updateUser(id, data) {
  return request.put(`/admin/users/${id}`, null, { params: data })
}
export function getUserDetail(id) {
  return request.get(`/admin/users/${id}/detail`)
}

// ── 问卷 ──
export function getQuestionnaires(params) {
  return request.get('/admin/questionnaires', { params })
}

// ── 情绪日志 ──
export function getEmotionLogs(params) {
  return request.get('/admin/emotion-logs', { params })
}

// ── 帖子 ──
export function getPosts(params) {
  return request.get('/admin/posts', { params })
}
export function deletePost(id) {
  return request.delete(`/admin/posts/${id}`)
}
export function deleteComment(id) {
  return request.delete(`/admin/comments/${id}`)
}

// ── 管理员管理 ──
export function getAdmins() {
  return request.get('/admin/admins')
}
export function createAdmin(data) {
  return request.post('/admin/admins', data)
}
export function updateAdmin(id, data) {
  return request.put(`/admin/admins/${id}`, data)
}
export function deleteAdmin(id) {
  return request.delete(`/admin/admins/${id}`)
}
export function resetAdminPassword(id, newPassword) {
  return request.post(`/admin/admins/${id}/reset-password`, { new_password: newPassword })
}

// ── 危机预警 ──
export function getCrisisAlerts(params) {
  return request.get('/admin/crisis-alerts', { params })
}
export function deleteCrisisAlert(id) {
  return request.delete(`/admin/crisis-alerts/${id}`)
}

// ── 审计日志 ──
export function getAuditLogs(params) {
  return request.get('/admin/audit-logs', { params })
}
export function getAuditActions() {
  return request.get('/admin/audit-logs/actions')
}

// ── 统计分析 ──
export function getStatsOverview() {
  return request.get('/admin/stats/overview')
}
export function getEmotionTrends(days = 30) {
  return request.get('/admin/stats/emotion-trends', { params: { days } })
}
export function getUserGrowth(days = 30) {
  return request.get('/admin/stats/user-growth', { params: { days } })
}
export function getRevenueStats(days = 30) {
  return request.get('/admin/stats/revenue', { params: { days } })
}
