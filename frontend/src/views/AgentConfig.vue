<template>
  <div class="agent-config-page">
    <div class="page-header glass-card">
      <div class="header-left">
        <span class="header-badge">Agent 配置</span>
        <h2>MCP 工具集成管理</h2>
        <p>管理 AI 情绪陪伴 Agent 的外部工具连接，增强知识检索与情绪分析能力。</p>
      </div>
      <div class="header-actions">
        <el-button @click="loadPresets" :loading="loadingPresets">
          <el-icon><Download /></el-icon>
          导入预设配置
        </el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加 MCP 服务器
        </el-button>
      </div>
    </div>

    <!-- 工具概览 -->
    <div class="stats-row">
      <div class="glass-card stat-card">
        <span class="stat-num">{{ servers.length }}</span>
        <span class="stat-label">MCP 服务器</span>
      </div>
      <div class="glass-card stat-card">
        <span class="stat-num">{{ connectedCount }}</span>
        <span class="stat-label">已连接</span>
      </div>
      <div class="glass-card stat-card">
        <span class="stat-num">{{ toolsInfo.length }}</span>
        <span class="stat-label">可用工具</span>
      </div>
      <div class="glass-card stat-card">
        <span class="stat-num">{{ builtinToolCount }}</span>
        <span class="stat-label">内置工具</span>
      </div>
    </div>

    <!-- 服务器列表 -->
    <div class="glass-card section-card">
      <div class="section-title">
        <h3>MCP 服务器列表</h3>
        <el-button text @click="refreshStatus">
          <el-icon><Refresh /></el-icon>
          刷新状态
        </el-button>
      </div>

      <el-table :data="servers" style="width: 100%" v-loading="loadingServers" empty-text="暂无 MCP 服务器配置">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="command" label="命令" width="100" />
        <el-table-column label="参数" min-width="140">
          <template #default="{ row }">
            <el-tag size="small" v-for="(arg, i) in parseArgs(row.args)" :key="i" class="arg-tag">
              {{ arg }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="连接" width="90">
          <template #default="{ row }">
            <span class="conn-status" :class="{ online: row.connected }">
              {{ row.connected ? '已连接' : '未连接' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="testConnection(row)" :loading="testingId === row.id">
              测试
            </el-button>
            <el-button text size="small" @click="editServer(row)">编辑</el-button>
            <el-popconfirm title="确定删除此配置？" @confirm="removeServer(row.id)">
              <template #reference>
                <el-button text size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Agent 工具列表 -->
    <div class="glass-card section-card">
      <div class="section-title">
        <h3>Agent 可用工具</h3>
        <el-button text @click="fetchTools">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <div class="tools-grid">
        <div v-for="tool in toolsInfo" :key="tool.name" class="tool-card">
          <div class="tool-card__header">
            <span class="tool-name">{{ tool.name }}</span>
            <el-tag :type="tool.source === 'builtin' ? '' : 'success'" size="small">
              {{ tool.source === 'builtin' ? '内置' : 'MCP' }}
            </el-tag>
          </div>
          <p class="tool-desc">{{ tool.description }}</p>
        </div>
        <div v-if="toolsInfo.length === 0" class="empty-tools">
          <p>暂无可用工具，请先配置并启用 MCP 服务器</p>
        </div>
      </div>
    </div>

    <!-- 预设推荐 -->
    <div class="glass-card section-card">
      <div class="section-title">
        <h3>推荐 MCP 服务器</h3>
        <span class="section-hint">适合情绪陪伴场景的预设配置</span>
      </div>
      <div class="preset-grid">
        <div v-for="preset in presets" :key="preset.name" class="preset-card">
          <div class="preset-card__header">
            <span class="preset-name">{{ preset.name }}</span>
            <el-tag size="small" type="info">{{ preset.command }}</el-tag>
          </div>
          <p class="preset-desc">{{ preset.description }}</p>
          <div class="preset-env" v-if="preset.env && Object.keys(preset.env).length">
            <span class="env-label">需配置:</span>
            <el-tag v-for="(_, key) in preset.env" :key="key" size="small" class="env-tag">
              {{ key }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingServer ? '编辑 MCP 服务器' : '添加 MCP 服务器'"
      width="520px"
      destroy-on-close
    >
      <el-form :model="form" label-position="top" ref="formRef" :rules="formRules">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="例如 brave_search" :disabled="!!editingServer" />
        </el-form-item>
        <el-form-item label="命令" prop="command">
          <el-input v-model="form.command" placeholder="npx 或 python" />
        </el-form-item>
        <el-form-item label="参数 (JSON 数组)" prop="args">
          <el-input
            v-model="form.args"
            type="textarea"
            :rows="2"
            placeholder='["-y", "@anthropic/mcp-server-brave-search"]'
          />
        </el-form-item>
        <el-form-item label="环境变量 (JSON 对象)" prop="env_vars">
          <el-input
            v-model="form.env_vars"
            type="textarea"
            :rows="3"
            placeholder='{"BRAVE_API_KEY": "your-key-here"}'
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" placeholder="服务器功能描述" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Download, Plus, Refresh, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getMCPServers, createMCPServer, updateMCPServer, deleteMCPServer,
  testMCPConnection, getMCPStatus, getPresetMCPServers, loadPresetsToDB,
  getAgentTools
} from '@/api/agent'

const servers = ref([])
const loadingServers = ref(false)
const loadingPresets = ref(false)
const saving = ref(false)
const testingId = ref(null)
const showAddDialog = ref(false)
const editingServer = ref(null)
const formRef = ref(null)
const toolsInfo = ref([])
const presets = ref([])

const form = ref({
  name: '', command: 'npx', args: '[]', env_vars: '{}', enabled: true, description: ''
})

const formRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  command: [{ required: true, message: '请输入命令', trigger: 'blur' }]
}

const connectedCount = computed(() => servers.value.filter(s => s.connected).length)
const builtinToolCount = computed(() => toolsInfo.value.filter(t => t.source === 'builtin').length)

function parseArgs(argsStr) {
  try { return JSON.parse(argsStr || '[]') } catch { return [] }
}

async function fetchServers() {
  loadingServers.value = true
  try {
    const res = await getMCPServers()
    servers.value = res.data || []
    await refreshStatus()
  } catch (e) {
    ElMessage.error('获取服务器列表失败')
  } finally {
    loadingServers.value = false
  }
}

async function refreshStatus() {
  try {
    const res = await getMCPStatus()
    const statusMap = {}
    ;(res.data || []).forEach(s => { statusMap[s.name] = s })
    servers.value.forEach(s => {
      const st = statusMap[s.name]
      s.connected = st ? st.connected : false
      s.tools_count = st ? st.tools_count : 0
    })
  } catch { /* ignore */ }
}

async function fetchTools() {
  try {
    const res = await getAgentTools()
    toolsInfo.value = res.data?.data || res.data || []
  } catch { ElMessage.error('获取工具列表失败') }
}

async function fetchPresets() {
  try {
    const res = await getPresetMCPServers()
    presets.value = res.data || []
  } catch { /* ignore */ }
}

async function testConnection(row) {
  testingId.value = row.id
  try {
    const res = await testMCPConnection(row.id)
    if (res.data?.success) {
      ElMessage.success(`连接成功，发现 ${(res.data.tools || []).length} 个工具`)
    } else {
      ElMessage.error(`连接失败: ${res.data?.error || '未知错误'}`)
    }
  } catch (e) {
    ElMessage.error('测试请求失败')
  } finally {
    testingId.value = null
  }
}

async function removeServer(id) {
  try {
    await deleteMCPServer(id)
    ElMessage.success('已删除')
    await fetchServers()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

function editServer(row) {
  editingServer.value = row
  form.value = {
    name: row.name,
    command: row.command,
    args: row.args || '[]',
    env_vars: row.env_vars || '{}',
    enabled: row.enabled,
    description: row.description || ''
  }
  showAddDialog.value = true
}

async function submitForm() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const data = { ...form.value }
    if (editingServer.value) {
      delete data.name
      await updateMCPServer(editingServer.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createMCPServer(data)
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    editingServer.value = null
    await fetchServers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function loadPresets() {
  loadingPresets.value = true
  try {
    const res = await loadPresetsToDB()
    ElMessage.success(`已导入 ${res.data?.count || 0} 个预设配置`)
    await fetchServers()
  } catch (e) {
    ElMessage.error('导入失败')
  } finally {
    loadingPresets.value = false
  }
}

onMounted(() => {
  fetchServers()
  fetchTools()
  fetchPresets()
})
</script>

<style scoped>
.agent-config-page {
  display: grid;
  gap: 20px;
  padding: 0;
}

.glass-card {
  padding: 24px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 40px rgba(109, 109, 173, 0.1);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: wrap;
}

.header-badge {
  display: inline-flex;
  min-height: 28px;
  padding: 0 10px;
  align-items: center;
  border-radius: 999px;
  font-size: 13px;
  color: #6074df;
  background: #edf2ff;
}

.header-left h2 {
  margin: 10px 0 4px;
  font-size: 20px;
  color: #2f3142;
}

.header-left p {
  margin: 0;
  font-size: 13px;
  color: #7a8191;
  max-width: 480px;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 700px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 20px;
  align-items: center;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: #2f3142;
}

.stat-label {
  font-size: 13px;
  color: #7a8191;
}

/* 区块 */
.section-card {
  display: grid;
  gap: 16px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title h3 {
  margin: 0;
  font-size: 16px;
  color: #2f3142;
}

.section-hint {
  font-size: 12px;
  color: #b0b7c4;
}

/* 表格 */
.arg-tag {
  margin: 1px 3px;
}

.conn-status {
  font-size: 12px;
  color: #b0b7c4;
}

.conn-status.online {
  color: #43a78d;
}

/* 工具网格 */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}

.tool-card {
  padding: 16px;
  border-radius: 16px;
  background: #fafbfe;
  border: 1px solid #f0f1f6;
}

.tool-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.tool-name {
  font-weight: 600;
  font-size: 14px;
  color: #2f3142;
}

.tool-desc {
  margin: 0;
  font-size: 12px;
  color: #7a8191;
  line-height: 1.6;
}

.empty-tools {
  grid-column: 1 / -1;
  text-align: center;
  padding: 32px;
  color: #b0b7c4;
}

/* 预设卡片 */
.preset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.preset-card {
  padding: 16px;
  border-radius: 16px;
  background: #f8f9fc;
  border: 1px solid #eeeff4;
}

.preset-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.preset-name {
  font-weight: 600;
  font-size: 14px;
  color: #2f3142;
}

.preset-desc {
  margin: 0 0 10px;
  font-size: 13px;
  color: #5f6475;
  line-height: 1.6;
}

.preset-env {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.env-label {
  font-size: 12px;
  color: #b0b7c4;
}

.env-tag {
  font-size: 11px;
}
</style>
