import request from './request'

export const getProfile = () => request.get('/user/profile')

export const getUserById = (userId) => request.get(`/user/${userId}`)

export const updateProfile = (data) => request.put('/user/profile', data)

export const changePassword = (data) => request.put('/user/password', data)

export const logout = () => request.post('/user/logout')

export const uploadAvatar = (formData) =>
  request.post('/user/avatar', formData, {
    header: { 'Content-Type': 'multipart/form-data' },
  })
