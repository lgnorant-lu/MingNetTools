<template>
  <div class="connection-lab-container pixel-tcp-lab scanlines">
    <!-- 页面标题 -->
    <div class="page-header pixel-header">
      <h1 class="page-title glitch-text" data-text="TCP COMMUNICATION LAB">
        <el-icon><Link /></el-icon>
        TCP COMMUNICATION LAB
      </h1>
      <p class="page-subtitle">TCP服务器和客户端通信测试平台</p>
    </div>

    <!-- 主要内容区域 -->
    <el-row :gutter="20">
      <!-- 服务器控制区域 -->
      <el-col :span="12" :xs="24" :sm="24" :md="12" :lg="12">
        <div class="pixel-card server-section">
          <div class="card-header">
            <span class="glitch-text" data-text="TCP SERVER">TCP SERVER</span>
            <div class="status-indicator" :class="serverStatus">
              <div class="status-dot"></div>
              <span>{{ serverStatus === 'running' ? 'RUNNING' : 'STOPPED' }}</span>
            </div>
          </div>

          <!-- 服务器配置 -->
          <div class="config-section">
            <div class="config-title">SERVER CONFIG</div>
            <div class="config-grid">
              <div class="config-item">
                <label class="config-label">HOST ADDRESS</label>
                <input
                  v-model="serverConfig.host"
                  :disabled="serverStatus === 'running'"
                  class="pixel-input"
                  placeholder="127.0.0.1"
                />
              </div>
              <div class="config-item">
                <label class="config-label">PORT</label>
                <input
                  v-model.number="serverConfig.port"
                  type="number"
                  :min="1024"
                  :max="65535"
                  :disabled="serverStatus === 'running'"
                  class="pixel-input"
                  placeholder="8888"
                />
              </div>
              <div class="config-item">
                <label class="config-label">MAX CONNECTIONS</label>
                <input
                  v-model.number="serverConfig.maxConnections"
                  type="number"
                  :min="1"
                  :max="100"
                  :disabled="serverStatus === 'running'"
                  class="pixel-input"
                  placeholder="10"
                />
              </div>
              <div class="config-item">
                <label class="config-label">TIMEOUT (SEC)</label>
                <input
                  v-model.number="serverConfig.timeout"
                  type="number"
                  :min="5"
                  :max="300"
                  :disabled="serverStatus === 'running'"
                  class="pixel-input"
                  placeholder="30"
                />
              </div>
            </div>
          </div>

          <!-- 服务器操作 -->
          <div class="action-section">
            <button
              v-if="serverStatus !== 'running'"
              @click="startServer"
              class="pixel-btn action-btn start-btn"
            >
              <el-icon><VideoPlay /></el-icon>
              <span>START SERVER</span>
            </button>
            
            <button
              v-else
              @click="stopServer"
              class="pixel-btn action-btn stop-btn"
            >
              <el-icon><VideoPause /></el-icon>
              <span>STOP SERVER</span>
            </button>
          </div>

          <!-- 服务器统计 -->
          <div v-if="serverStatus === 'running'" class="stats-section">
            <div class="stats-title">SERVER STATISTICS</div>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ serverStats.currentConnections }}</div>
                <div class="stat-label">CURRENT</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ serverStats.totalConnections }}</div>
                <div class="stat-label">TOTAL</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ serverStats.messageCount }}</div>
                <div class="stat-label">MESSAGES</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 客户端控制区域 -->
      <el-col :span="12" :xs="24" :sm="24" :md="12" :lg="12">
        <div class="pixel-card client-section">
          <div class="card-header">
            <span class="glitch-text" data-text="TCP CLIENT">TCP CLIENT</span>
            <div class="status-indicator" :class="clientStatus">
              <div class="status-dot"></div>
              <span>{{ clientStatus === 'connected' ? 'CONNECTED' : 'DISCONNECTED' }}</span>
            </div>
          </div>

          <!-- 连接配置 -->
          <div class="config-section">
            <div class="config-title">CONNECTION CONFIG</div>
            <div class="config-grid">
              <div class="config-item">
                <label class="config-label">SERVER HOST</label>
                <input
                  v-model="clientConfig.host"
                  :disabled="clientStatus === 'connected'"
                  class="pixel-input"
                  placeholder="127.0.0.1"
                />
              </div>
              <div class="config-item">
                <label class="config-label">SERVER PORT</label>
                <input
                  v-model.number="clientConfig.port"
                  type="number"
                  :min="1024"
                  :max="65535"
                  :disabled="clientStatus === 'connected'"
                  class="pixel-input"
                  placeholder="8888"
                />
              </div>
              <div class="config-item">
                <label class="config-label">TIMEOUT (SEC)</label>
                <input
                  v-model.number="clientConfig.timeout"
                  type="number"
                  :min="5"
                  :max="60"
                  :disabled="clientStatus === 'connected'"
                  class="pixel-input"
                  placeholder="10"
                />
              </div>
              <div class="config-item full-width">
                <label class="config-label">
                  <input
                    type="checkbox"
                    v-model="clientConfig.autoReconnect"
                    :disabled="clientStatus === 'connected'"
                    class="pixel-checkbox"
                  />
                  AUTO RECONNECT
                </label>
              </div>
            </div>
          </div>

          <!-- 客户端操作 -->
          <div class="action-section">
            <button
              v-if="clientStatus !== 'connected'"
              @click="connectClient"
              :disabled="!canConnect"
              class="pixel-btn action-btn connect-btn"
            >
              <el-icon><Link /></el-icon>
              <span>CONNECT</span>
            </button>
            
            <button
              v-else
              @click="disconnectClient"
              class="pixel-btn action-btn disconnect-btn"
            >
              <el-icon><Close /></el-icon>
              <span>DISCONNECT</span>
            </button>
          </div>

          <!-- 快速连接 -->
          <div class="quick-actions">
            <div class="quick-title">QUICK ACTIONS</div>
            <div class="quick-buttons">
              <button @click="connectToLocal" class="pixel-btn quick-btn">
                <el-icon><Monitor /></el-icon>
                <span>LOCAL</span>
              </button>
              <button @click="connectToDemo" class="pixel-btn quick-btn">
                <el-icon><Connection /></el-icon>
                <span>DEMO</span>
              </button>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 通信区域 -->
    <div class="communication-section">
      <div class="pixel-card">
        <div class="card-header">
          <span class="glitch-text" data-text="COMMUNICATION LOG">COMMUNICATION LOG</span>
          <div class="header-actions">
            <button @click="clearMessages" :disabled="messages.length === 0" class="pixel-btn small-btn">
              <el-icon><Delete /></el-icon>
              <span>CLEAR</span>
            </button>
            <button @click="exportMessages" :disabled="messages.length === 0" class="pixel-btn small-btn">
              <el-icon><Download /></el-icon>
              <span>EXPORT</span>
            </button>
          </div>
        </div>

        <!-- 消息输入区域 -->
        <div v-if="canSendMessage" class="message-input-section">
          <div class="input-row">
            <select v-model="messageType" class="pixel-select">
              <option value="text">TEXT</option>
              <option value="broadcast">BROADCAST</option>
              <option value="system">SYSTEM</option>
            </select>
            <input
              v-model="messageInput"
              @keyup.enter="sendMessage"
              placeholder="Type your message..."
              class="pixel-input message-input"
            />
            <button @click="sendMessage" :disabled="!messageInput.trim()" class="pixel-btn send-btn">
              <el-icon><Promotion /></el-icon>
              <span>SEND</span>
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="messages-container">
          <div v-if="messages.length === 0" class="empty-messages">
            <div class="empty-icon">📡</div>
            <div class="empty-text">NO MESSAGES YET</div>
            <div class="empty-subtitle">Start communicating to see logs here</div>
          </div>
          <div v-else class="messages-list" ref="messagesContainer">
            <div 
              v-for="(message, index) in messages" 
              :key="index"
              class="message-item"
              :class="[message.type, `message-${index % 4}`]"
            >
              <div class="message-header">
                <span class="message-time">{{ message.time }}</span>
                <span class="message-source">{{ message.source }}</span>
                <div class="message-type-tag" :class="message.type">
                  {{ getMessageTypeText(message.type) }}
                </div>
              </div>
              <div class="message-content">{{ message.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Link, 
  VideoPlay, 
  VideoPause, 
  Close, 
  Monitor, 
  Connection, 
  Delete, 
  Download, 
  Promotion 
} from '@element-plus/icons-vue'

// 类型定义
interface TCPConnection {
  id: string
  type: 'server' | 'client'
  status: 'running' | 'connected' | 'disconnected' | 'stopped'
  host?: string
  port?: number
  [key: string]: any
}

interface ConnectionData {
  total_connections: number
  servers: number
  clients: number
  connections: TCPConnection[]
}

// 响应式状态
const isMobile = ref(false)

// 服务器配置
const serverConfig = ref({
  host: '127.0.0.1',
  port: 8888,
  maxConnections: 10,
  timeout: 30
})

// 客户端配置
const clientConfig = ref({
  host: '127.0.0.1',
  port: 8888,
  timeout: 10,
  autoReconnect: false
})

// 状态
const serverStatus = ref<'stopped' | 'running'>('stopped')
const clientStatus = ref<'disconnected' | 'connected'>('disconnected')

// 统计信息
const serverStats = ref({
  currentConnections: 0,
  totalConnections: 0,
  messageCount: 0
})

// 真实的服务器和客户端ID
const realServerId = ref<string | null>(null)
const realClientId = ref<string | null>(null)

// 消息相关
const messages = ref<any[]>([])
const messageInput = ref('')
const messageType = ref('text')

// 引用
const messagesContainer = ref<HTMLElement>()

// API调用函数
const fetchConnectionStats = async () => {
  try {
    const response = await fetch('/api/v1/tcp/connections')
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        const connectionData = data.data as ConnectionData
        const connections = connectionData.connections || []
        serverStats.value.totalConnections = connectionData.total_connections || 0
        
        // 计算当前连接数（只统计connected和running状态的连接）
        const activeConnections = connections.filter((conn: TCPConnection) => 
          conn.status === 'running' || conn.status === 'connected'
        )
        serverStats.value.currentConnections = activeConnections.length
      }
    }
  } catch (error) {
    console.error('获取连接状态失败:', error)
  }
}

