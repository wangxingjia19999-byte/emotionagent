import request from './request'

// ── MCP 服务器管理 ────────────────────────────
export const getMcpServers = () => request.get('/mcp/servers')

export const createMcpServer = (data) => request.post('/mcp/servers', data)

export const updateMcpServer = (serverId, data) =>
  request.put(`/mcp/servers/${serverId}`, data)

export const deleteMcpServer = (serverId) =>
  request.delete(`/mcp/servers/${serverId}`)

export const getMcpTools = () => request.get('/mcp/tools')

export const getMcpStatus = () => request.get('/mcp/status')

export const testMcpServer = (serverId) =>
  request.post(`/mcp/servers/${serverId}/test`)

export const getMcpPresets = () => request.get('/mcp/presets')

export const loadMcpPresets = () => request.post('/mcp/presets/load')
