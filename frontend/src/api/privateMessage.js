import request from './request'

export const sendMessage = (data) => request.post('/private-messages/send', data)
export const getMessageHistory = (friendId, params) => request.get(`/private-messages/history/${friendId}`, { params })
export const getUnreadCount = () => request.get('/private-messages/unread')
export const markAsRead = (friendId) => request.post(`/private-messages/read/${friendId}`)
