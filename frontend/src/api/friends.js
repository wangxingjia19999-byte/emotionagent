import request from './request'

export const searchUsers = (q) => request.get('/friends/search', { params: { q } })
export const sendFriendRequest = (data) => request.post('/friends/request', data)
export const getFriendRequests = () => request.get('/friends/requests')
export const acceptRequest = (requestId) => request.post('/friends/accept', null, { params: { request_id: requestId } })
export const rejectRequest = (requestId) => request.post('/friends/reject', null, { params: { request_id: requestId } })
export const getFriends = () => request.get('/friends')
export const removeFriend = (friendId) => request.delete(`/friends/${friendId}`)
