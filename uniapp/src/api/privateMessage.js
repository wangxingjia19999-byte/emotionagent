import request from './request'

export const sendMessage = (data) =>
  request.post('/private-messages/send', data)

export const getMessageHistory = (friendId, page = 1, pageSize = 30) =>
  request.get(`/private-messages/history/${friendId}`, {
    params: { page, page_size: pageSize },
  })

export const getUnreadMessages = () =>
  request.get('/private-messages/unread')

export const markMessagesRead = (friendId) =>
  request.post(`/private-messages/read/${friendId}`)