// 检查是否为移动端
const checkIfMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// 计算属性
const canConnect = computed(() => {
  return clientConfig.value.host.trim() !== '' && clientConfig.value.port > 0
})

const canSendMessage = computed(() => {
  return serverStatus.value === 'running' || clientStatus.value === 'connected'
})

// 服务器操作
const startServer = async () => {
  try {
    const response = await fetch('/api/v1/tcp/server/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        host: serverConfig.value.host,
        port: serverConfig.value.port,
        max_connections: serverConfig.value.maxConnections,
        timeout: serverConfig.value.timeout,
        ssl_enabled: false
      })
    })

    if (response.ok) {
      const result = await response.json()
      if (result.success) {
        realServerId.value = result.data.server_id
        serverStatus.value = 'running'
        addMessage('system', 'server', `TCP服务器已启动，监听 ${serverConfig.value.host}:${serverConfig.value.port}`)
        ElMessage.success('TCP服务器启动成功')
        
        // 开始定期更新统计信息
        startStatsUpdate()
      } else {
        ElMessage.error(`服务器启动失败: ${result.message}`)
      }
    } else {
      ElMessage.error('服务器启动请求失败')
    }
  } catch (error) {
    console.error('启动服务器错误:', error)
    ElMessage.error('启动服务器时发生错误')
  }
}

