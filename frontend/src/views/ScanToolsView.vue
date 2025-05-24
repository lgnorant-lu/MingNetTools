<template>
  <div class="scan-tools-container pixel-container">
    <!-- 页面标题 -->
    <div class="page-header pixel-header">
      <h1 class="page-title glitch-text" data-text="端口扫描工具">端口扫描工具</h1>
      <p class="page-subtitle">强大的网络端口扫描和服务发现工具</p>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="scanStore.error"
      :title="scanStore.error"
      type="error"
      @close="scanStore.clearError"
      closable
      class="error-alert pixel-alert"
    />

    <!-- 扫描配置和结果区域 -->
    <el-row :gutter="20">
      <el-col :span="8" :xs="24" :sm="24" :md="8" :lg="8">
        <el-card class="config-card pixel-card">
          <template #header>
            <div class="card-header pixel-card-header">
              <span>扫描配置</span>
              <el-tag v-if="scanStore.isScanning" type="warning" size="small" class="pixel-tag">
                扫描进行中
              </el-tag>
            </div>
          </template>

          <el-form :model="scanStore.scanConfig" label-position="top" class="scan-form pixel-form">
            <!-- 目标配置 -->
            <el-form-item label="扫描目标">
              <el-input
                v-model="scanStore.scanConfig.target"
                placeholder="输入IP地址或域名，如: 192.168.1.1"
                :disabled="scanStore.isScanning"
                @keyup.enter="handleStartScan"
                class="pixel-input"
              />
            </el-form-item>

            <!-- 端口配置 -->
            <el-form-item label="端口范围">
              <el-input
                v-model="scanStore.scanConfig.ports"
                placeholder="如: 1-1000, 80,443 或 22,80,443"
                :disabled="scanStore.isScanning"
                class="pixel-input"
              />
            </el-form-item>

            <!-- 扫描类型 -->
            <el-form-item label="扫描类型">
              <el-select 
                v-model="scanStore.scanConfig.scan_type" 
                style="width: 100%"
                :disabled="scanStore.isScanning"
                class="pixel-select"
              >
                <el-option label="TCP连接扫描" value="tcp" />
                <el-option label="UDP扫描" value="udp" />
                <el-option label="SYN扫描" value="syn" />
              </el-select>
            </el-form-item>

            <!-- 高级选项 -->
            <el-form-item label="超时时间 (秒)">
              <el-input-number
                v-model="scanStore.scanConfig.timeout"
                :min="1"
                :max="30"
                style="width: 100%"
                :disabled="scanStore.isScanning"
                class="pixel-input-number"
              />
            </el-form-item>

            <el-form-item label="最大线程数">
              <el-input-number
                v-model="scanStore.scanConfig.max_threads"
                :min="1"
                :max="500"
                style="width: 100%"
                :disabled="scanStore.isScanning"
                class="pixel-input-number"
              />
            </el-form-item>

            <!-- 预设配置按钮 -->
            <el-form-item label="快速配置">
              <div class="preset-buttons">
                <el-button
                  size="small"
                  @click="setPreset('quick')"
                  :disabled="scanStore.isScanning"
                  class="pixel-btn pixel-btn-preset"
                >
                  快速扫描
                </el-button>
                <el-button
                  size="small"
                  @click="setPreset('full')"
                  :disabled="scanStore.isScanning"
                  class="pixel-btn pixel-btn-preset"
                >
                  全端口扫描
                </el-button>
                <el-button
                  size="small"
                  @click="setPreset('stealth')"
                  :disabled="scanStore.isScanning"
                  class="pixel-btn pixel-btn-preset"
                >
                  隐蔽扫描
                </el-button>
              </div>
            </el-form-item>

            <!-- 操作按钮 -->
            <el-form-item>
              <div class="action-buttons">
                <el-button
                  type="primary"
                  @click="handleStartScan"
                  :loading="scanStore.loading"
                  :disabled="!scanStore.canStartScan"
                  style="width: 100%"
                  class="pixel-btn pixel-btn-primary"
                >
                  <el-icon><Search /></el-icon>
                  {{ scanStore.isScanning ? '扫描中...' : '开始扫描' }}
                </el-button>
                
                <el-button
                  v-if="scanStore.isScanning"
                  type="danger"
                  @click="handleStopScan"
                  style="width: 100%; margin-top: 8px"
                  class="pixel-btn pixel-btn-danger"
                >
                  <el-icon><Close /></el-icon>
                  停止扫描
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 扫描进度和结果区域 -->
      <el-col :span="16" :xs="24" :sm="24" :md="16" :lg="16">
        <!-- 扫描进度 -->
        <el-card class="progress-card pixel-card" v-if="scanStore.currentScan">
          <template #header>
            <span>扫描进度</span>
          </template>
          
          <div class="progress-content">
            <el-progress
              :percentage="scanStore.scanProgress"
              :status="getProgressStatus()"
              :stroke-width="8"
              class="pixel-progress"
            />
            
            <div class="progress-details pixel-progress-details">
              <div class="progress-item pixel-progress-item">
                <span>扫描状态:</span>
                <el-tag :type="getScanStatusType()" class="pixel-tag">
                  {{ getScanStatusText() }}
                </el-tag>
              </div>
              <div class="progress-item pixel-progress-item">
                <span>目标:</span>
                <span>{{ scanStore.scanConfig.target }}</span>
              </div>
              <div class="progress-item pixel-progress-item">
                <span>已扫描:</span>
                <span>{{ scanStore.currentScan.scanned_ports }} / {{ scanStore.currentScan.total_ports }}</span>
              </div>
              <div class="progress-item pixel-progress-item">
                <span>发现端口:</span>
                <span>{{ scanStore.currentScan.found_ports }}</span>
              </div>
              <div class="progress-item pixel-progress-item">
                <span>开始时间:</span>
                <span>{{ formatTime(scanStore.currentScan.start_time) }}</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 扫描结果 -->
        <el-card class="results-card pixel-card">
          <template #header>
            <div class="card-header pixel-card-header">
              <span>扫描结果</span>
              <div class="result-stats" v-if="scanStore.scanResults.length > 0">
                <el-tag type="success" size="small" class="pixel-tag">
                  开放: {{ scanStore.openPorts.length }}
                </el-tag>
                <el-tag type="info" size="small" style="margin-left: 8px;" class="pixel-tag">
                  总计: {{ scanStore.scanResults.length }}
                </el-tag>
              </div>
            </div>
          </template>

          <!-- 结果表格 -->
          <el-table
            :data="scanStore.scanResults"
            style="width: 100%"
            :empty-text="getEmptyText()"
            v-loading="scanStore.loading && !scanStore.isScanning"
          >
            <el-table-column prop="port" label="端口" width="80" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag 
                  :type="getPortStatusType(row.status)"
                  size="small"
                >
                  {{ getPortStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="service" label="服务" />
            <el-table-column label="发现时间" width="120">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
          </el-table>

          <!-- 空状态 -->
          <div v-if="!scanStore.isScanning && scanStore.scanResults.length === 0" class="empty-state">
            <el-icon><Search /></el-icon>
            <p>{{ scanStore.currentScan ? '未发现开放端口' : '请配置扫描参数并开始扫描' }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  Search, 
  Close, 
  Monitor 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useScanToolsStore } from '../stores/scanTools'

const scanStore = useScanToolsStore()

// 初始化WebSocket连接
onMounted(() => {
  // WebSocket连接现在通过store内部的全局管理器自动处理
  if (scanStore.isScanning && scanStore.currentScan) {
    console.log('[ScanToolsView] 检测到正在进行的扫描任务，状态将自动恢复')
  } else {
    console.log('[ScanToolsView] 没有检测到正在进行的扫描任务')
  }
})

// 预设配置
const setPreset = (preset: 'quick' | 'full' | 'stealth') => {
  const configs = {
    quick: {
      ports: '21,22,23,25,53,80,110,443,993,995',
      scan_type: 'tcp' as const,
      timeout: 1,
      max_threads: 100
    },
    full: {
      ports: '1-65535',
      scan_type: 'tcp' as const,
      timeout: 3,
      max_threads: 400
    },
    stealth: {
      ports: '1-1000',
      scan_type: 'syn' as const,
      timeout: 5,
      max_threads: 50
    }
  }
  
  Object.assign(scanStore.scanConfig, configs[preset])
}

// 扫描操作
const handleStartScan = async () => {
  if (!scanStore.canStartScan) return
  
  try {
    await scanStore.startScan()
    ElMessage.success('扫描已开始')
  } catch (error) {
    ElMessage.error('启动扫描失败')
  }
}

const handleStopScan = async () => {
  try {
    await scanStore.stopScan()
    ElMessage.success('扫描已停止')
  } catch (error) {
    ElMessage.error('停止扫描失败')
  }
}

// 状态辅助方法
const getProgressStatus = () => {
  if (!scanStore.currentScan) return ''
  
  switch (scanStore.currentScan.status) {
    case 'running':
      return ''
    case 'completed':
      return 'success'
    case 'failed':
      return 'exception'
    case 'cancelled':
      return 'exception'
    default:
      return ''
  }
}

const getScanStatusType = () => {
  if (!scanStore.currentScan) return 'info'
  
  switch (scanStore.currentScan.status) {
    case 'running':
      return 'warning'
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    case 'cancelled':
      return 'info'
    default:
      return 'info'
  }
}

const getScanStatusText = () => {
  if (!scanStore.currentScan) return '未知'
  
  switch (scanStore.currentScan.status) {
    case 'running':
      return '扫描中'
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    case 'cancelled':
      return '已取消'
    default:
      return '未知'
  }
}

const getPortStatusType = (status: string) => {
  switch (status) {
    case 'open':
      return 'success'
    case 'closed':
      return 'info'
    case 'filtered':
      return 'warning'
    default:
      return 'info'
  }
}

const getPortStatusText = (status: string) => {
  switch (status) {
    case 'open':
      return '开放'
    case 'closed':
      return '关闭'
    case 'filtered':
      return '过滤'
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
    return date.toLocaleString()
  } catch (error) {
    console.warn('时间格式化失败:', timeString, error)
    return '--'
  }
}

const getEmptyText = () => {
  if (scanStore.isScanning) {
    return '扫描进行中...'
  }
  return '暂无扫描结果'
}

// 组件卸载时清理
onUnmounted(() => {
  // 清理由全局WebSocket管理器自动处理
  console.log('[ScanToolsView] 组件卸载，WebSocket连接由全局管理器处理')
})
</script>

<style scoped>
/* 像素风格扫描工具容器 */
.scan-tools-container {
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
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

.input-label {
  font-size: 0.8em;
  color: var(--text-secondary);
  text-align: center;
  margin-top: 5px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.preset-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 进度卡片 */
.progress-card {
  margin-bottom: 24px;
  min-height: 140px;
  background: var(--bg-darker) !important;
  border: var(--pixel-border) !important;
  box-shadow: var(--pixel-shadow) !important;
}

.progress-card .el-card__body {
  padding: 24px;
  background: var(--bg-darker) !important;
}

.progress-info {
  margin-bottom: 20px;
  color: var(--text-primary);
}

.progress-details {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 0.9em;
  color: var(--text-secondary);
  padding: 8px 0;
}

/* 结果卡片 */
.results-card {
  min-height: 640px;
  background: var(--bg-darker) !important;
  border: var(--pixel-border) !important;
  box-shadow: var(--pixel-shadow) !important;
}

.results-card .el-card__body {
  padding: 24px;
  background: var(--bg-darker) !important;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-text {
  margin-left: 4px;
}

.empty-results {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary);
}

.empty-results .el-icon {
  color: var(--pixel-primary);
  opacity: 0.6;
}

.results-summary {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24px;
  padding: 24px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 8px;
  box-shadow: inset 0 0 10px rgba(0, 255, 65, 0.1);
}

.results-summary .el-statistic {
  text-align: center;
  padding: 8px 16px;
  color: var(--text-primary);
}

.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
  border-radius: 8px;
  border: var(--pixel-border);
  box-shadow: var(--pixel-shadow);
}

.pagination-container {
  margin-top: 24px;
  text-align: center;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .scan-tools-container {
    padding: 12px;
  }
  
  .page-header {
    margin-bottom: 20px;
  }
  
  .page-title {
    font-size: 1.8em;
    flex-direction: column;
    gap: 10px;
  }
  
  .page-subtitle {
    font-size: 1em;
  }
  
  .config-card {
    margin-bottom: 16px;
    min-height: auto;
  }
  
  .preset-buttons {
    justify-content: center;
  }
  
  .preset-buttons .el-button {
    font-size: 0.8em;
    padding: 6px 12px;
  }
  
  .progress-details {
    flex-direction: column;
    gap: 8px;
    font-size: 0.85em;
  }
  
  .header-actions {
    gap: 8px;
  }
  
  .btn-text {
    display: none;
  }
  
  .results-summary {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .table-container {
    border-radius: 8px;
  }
  
  .pagination-container {
    overflow-x: auto;
    padding: 8px 0;
  }
  
  .pagination-container .el-pagination {
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }
}

/* 平板端适配 */
@media (min-width: 769px) and (max-width: 1023px) {
  .scan-tools-container {
    padding: 18px;
  }
  
  .config-card {
    min-height: 480px;
  }
  
  .config-card .el-card__body {
    padding: 18px;
  }
  
  .preset-buttons .el-button {
    font-size: 0.82em;
    padding: 7px 13px;
  }
  
  .progress-card {
    min-height: 110px;
  }
  
  .progress-card .el-card__body {
    padding: 18px;
  }
  
  .results-card {
    min-height: 540px;
  }
  
  .results-card .el-card__body {
    padding: 18px;
  }
  
  .results-summary {
    padding: 18px;
    margin-bottom: 18px;
  }
  
  .table-container {
    margin-bottom: 16px;
  }
}

/* PC桌面端适配 - 1200px及以上 */
@media (min-width: 1200px) {
  .scan-tools-container {
    padding: 32px;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .page-header {
    margin-bottom: 40px;
  }
  
  .page-title {
    font-size: 2.8em;
  }
  
  .page-subtitle {
    font-size: 1.3em;
  }
  
  .config-card {
    min-height: 680px;
  }
  
  .config-card .el-card__body {
    padding: 28px;
  }
  
  .preset-buttons {
    gap: 12px;
  }
  
  .preset-buttons .el-button {
    font-size: 0.9em;
    padding: 10px 16px;
    min-width: 100px;
  }
  
  .progress-card {
    min-height: 180px;
    margin-bottom: 28px;
  }
  
  .progress-card .el-card__body {
    padding: 28px;
  }
  
  .progress-details {
    margin-top: 16px;
    font-size: 1em;
    gap: 20px;
  }
  
  .results-card {
    min-height: 720px;
  }
  
  .results-card .el-card__body {
    padding: 28px;
  }
  
  .results-summary {
    padding: 28px;
    margin-bottom: 28px;
    gap: 20px;
  }
  
  .results-summary .el-statistic {
    padding: 12px 20px;
  }
  
  .table-container {
    margin-bottom: 24px;
    border-radius: 12px;
  }
  
  .pagination-container {
    margin-top: 28px;
  }
  
  .empty-results {
    padding: 80px 0;
  }
}

/* Element Plus组件覆盖 */
.scan-tools-container :deep(.el-card) {
  background: var(--bg-darker) !important;
  border: var(--pixel-border) !important;
  box-shadow: var(--pixel-shadow) !important;
}

.scan-tools-container :deep(.el-card__body) {
  background: var(--bg-darker) !important;
  color: var(--text-primary) !important;
}

.scan-tools-container :deep(.el-table) {
  background: var(--bg-dark) !important;
  color: var(--text-primary) !important;
}

.scan-tools-container :deep(.el-table th) {
  background: var(--bg-darker) !important;
  color: var(--pixel-primary) !important;
  border-bottom: 1px solid var(--pixel-primary) !important;
}

.scan-tools-container :deep(.el-table td) {
  background: var(--bg-dark) !important;
  color: var(--text-primary) !important;
  border-bottom: 1px solid rgba(0, 255, 65, 0.1) !important;
}

.scan-tools-container :deep(.el-table__empty-text) {
  color: var(--text-secondary) !important;
}

.scan-tools-container :deep(.el-progress) {
  background: var(--bg-dark) !important;
}

.scan-tools-container :deep(.el-progress__text) {
  color: var(--text-primary) !important;
}

.scan-tools-container :deep(.el-pagination) {
  background: transparent !important;
  color: var(--text-primary) !important;
}

.scan-tools-container :deep(.el-pagination .el-pager li) {
  background: var(--bg-dark) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--pixel-primary) !important;
}

.scan-tools-container :deep(.el-pagination .el-pager li.is-active) {
  background: var(--pixel-primary) !important;
  color: var(--bg-dark) !important;
}

.scan-tools-container :deep(.el-statistic) {
  color: var(--text-primary) !important;
}

.scan-tools-container :deep(.el-statistic__content) {
  color: var(--pixel-primary) !important;
}
</style> 