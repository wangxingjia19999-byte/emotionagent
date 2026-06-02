import request from './request'

// ── 好友搜索 ──────────────────────────────────
export const searchFriends = (q) =>
  request.get('/friends/search', { params: { q } })

// ── 好友请求 ──────────────────────────────────
export const sendFriendRequest = (data) =>
  request.post('/friends/request', data)

export const getFriendRequests = () => request.get('/friends/requests')

export const acceptFriendRequest = (requestId) =>
  request.post('/friends/accept', null, { params: { request_id: requestId } })

export const rejectFriendRequest = (requestId) =>
  request.post('/friends/reject', null, { params: { request_id: requestId } })

// ── 好友列表 ──────────────────────────────────
export const getFriends = () => request.get('/friends')

export const deleteFriend = (friendId) => request.delete(`/friends/${friendId}`)
