import request from './request'

// 分类
export function getCategories() {
  return request.get('/shop/categories')
}

// 商品
export function getProducts(params) {
  return request.get('/shop/products', { params })
}

export function getProduct(id) {
  return request.get(`/shop/products/${id}`)
}

// 购物车
export function addToCart(data) {
  return request.post('/shop/cart', data)
}

export function getCart() {
  return request.get('/shop/cart')
}

export function updateCartItem(id, data) {
  return request.put(`/shop/cart/${id}`, data)
}

export function removeCartItem(id) {
  return request.delete(`/shop/cart/${id}`)
}

// 地址
export function createAddress(data) {
  return request.post('/shop/addresses', data)
}

export function getAddresses() {
  return request.get('/shop/addresses')
}

export function updateAddress(id, data) {
  return request.put(`/shop/addresses/${id}`, data)
}

export function deleteAddress(id) {
  return request.delete(`/shop/addresses/${id}`)
}

// 订单
export function createOrder(data) {
  return request.post('/shop/orders', data)
}

export function getOrders(params) {
  return request.get('/shop/orders', { params })
}

export function getOrder(id) {
  return request.get(`/shop/orders/${id}`)
}

export function payOrder(id) {
  return request.put(`/shop/orders/${id}/pay`)
}

export function cancelOrder(id) {
  return request.put(`/shop/orders/${id}/cancel`)
}
