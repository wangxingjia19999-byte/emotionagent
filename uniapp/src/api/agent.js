import request from './request'

// ── 基础对话 ──────────────────────────────────
export const chatWithAgent = (message) =>
  request.post('/agent/chat', { message })

// ── 增强对话（需登录） ─────────────────────────
export const chatWithEnhancedAgent = (message, userId) =>
  request.post('/agent/chat/enhanced', { message, user_id: userId })

// ── 多 Agent 对话（需登录） ────────────────────
export const chatWithMultiAgent = (message) =>
  request.post('/agent/chat/multi', { message })

// ── 工具列表 ──────────────────────────────────
export const getAgentTools = () => request.get('/agent/tools')

export const getMultiAgentTools = () => request.get('/agent/tools/multi')

// ── 对话历史 ──────────────────────────────────
export const getChatSessions = (page = 1, pageSize = 20) =>
  request.get('/agent/sessions', { params: { page, page_size: pageSize } })

export const getChatSessionDetail = (sessionId) =>
  request.get(`/agent/sessions/${sessionId}`)