const stopServer = async () => {
  if (!realServerId.value) {
    serverStatus.value = 'stopped'
    serverStats.value = { currentConnections: 0, totalConnections: 0, messageCount: 0 }
    addMessage('system', 'server', 'TCP服务器已停止')
    ElMessage.warning('TCP服务器已停止')
    return
  }

  try {
    const response = await fetch(`/api/v1/tcp/server/${realServerId.value}/stop`, {
      method: 'POST'
    })

    if (response.ok) {
      const result = await response.json()
      if (result.success) {
        realServerId.value = null
        serverStatus.value = 'stopped'
        serverStats.value = { currentConnections: 0, totalConnections: 0, messageCount: 0 }
        addMessage('system', 'server', 'TCP服务器已停止')
        ElMessage.warning('TCP服务器已停止')
      } else {
        ElMessage.error(`服务器停止失败: ${result.message}`)
      }
    } else {
      ElMessage.error('服务器停止请求失败')
    }
  } catch (error) {
    console.error('停止服务器错误:', error)
    ElMessage.error('停止服务器时发生错误')
  }
}

// 客户端操作
const connectClient = async () => {
  try {
    const response = await fetch('/api/v1/tcp/client/connect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        host: clientConfig.value.host,
        port: clientConfig.value.port,
        timeout: clientConfig.value.timeout,
        auto_reconnect: clientConfig.value.autoReconnect,
        ssl_enabled: false
      })
    })

    if (response.ok) {
      const result = await response.json()
      if (result.success) {
        realClientId.value = result.data.client_id
        clientStatus.value = 'connected'
        addMessage('system', 'client', `已连接到服务器 ${clientConfig.value.host}:${clientConfig.value.port}`)
        ElMessage.success('客户端连接成功')
        
        // 更新统计信息
        await fetchConnectionStats()
      } else {
        ElMessage.error(`客户端连接失败: ${result.message}`)
      }
    } else {
      ElMessage.error('客户端连接请求失败')
    }
  } catch (error) {
    console.error('连接客户端错误:', error)
    ElMessage.error('连接客户端时发生错误')
  }
}

