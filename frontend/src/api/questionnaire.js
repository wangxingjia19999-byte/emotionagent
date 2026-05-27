import request from './request'

export const getScales = () => request.get('/questionnaires/scales')
export const getScaleDetail = (type) => request.get(`/questionnaires/scales/${type}`)
export const submitQuestionnaire = (data) => request.post('/questionnaires/submit', data)
export const getHistory = (params) => request.get('/questionnaires/history', { params })
export const getTrends = (params) => request.get('/questionnaires/trends', { params })
export const getTodayStatus = () => request.get('/questionnaires/today-status')
