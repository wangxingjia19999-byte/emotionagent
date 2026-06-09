import request from './request'

// ── 帖子列表 ──────────────────────────────────
export const getPosts = (params = {}) =>
  request.get('/posts', { params })

export const getMyPosts = (page = 1, pageSize = 10) =>
  request.get('/posts/my', { params: { page, page_size: pageSize } })

export const getFavoritePosts = (page = 1, pageSize = 10) =>
  request.get('/posts/favorites', { params: { page, page_size: pageSize } })

// ── 帖子 CRUD ─────────────────────────────────
export const getPostDetail = (postId) => request.get(`/posts/${postId}`)

export const createPost = (data) => request.post('/posts', data)

export const updatePost = (postId, data) =>
  request.put(`/posts/${postId}`, data)

export const deletePost = (postId) => request.delete(`/posts/${postId}`)

// ── 互动 ──────────────────────────────────────
export const likePost = (postId) => request.post(`/posts/${postId}/like`)

export const unlikePost = (postId) => request.delete(`/posts/${postId}/like`)

export const hugPost = (postId) => request.post(`/posts/${postId}/hug`)

export const unhugPost = (postId) => request.delete(`/posts/${postId}/hug`)

export const favoritePost = (postId) =>
  request.post(`/posts/${postId}/favorite`)

export const unfavoritePost = (postId) =>
  request.delete(`/posts/${postId}/favorite`)

// ── 评论 ──────────────────────────────────────
export const getComments = (postId, page = 1, pageSize = 10) =>
  request.get(`/posts/${postId}/comments`, {
    params: { page, page_size: pageSize },
  })

export const createComment = (postId, content) =>
  request.post(`/posts/${postId}/comments`, { content })

export const deleteComment = (commentId) =>
  request.delete(`/posts/comments/${commentId}`)
