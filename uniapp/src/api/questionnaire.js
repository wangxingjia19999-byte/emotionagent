import request from './request'

export const getScales = () => request.get('/questionnaires/scales')

export const getScaleDetail = (scaleType) =>
  request.get(`/questionnaires/scales/${scaleType}`)

export const submitQuestionnaire = (data) =>
  request.post('/questionnaires/submit', data)

export const getQuestionnaireHistory = (params = {}) =>
  request.get('/questionnaires/history', { params })

export const getEmotionTrends = (days = 30, scaleType) =>
  request.get('/questionnaires/trends', {
    params: { days, scale_type: scaleType },
  })

export const getTodayStatus = () =>
  request.get('/questionnaires/today-status')
