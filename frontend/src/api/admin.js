import request from './request'

// 仪表盘
export function getDashboard() {
  return request.get('/admin/dashboard')
}

// 商品分类
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

// 商品
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

// 订单
export function getOrders(params) {
  return request.get('/admin/orders', { params })
}
export function updateOrderStatus(id, status) {
  return request.put(`/admin/orders/${id}/status`, null, { params: { status_val: status } })
}

// 用户
export function getUsers(params) {
  return request.get('/admin/users', { params })
}
export function updateUser(id, data) {
  return request.put(`/admin/users/${id}`, null, { params: data })
}

// 问卷
export function getQuestionnaires(params) {
  return request.get('/admin/questionnaires', { params })
}

// 情绪日志
export function getEmotionLogs(params) {
  return request.get('/admin/emotion-logs', { params })
}

// 帖子
export function getPosts(params) {
  return request.get('/admin/posts', { params })
}
export function deletePost(id) {
  return request.delete(`/admin/posts/${id}`)
}
export function deleteComment(id) {
  return request.delete(`/admin/comments/${id}`)
}
