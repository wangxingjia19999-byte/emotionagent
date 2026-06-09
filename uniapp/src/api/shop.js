import request from './request'

// ── 分类 ──────────────────────────────────────
export const getCategories = () => request.get('/shop/categories')

// ── 商品 ──────────────────────────────────────
export const getProducts = (params = {}) =>
  request.get('/shop/products', { params })

export const getProductDetail = (productId) =>
  request.get(`/shop/products/${productId}`)

// ── 购物车 ────────────────────────────────────
export const addToCart = (data) => request.post('/shop/cart', data)

export const getCart = () => request.get('/shop/cart')

export const updateCartItem = (itemId, quantity) =>
  request.put(`/shop/cart/${itemId}`, { quantity })

export const removeCartItem = (itemId) =>
  request.delete(`/shop/cart/${itemId}`)

// ── 收货地址 ──────────────────────────────────
export const createAddress = (data) => request.post('/shop/addresses', data)

export const getAddresses = () => request.get('/shop/addresses')

export const updateAddress = (addressId, data) =>
  request.put(`/shop/addresses/${addressId}`, data)

export const deleteAddress = (addressId) =>
  request.delete(`/shop/addresses/${addressId}`)

// ── 订单 ──────────────────────────────────────
export const createOrder = (data) => request.post('/shop/orders', data)

export const getOrders = (params = {}) =>
  request.get('/shop/orders', { params })

export const getOrderDetail = (orderId) =>
  request.get(`/shop/orders/${orderId}`)

export const payOrder = (orderId) =>
  request.put(`/shop/orders/${orderId}/pay`)

export const cancelOrder = (orderId) =>
  request.put(`/shop/orders/${orderId}/cancel`)
