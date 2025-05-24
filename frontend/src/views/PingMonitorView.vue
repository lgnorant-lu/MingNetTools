<template>
  <div class="ping-monitor-container pixel-container">
    <!-- 页面标题 -->
    <div class="page-header pixel-header">
      <h1 class="page-title glitch-text" data-text="PING网络监控">PING网络监控</h1>
      <p class="page-subtitle">实时网络延迟监控和连通性检测</p>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="pingStore.error"
      :title="pingStore.error"
      type="error"
      @close="pingStore.clearError"
      closable
      class="error-alert pixel-alert"
    />

    <!-- 监控配置和结果区域 -->
    <el-row :gutter="20">
      <el-col :span="8" :xs="24" :sm="24" :md="8" :lg="8">
        <el-card class="config-card pixel-card">
          <template #header>
            <div class="card-header pixel-card-header">
              <span>监控配置</span>
              <el-tag v-if="pingStore.isPinging" type="warning" size="small" class="pixel-tag">
                监控中
              </el-tag>
            </div>
          </template>

          <el-form :model="pingStore.pingConfig" label-position="top" class="ping-form pixel-form">
            <!-- 目标主机 -->
            <el-form-item label="目标主机">
              <el-input
                v-model="pingStore.pingConfig.target"
                placeholder="输入IP地址或域名，如: google.com"
                :disabled="pingStore.isPinging"
                @keyup.enter="handleStartPing"
                class="pixel-input"
              />
            </el-form-item>

            <!-- PING次数 -->
            <el-form-item label="PING次数">
              <el-input-number
                v-model="pingStore.pingConfig.count"
                :min="1"
                :max="1000"
                style="width: 100%"
                :disabled="pingStore.isPinging"
                class="pixel-input-number"
              />
            </el-form-item>

            <!-- 时间间隔 -->
            <el-form-item label="时间间隔 (秒)">
              <el-input-number
                v-model="pingStore.pingConfig.interval"
                :min="0.1"
                :max="10"
                :step="0.1"
                style="width: 100%"
                :disabled="pingStore.isPinging"
                class="pixel-input-number"
              />
            </el-form-item>

            <!-- 超时时间 -->
            <el-form-item label="超时时间 (秒)">
              <el-input-number
                v-model="pingStore.pingConfig.timeout"
                :min="1"
                :max="30"
                style="width: 100%"
                :disabled="pingStore.isPinging"
                class="pixel-input-number"
              />
            </el-form-item>

            <!-- 数据包大小 -->
            <el-form-item label="数据包大小 (字节)">
              <el-input-number
                v-model="pingStore.pingConfig.packet_size"
                :min="32"
                :max="1500"
                style="width: 100%"
                :disabled="pingStore.isPinging"
                class="pixel-input-number"
              />
            </el-form-item>

            <!-- 连续监控 -->
            <el-form-item>
              <el-checkbox 
                v-model="pingStore.pingConfig.continuous"
                :disabled="pingStore.isPinging"
                class="pixel-checkbox"
              >
                连续监控模式
              </el-checkbox>
            </el-form-item>

            <!-- 操作按钮 -->
            <el-form-item>
              <div class="action-buttons">
                <el-button
                  type="primary"
                  @click="handleStartPing"
                  :loading="pingStore.loading"
                  :disabled="!pingStore.canStartPing"
                  style="width: 100%"
                  class="pixel-btn pixel-btn-primary"
                >
                  <el-icon><Connection /></el-icon>
                  {{ pingStore.isPinging ? 'PING中...' : '开始PING' }}
                </el-button>
                
                <el-button
                  v-if="pingStore.isPinging"
                  type="danger"
                  @click="handleStopPing"
                  style="width: 100%; margin-top: 8px"
                  class="pixel-btn pixel-btn-danger"
                >
                  <el-icon><Close /></el-icon>
                  停止PING
                </el-button>

                <el-button
                  type="info"
                  @click="handleSinglePing"
                  :loading="pingStore.loading && !pingStore.isPinging"
                  :disabled="!pingStore.pingConfig.target.trim()"
                  style="width: 100%; margin-top: 8px"
                  class="pixel-btn pixel-btn-info"
                >
                  <el-icon><Refresh /></el-icon>
                  单次PING
                </el-button>
              </div>
            </el-form-item>
          </el-form>

          <!-- 统计信息 -->
          <div class="stats-mini-card pixel-stats-card" v-if="pingStore.currentPing">
            <div class="mini-stats">
              <div class="mini-stat pixel-stat">
                <div class="mini-stat-label">成功率</div>
                <div class="mini-stat-value">{{ pingStore.successRate.toFixed(1) }}%</div>
              </div>
              <div class="mini-stat pixel-stat">
                <div class="mini-stat-label">平均延迟</div>
                <div class="mini-stat-value">{{ pingStore.averageTime.toFixed(1) }}ms</div>
              </div>
              <div class="mini-stat pixel-stat">
                <div class="mini-stat-label">丢包率</div>
                <div class="mini-stat-value">{{ pingStore.packetLoss.toFixed(1) }}%</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 监控结果区域 -->
      <el-col :span="16" :xs="24" :sm="24" :md="16" :lg="16">
        <!-- PING统计 -->
        <el-card class="stats-card pixel-card" v-if="pingStore.currentPing">
          <template #header>
            <span>PING统计</span>
          </template>
          
          <div class="ping-stats pixel-stats">
            <el-row :gutter="16">
              <el-col :span="6">
                <div class="stat-item pixel-stat-item">
                  <div class="stat-label">已发送</div>
                  <div class="stat-value">{{ pingStore.currentPing.packets_sent }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item pixel-stat-item">
                  <div class="stat-label">已接收</div>
                  <div class="stat-value">{{ pingStore.currentPing.packets_received }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item pixel-stat-item">
                  <div class="stat-label">最小延迟</div>
                  <div class="stat-value">{{ pingStore.currentPing.min_time.toFixed(1) }}ms</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item pixel-stat-item">
                  <div class="stat-label">最大延迟</div>
                  <div class="stat-value">{{ pingStore.currentPing.max_time.toFixed(1) }}ms</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- PING结果 -->
        <el-card class="results-card pixel-card">
          <template #header>
            <div class="card-header pixel-card-header">
              <span>PING结果</span>
              <div class="result-stats" v-if="pingStore.pingResults.length > 0">
                <el-tag type="success" size="small" class="pixel-tag">
                  成功: {{ pingStore.pingResults.filter(r => r.status === 'success').length }}
                </el-tag>
                <el-tag type="danger" size="small" style="margin-left: 8px;" class="pixel-tag">
                  失败: {{ pingStore.pingResults.filter(r => r.status !== 'success').length }}
                </el-tag>
              </div>
            </div>
          </template>

          <!-- 结果表格 -->
          <el-table
            :data="pingStore.pingResults"
            style="width: 100%"
            :empty-text="getEmptyText()"
            v-loading="pingStore.loading && !pingStore.isPinging"
            max-height="400"
          >
            <el-table-column prop="sequence" label="序号" width="80" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag 
                  :type="getPingStatusType(row.status)"
                  size="small"
                  class="pixel-tag"
                >
                  {{ getPingStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="响应时间" width="100">
              <template #default="{ row }">
                {{ row.response_time ? `${row.response_time.toFixed(1)}ms` : '--' }}
              </template>
            </el-table-column>
            <el-table-column prop="ttl" label="TTL" width="60" />
            <el-table-column label="时间" width="140">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="error" label="错误信息" show-overflow-tooltip />
          </el-table>

          <!-- 空状态 -->
          <div v-if="!pingStore.isPinging && pingStore.pingResults.length === 0" class="empty-state">
            <el-icon><Connection /></el-icon>
            <p>{{ pingStore.currentPing ? '暂无PING结果' : '请配置PING参数并开始监控' }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  Connection, 
  Close, 
  Refresh 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { usePingMonitorStore } from '../stores/pingMonitor'

const pingStore = usePingMonitorStore()

// 初始化
onMounted(() => {
  // WebSocket连接现在通过store内部的全局管理器自动处理
  if (pingStore.isPinging && pingStore.currentPing) {
    console.log('[PingMonitorView] 检测到正在进行的PING任务，状态将自动恢复')
  }
})

// PING操作
const handleStartPing = async () => {
  if (!pingStore.canStartPing) return
  
  try {
    await pingStore.startPing()
    ElMessage.success('PING监控已开始')
  } catch (error) {
    ElMessage.error('启动PING失败')
  }
}

const handleStopPing = async () => {
  try {
    await pingStore.stopPing()
    ElMessage.success('PING监控已停止')
  } catch (error) {
    ElMessage.error('停止PING失败')
  }
}

const handleSinglePing = async () => {
  try {
    const result = await pingStore.singlePing(pingStore.pingConfig.target)
    ElMessage.success(`单次PING成功: ${result.response_time}ms`)
  } catch (error) {
    ElMessage.error('单次PING失败')
  }
}

// 状态辅助方法
const getPingStatusType = (status: string) => {
  switch (status) {
    case 'success':
      return 'success'
    case 'timeout':
      return 'warning'
    case 'failed':
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

const getPingStatusText = (status: string) => {
  switch (status) {
    case 'success':
      return '成功'
    case 'timeout':
      return '超时'
    case 'failed':
    case 'error':
      return '失败'
    default:
      return '未知'
  }
}

const formatTime = (timeString: string | undefined) => {
  if (!timeString) return '--'
  
  try {
    const date = new Date(timeString)
    if (isNaN(date.getTime())) {
      return '--'
    }
    return date.toLocaleTimeString()
  } catch (error) {
    console.warn('时间格式化失败:', timeString, error)
    return '--'
  }
}

const getEmptyText = () => {
  if (pingStore.isPinging) {
    return 'PING进行中...'
  }
  return '暂无PING结果'
}

// 组件卸载时清理
onUnmounted(() => {
  // 清理由全局WebSocket管理器自动处理
  console.log('[PingMonitorView] 组件卸载，WebSocket连接由全局管理器处理')
})
</script>

<style scoped>
/* 像素风格PING监控容器 */
.ping-monitor-container {
  padding: 24px;
  background: var(--bg-dark);
  min-height: calc(100vh - 110px);
}

/* 像素风格页面头部 */
.page-header {
  margin-bottom: 32px;
  text-align: center;
  padding: 20px;
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  box-shadow: var(--pixel-shadow);
}

.page-title {
  font-size: 2.5em;
  color: var(--pixel-primary);
  margin-bottom: 10px;
  text-shadow: 0 0 15px var(--pixel-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.page-subtitle {
  font-size: 1.2em;
  color: var(--pixel-accent);
  margin: 0;
  opacity: 0.8;
}

/* 像素风格配置卡片 */
.config-card {
  height: fit-content;
  margin-bottom: 20px;
  min-height: 580px;
  background: var(--bg-darker) !important;
  border: var(--pixel-border) !important;
  box-shadow: var(--pixel-shadow) !important;
}

.config-card .el-card__body {
  padding: 24px;
  background: var(--bg-darker) !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-primary);
}

/* 统计迷你卡片 */
.stats-mini-card {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 8px;
  box-shadow: inset 0 0 10px rgba(0, 255, 65, 0.1);
}

.mini-stats {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.mini-stat {
  text-align: center;
  flex: 1;
}

.mini-stat-label {
  font-size: 0.8em;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.mini-stat-value {
  font-size: 1.4em;
  font-weight: bold;
  color: var(--pixel-primary);
  text-shadow: 0 0 10px var(--pixel-primary);
}

/* 统计卡片 */
.stats-card {
  margin-bottom: 24px;
  background: var(--bg-darker) !important;
  border: var(--pixel-border) !important;
  box-shadow: var(--pixel-shadow) !important;
}

.ping-stats {
  padding: 16px;
  background: var(--bg-darker);
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 8px;
  transition: all var(--animation-speed-fast) ease;
}

.stat-item:hover {
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
  transform: translateY(-1px);
}

.stat-label {
  font-size: 0.9em;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  font-size: 1.5em;
  font-weight: bold;
  color: var(--pixel-primary);
  text-shadow: 0 0 10px var(--pixel-primary);
}

/* 结果卡片 */
.results-card {
  min-height: 500px;
  background: var(--bg-darker) !important;
  border: var(--pixel-border) !important;
  box-shadow: var(--pixel-shadow) !important;
}

.results-card .el-card__body {
  padding: 24px;
  background: var(--bg-darker) !important;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary);
}

.empty-state .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: var(--pixel-primary);
  opacity: 0.6;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .ping-monitor-container {
    padding: 12px;
  }
  
  .config-card {
    margin-bottom: 16px;
    min-height: auto;
  }
  
  .mini-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .results-card {
    min-height: 400px;
  }
  
  .page-title {
    font-size: 1.8em;
  }
  
  .page-subtitle {
    font-size: 1em;
  }
}

@media (min-width: 1200px) {
  .ping-monitor-container {
    padding: 32px;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .config-card {
    min-height: 680px;
  }
  
  .results-card {
    min-height: 600px;
  }
}

/* Element Plus组件覆盖 */
.ping-monitor-container :deep(.el-card) {
  background: var(--bg-darker) !important;
  border: var(--pixel-border) !important;
  box-shadow: var(--pixel-shadow) !important;
}

.ping-monitor-container :deep(.el-card__body) {
  background: var(--bg-darker) !important;
  color: var(--text-primary) !important;
}

.ping-monitor-container :deep(.el-table) {
  background: var(--bg-dark) !important;
  color: var(--text-primary) !important;
}

.ping-monitor-container :deep(.el-table th) {
  background: var(--bg-darker) !important;
  color: var(--pixel-primary) !important;
  border-bottom: 1px solid var(--pixel-primary) !important;
}

.ping-monitor-container :deep(.el-table td) {
  background: var(--bg-dark) !important;
  color: var(--text-primary) !important;
  border-bottom: 1px solid rgba(0, 255, 65, 0.1) !important;
}

.ping-monitor-container :deep(.el-table__empty-text) {
  color: var(--text-secondary) !important;
}

.ping-monitor-container :deep(.el-progress) {
  background: var(--bg-dark) !important;
}

.ping-monitor-container :deep(.el-progress__text) {
  color: var(--text-primary) !important;
}
</style> 