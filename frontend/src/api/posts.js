import request from './request'

export const createPost = (data) => request.post('/posts', data)
export const getPosts = (params) => request.get('/posts', { params })
export const getPostDetail = (id) => request.get(`/posts/${id}`)
export const updatePost = (id, data) => request.put(`/posts/${id}`, data)
export const uploadPostImage = (file) => {
	const formData = new FormData()
	formData.append('file', file)
	return request.post('/posts/images', formData)
}
export const deletePost = (id) => request.delete(`/posts/${id}`)
export const getComments = (postId, params) => request.get(`/posts/${postId}/comments`, { params })
export const createComment = (postId, data) => request.post(`/posts/${postId}/comments`, data)
export const deleteComment = (commentId) => request.delete(`/comments/${commentId}`)
export const likePost = (postId) => request.post(`/posts/${postId}/like`)
export const unlikePost = (postId) => request.delete(`/posts/${postId}/like`)
export const favoritePost = (postId) => request.post(`/posts/${postId}/favorite`)
export const unfavoritePost = (postId) => request.delete(`/posts/${postId}/favorite`)
export const hugPost = (postId) => request.post(`/posts/${postId}/hug`)
export const unhugPost = (postId) => request.delete(`/posts/${postId}/hug`)
export const getMyPosts = (params) => request.get('/posts/my', { params })
export const getFavoritePosts = (params) => request.get('/posts/favorites', { params })