const disconnectClient = async () => {
  if (!realClientId.value) {
    clientStatus.value = 'disconnected'
    addMessage('system', 'client', '已断开与服务器的连接')
    ElMessage.warning('客户端已断开连接')
    return
  }

  try {
    const response = await fetch(`/api/v1/tcp/client/${realClientId.value}/disconnect`, {
      method: 'POST'
    })

    if (response.ok) {
      const result = await response.json()
      if (result.success) {
        realClientId.value = null
        clientStatus.value = 'disconnected'
        addMessage('system', 'client', '已断开与服务器的连接')
        ElMessage.warning('客户端已断开连接')
        
        // 更新统计信息
        await fetchConnectionStats()
      } else {
        ElMessage.error(`客户端断开失败: ${result.message}`)
      }
    } else {
      ElMessage.error('客户端断开请求失败')
    }
  } catch (error) {
    console.error('断开客户端错误:', error)
    ElMessage.error('断开客户端时发生错误')
  }
}

// 定期更新统计信息
let statsUpdateInterval: number | null = null

const startStatsUpdate = () => {
  // 立即更新一次
  fetchConnectionStats()
  
  // 每5秒更新一次
  statsUpdateInterval = setInterval(() => {
    if (serverStatus.value === 'running') {
      fetchConnectionStats()
    } else {
      stopStatsUpdate()
    }
  }, 5000)
}

const stopStatsUpdate = () => {
  if (statsUpdateInterval) {
    clearInterval(statsUpdateInterval)
    statsUpdateInterval = null
  }
}

// 快速连接
const connectToLocal = () => {
  clientConfig.value.host = serverConfig.value.host
  clientConfig.value.port = serverConfig.value.port
  ElMessage.success('已设置为本地服务器地址')
}

const connectToDemo = () => {
  clientConfig.value.host = 'demo.example.com'
  clientConfig.value.port = 8080
  ElMessage.success('已设置为演示服务器地址')
}

// 消息操作
const sendMessage = () => {
  if (!messageInput.value.trim()) return

  const content = messageInput.value.trim()
  const source = clientStatus.value === 'connected' ? 'client' : 'server'
  
  addMessage(messageType.value, source, content)
  serverStats.value.messageCount++
  
  messageInput.value = ''
  ElMessage.success('消息发送成功')
}

const addMessage = (type: string, source: string, content: string) => {
  const message = {
    time: new Date().toLocaleTimeString(),
    type,
    source,
    content,
    timestamp: Date.now()
  }
  
  messages.value.push(message)
  
  // 自动滚动到底部
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const clearMessages = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有通信消息吗？', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    messages.value = []
    ElMessage.success('消息已清空')
  } catch {
    // 用户取消
  }
}

