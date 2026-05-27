import request from './request'

/** 基础版对话 */
export function chatWithAgent(message) {
  return request.post('/agent/chat', { message })
}

/** 增强版对话（含 MCP 工具） */
export function chatWithEnhancedAgent(message, userId = null) {
  return request.post('/agent/chat/enhanced', { message, user_id: userId })
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
