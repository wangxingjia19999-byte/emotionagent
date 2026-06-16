import request from './request'

/** 基础版对话 */
export function chatWithAgent(message) {
  return request.post('/agent/chat', { message })
}

/** 增强版对话（含 MCP 工具） */
export function chatWithEnhancedAgent(message, userId = null) {
  return request.post('/agent/chat/enhanced', { message, user_id: userId })
}

/** 多 Agent 对话（Supervisor 架构，含商城推荐） */
export function chatWithMultiAgent(message, userId = null) {
  return request.post('/agent/chat/multi', { message, user_id: userId })
}

/** 获取 Agent 可用工具列表 */
export function getAgentTools() {
  return request.get('/agent/tools')
}

/** 获取 MCP 服务器列表 */
export function getMCPServers() {
  return request.get('/mcp/servers')
}

/** 新增 MCP 服务器 */
export function createMCPServer(data) {
  return request.post('/mcp/servers', data)
}

/** 更新 MCP 服务器 */
export function updateMCPServer(id, data) {
  return request.put(`/mcp/servers/${id}`, data)
}

/** 删除 MCP 服务器 */
export function deleteMCPServer(id) {
  return request.delete(`/mcp/servers/${id}`)
}

/** 测试 MCP 连接 */
export function testMCPConnection(id) {
  return request.post(`/mcp/servers/${id}/test`)
}

/** 获取 MCP 状态 */
export function getMCPStatus() {
  return request.get('/mcp/status')
}

/** 获取预设 MCP 服务器 */
export function getPresetMCPServers() {
  return request.get('/mcp/presets')
}

/** 导入预设到数据库 */
export function loadPresetsToDB() {
  return request.post('/mcp/presets/load')
}

/** 获取 AI 聊天历史会话列表 */
export function getChatSessions(page = 1, pageSize = 20) {
  return request.get('/agent/sessions', { params: { page, page_size: pageSize } })
}

/** 获取单个会话详情（含消息列表） */
export function getChatSessionDetail(sessionId) {
  return request.get(`/agent/sessions/${sessionId}`)
}

/** 上传摄像头帧进行面部表情检测 */
export function detectFacialExpression(imageBase64, userId = null) {
  return request.post('/agent/facial-expression', {
    image_base64: imageBase64,
    user_id: userId,
  })
}

/** 表情自动建议 — 检测到表情后触发 AI 回应 */
export function getExpressionSuggestion(expression, expressionCn) {
  return request.post('/agent/expression-suggestion', {
    expression,
    expression_cn: expressionCn,
  })
}