const exportMessages = () => {
  const csvContent = [
    'Time,Type,Source,Content',
    ...messages.value.map(msg => 
      `"${msg.time}","${msg.type}","${msg.source}","${msg.content}"`
    )
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `tcp_communication_log_${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('通信日志已导出')
}

// 辅助函数
const getMessageTagType = (type: string) => {
  switch (type) {
    case 'system': return 'info'
    case 'broadcast': return 'warning'
    case 'text': return 'success'
    default: return 'info'
  }
}

const getMessageTypeText = (type: string) => {
  switch (type) {
    case 'system': return '系统'
    case 'broadcast': return '广播'
    case 'text': return '文本'
    default: return '未知'
  }
}

// 组件生命周期
onMounted(() => {
  addMessage('system', 'system', 'TCP通信实验室已启动')
  checkIfMobile()
  window.addEventListener('resize', checkIfMobile)
  
  // 页面加载时获取一次连接状态
  fetchConnectionStats()
})

onUnmounted(() => {
  // 清理资源
  stopStatsUpdate()
  
  if (serverStatus.value === 'running') {
    serverStatus.value = 'stopped'
  }
  if (clientStatus.value === 'connected') {
    clientStatus.value = 'disconnected'
  }
  window.removeEventListener('resize', checkIfMobile)
})
</script>

<style scoped>
/* 像素风格TCP通信实验室 */
.pixel-tcp-lab {
  padding: 24px;
  background: var(--bg-dark);
  min-height: calc(100vh - 110px);
  font-family: var(--current-font-family);
  font-size: var(--current-font-size);
  line-height: var(--current-line-height);
}

/* 像素风格页面头部 */
.pixel-header {
  margin-bottom: 32px;
  padding: 20px;
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  box-shadow: var(--pixel-shadow);
  text-align: center;
}

.page-title {
  font-size: calc(var(--current-font-size) * 2.4);
  margin: 0 0 8px 0;
  color: var(--pixel-primary);
  text-shadow: 0 0 15px var(--pixel-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  font-family: var(--current-font-family);
}

.page-subtitle {
  font-size: calc(var(--current-font-size) * 1.2);
  color: var(--pixel-accent);
  margin: 0;
  opacity: 0.8;
  font-family: var(--current-font-family);
}

/* 像素风格卡片 */
.pixel-card {
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--pixel-shadow);
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.pixel-card:hover {
  box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
  transform: translateY(-2px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--pixel-primary);
  font-size: calc(var(--current-font-size) * 1.4);
  color: var(--pixel-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  font-family: var(--current-font-family);
}

/* 状态指示器 */
.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: calc(var(--current-font-size) * 1.0);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-family: var(--current-font-family);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.running .status-dot,
.status-indicator.connected .status-dot {
  background: var(--pixel-success);
  box-shadow: 0 0 10px var(--pixel-success);
}

.status-indicator.stopped .status-dot,
.status-indicator.disconnected .status-dot {
  background: var(--pixel-danger);
  box-shadow: 0 0 10px var(--pixel-danger);
}

.status-indicator.running,
.status-indicator.connected {
  color: var(--pixel-success);
}

.status-indicator.stopped,
.status-indicator.disconnected {
  color: var(--pixel-danger);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* 配置部分 */
.config-section {
  margin-bottom: 24px;
}

.config-title {
  font-size: calc(var(--current-font-size) * 1.2);
  color: var(--pixel-accent);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--pixel-accent);
  padding-bottom: 8px;
  font-family: var(--current-font-family);
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item.full-width {
  grid-column: 1 / -1;
}

.config-label {
  font-size: calc(var(--current-font-size) * 1.0);
  color: var(--pixel-accent);
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--current-font-family);
}

/* 像素风格输入框 */
.pixel-input {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  color: var(--pixel-primary);
  padding: 8px 12px;
  font-family: var(--current-font-family);
  font-size: var(--current-font-size);
  border-radius: 4px;
  transition: all 0.2s ease;
  text-transform: uppercase;
}

.pixel-input:focus {
  outline: none;
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
  background: rgba(0, 212, 255, 0.1);
}

.pixel-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pixel-input::placeholder {
  color: var(--pixel-primary);
  opacity: 0.5;
}

/* 像素风格复选框 */
.pixel-checkbox {
  width: 16px;
  height: 16px;
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  border-radius: 2px;
  cursor: pointer;
  position: relative;
  margin: 0;
}

.pixel-checkbox:checked {
  background: var(--pixel-primary);
  border-color: var(--pixel-primary);
  box-shadow: 0 0 10px var(--pixel-primary);
}

.pixel-checkbox:checked::after {
  content: '✓';
  position: absolute;
  top: -2px;
  left: 1px;
  color: var(--bg-dark);
  font-size: 12px;
  font-weight: bold;
}

/* 像素风格下拉框 */
.pixel-select {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  color: var(--pixel-primary);
  padding: 8px 12px;
  font-family: var(--pixel-font);
  font-size: 10px;
  border-radius: 4px;
  text-transform: uppercase;
  cursor: pointer;
  min-width: 120px;
}

.pixel-select:focus {
  outline: none;
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
}

/* 操作按钮部分 */
.action-section {
  margin-bottom: 24px;
}

.action-btn {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  color: var(--pixel-primary);
  padding: 12px 24px;
  font-family: var(--current-font-family);
  font-size: var(--current-font-size);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
}

.start-btn {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-success);
  color: var(--pixel-success);
}

.start-btn:hover {
  background: var(--pixel-success);
  color: var(--bg-dark);
  box-shadow: 0 0 20px var(--pixel-success);
}

.stop-btn {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-danger);
  color: var(--pixel-danger);
}

.stop-btn:hover {
  background: var(--pixel-danger);
  color: var(--bg-dark);
  box-shadow: 0 0 20px var(--pixel-danger);
}

.connect-btn {
  background: var(--bg-dark);
  border: 2px solid var(--neon-cyan);
  color: var(--neon-cyan);
}

.connect-btn:hover:not(:disabled) {
  background: var(--neon-cyan);
  color: var(--bg-dark);
  box-shadow: 0 0 20px var(--neon-cyan);
}

.connect-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.disconnect-btn {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-warning);
  color: var(--pixel-warning);
}

.disconnect-btn:hover {
  background: var(--pixel-warning);
  color: var(--bg-dark);
  box-shadow: 0 0 20px var(--pixel-warning);
}

/* 统计部分 */
.stats-section {
  margin-bottom: 24px;
}

.stats-title {
  font-size: 12px;
  color: var(--pixel-accent);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--pixel-accent);
  padding-bottom: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 6px;
  transition: all 0.2s ease;
  font-family: var(--current-font-family);
}

.stat-item:hover {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

.stat-label {
  font-size: calc(var(--current-font-size) * 0.9);
  color: var(--pixel-accent);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-family: var(--current-font-family);
}

.stat-value {
  font-size: calc(var(--current-font-size) * 1.8);
  color: var(--pixel-primary);
  font-weight: bold;
  text-shadow: 0 0 10px var(--pixel-primary);
  font-family: var(--current-font-family);
}

/* 快速操作 */
.quick-actions {
  margin-top: 20px;
}

.quick-title {
  font-size: 10px;
  color: var(--pixel-accent);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--pixel-accent);
  padding-bottom: 6px;
}

.quick-buttons {
  display: flex;
  gap: 12px;
}

.quick-btn {
  flex: 1;
  padding: 8px 12px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  color: var(--pixel-primary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.quick-btn:hover {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  box-shadow: 0 0 15px var(--pixel-primary);
}

/* 通信部分 */
.communication-section {
  margin-top: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.small-btn {
  padding: 6px 12px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  color: var(--pixel-primary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.small-btn:hover:not(:disabled) {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  box-shadow: 0 0 15px var(--pixel-primary);
}

.small-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 消息输入部分 */
.message-input-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--pixel-primary);
}

.input-row {
  display: grid;
  grid-template-columns: 120px 1fr auto;
  gap: 12px;
  align-items: center;
}

.message-input {
  text-transform: none;
}

.send-btn {
  padding: 8px 16px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  background: var(--bg-dark);
  border: 2px solid var(--neon-green);
  color: var(--neon-green);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.send-btn:hover:not(:disabled) {
  background: var(--neon-green);
  color: var(--bg-dark);
  box-shadow: 0 0 15px var(--neon-green);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 消息容器 */
.messages-container {
  max-height: 400px;
  overflow-y: auto;
}

.empty-messages {
  text-align: center;
  padding: 40px 20px;
  color: var(--pixel-accent);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 8px;
  color: var(--pixel-primary);
}

.empty-subtitle {
  font-size: 10px;
  opacity: 0.7;
}

/* 消息列表 */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 0;
}

.message-item {
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 6px;
  padding: 12px;
  transition: all 0.2s ease;
  animation: messageSlideIn 0.3s ease;
}

.message-item:hover {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
  transform: translateX(4px);
}

.message-item.system {
  border-color: var(--pixel-accent);
  background: rgba(0, 212, 255, 0.05);
}

.message-item.broadcast {
  border-color: var(--pixel-warning);
  background: rgba(255, 255, 0, 0.05);
}

.message-item.text {
  border-color: var(--pixel-success);
  background: rgba(68, 255, 68, 0.05);
}

/* 消息动画效果 */
.message-0 { animation-delay: 0s; }
.message-1 { animation-delay: 0.1s; }
.message-2 { animation-delay: 0.2s; }
.message-3 { animation-delay: 0.3s; }

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
  font-family: var(--current-font-family);
}

.message-time {
  color: var(--pixel-accent);
}

.message-source {
  font-weight: bold;
  color: var(--pixel-primary);
  text-transform: uppercase;
}

.message-type-tag {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
  border: 1px solid;
}

.message-type-tag.system {
  background: rgba(0, 212, 255, 0.2);
  border-color: var(--pixel-accent);
  color: var(--pixel-accent);
}

.message-type-tag.broadcast {
  background: rgba(255, 255, 0, 0.2);
  border-color: var(--pixel-warning);
  color: var(--pixel-warning);
}

.message-type-tag.text {
  background: rgba(68, 255, 68, 0.2);
  border-color: var(--pixel-success);
  color: var(--pixel-success);
}

.message-content {
  color: var(--pixel-primary);
  line-height: var(--current-line-height);
  word-break: break-word;
  font-size: var(--current-font-size);
  font-family: var(--current-font-family);
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: calc(var(--current-font-size) * 0.8);
  color: var(--text-secondary);
  font-family: var(--current-font-family);
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: var(--bg-dark);
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--pixel-primary);
  border-radius: 4px;
  border: 1px solid var(--bg-dark);
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: var(--neon-cyan);
  box-shadow: 0 0 5px var(--neon-cyan);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pixel-tcp-lab {
    padding: 16px;
  }
  
  .page-title {
    font-size: 18px;
    flex-direction: column;
    gap: 10px;
  }
  
  .config-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .quick-buttons {
    flex-direction: column;
  }
  
  .input-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .message-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .pixel-tcp-lab {
    padding: 12px;
  }
  
  .page-title {
    font-size: 16px;
  }
  
  .pixel-card {
    padding: 16px;
  }
  
  .action-btn {
    padding: 10px 16px;
    font-size: 10px;
  }
  
  .stat-value {
    font-size: 16px;
  }
  
  .messages-container {
    max-height: 300px;
  }
}

/* 高级屏幕优化 */
@media (min-width: 1200px) {
  .pixel-tcp-lab {
    padding: 32px;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .config-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .messages-container {
    max-height: 500px;
  }
  
  .message-item {
    padding: 16px;
  }
  
  .message-content {
    font-size: 12px;
    line-height: 1.7;
  }
}

/* 动画增强 */
.pixel-card {
  animation: cardFadeIn 0.5s ease;
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 服务器/客户端区域特定样式 */
.server-section {
  border-color: var(--pixel-success);
  box-shadow: 0 0 15px rgba(68, 255, 68, 0.2);
}

.client-section {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
}

.server-section:hover {
  box-shadow: 0 0 25px rgba(68, 255, 68, 0.4);
}

.client-section:hover {
  box-shadow: 0 0 25px rgba(0, 212, 255, 0.4);
}
</style> 