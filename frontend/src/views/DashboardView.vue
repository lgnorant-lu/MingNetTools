<template>
  <div class="dashboard-container pixel-dashboard">
    <!-- 页面标题 -->
    <div class="page-header pixel-header">
      <h1 class="page-title glitch-text" data-text="SYSTEM DASHBOARD">
        SYSTEM DASHBOARD
      </h1>
      <p class="page-subtitle">实时监控系统状态和性能指标</p>
      <div class="header-actions">
        <el-button 
          :icon="Refresh" 
          @click="handleRefresh" 
          :loading="dashboardStore.loading"
          class="pixel-btn refresh-btn"
        >
          刷新数据
        </el-button>
        <span v-if="dashboardStore.lastUpdated" class="last-updated pixel-text">
          最后更新: {{ formatTime(dashboardStore.lastUpdated) }}
        </span>
      </div>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="dashboardStore.error"
      :title="dashboardStore.error"
      type="error"
      @close="dashboardStore.clearError"
      closable
      class="error-alert pixel-alert"
    />

    <!-- 系统状态统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <!-- 系统状态 - Ming彩蛋触发点 -->
      <el-col :span="6" :xs="24" :sm="12" :md="6" :lg="6">
        <div class="stat-card pixel-card dashboard-system-info" @dblclick="handleSystemDoubleClick">
          <div class="stat-content">
            <div class="stat-icon system-status pixel-icon" :class="dashboardStore.systemStatusSeverity">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number pixel-number">{{ systemStatusText }}</div>
              <div class="stat-label">SYSTEM STATUS</div>
              <div class="stat-detail">运行时间: {{ dashboardStore.systemUptime }}</div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 活跃服务 -->
      <el-col :span="6" :xs="24" :sm="12" :md="6" :lg="6">
        <div class="stat-card pixel-card">
          <div class="stat-content">
            <div class="stat-icon services pixel-icon">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number pixel-number">{{ dashboardStore.activeServices.length }}/{{ dashboardStore.totalServices }}</div>
              <div class="stat-label">ACTIVE SERVICES</div>
              <div class="stat-detail">服务正常运行</div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- CPU使用率 -->
      <el-col :span="6" :xs="24" :sm="12" :md="6" :lg="6">
        <div class="stat-card pixel-card">
          <div class="stat-content">
            <div class="stat-icon cpu pixel-icon">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number pixel-number">{{ formatPercentage(dashboardStore.resourceUsage.cpu) }}</div>
              <div class="stat-label">CPU USAGE</div>
              <div class="stat-detail">处理器负载</div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 内存使用率 -->
      <el-col :span="6" :xs="24" :sm="12" :md="6" :lg="6">
        <div class="stat-card pixel-card">
          <div class="stat-content">
            <div class="stat-icon memory pixel-icon">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number pixel-number">{{ formatPercentage(dashboardStore.resourceUsage.memory) }}</div>
              <div class="stat-label">MEMORY USAGE</div>
              <div class="stat-detail">内存占用</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 性能统计卡片 -->
    <el-row :gutter="20" class="stats-row" v-if="dashboardStore.performanceStats">
      <el-col :span="8" :xs="24" :sm="12" :md="8" :lg="8">
        <div class="stat-card pixel-card performance">
          <div class="stat-content">
            <div class="stat-icon scans pixel-icon">
              <el-icon><Search /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number pixel-number">{{ dashboardStore.performanceStats.total_scans }}</div>
              <div class="stat-label">TOTAL SCANS</div>
              <div class="stat-detail">活跃: {{ dashboardStore.performanceStats.active_scans }}</div>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :span="8" :xs="24" :sm="12" :md="8" :lg="8">
        <div class="stat-card pixel-card performance">
          <div class="stat-content">
            <div class="stat-icon pings pixel-icon">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number pixel-number">{{ dashboardStore.performanceStats.total_pings }}</div>
              <div class="stat-label">PING TESTS</div>
              <div class="stat-detail">活跃: {{ dashboardStore.performanceStats.active_pings }}</div>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :span="8" :xs="24" :sm="12" :md="8" :lg="8">
        <div class="stat-card pixel-card performance">
          <div class="stat-content">
            <div class="stat-icon connections pixel-icon">
              <el-icon><Link /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number pixel-number">{{ dashboardStore.performanceStats.total_tcp_connections }}</div>
              <div class="stat-label">TCP CONNECTIONS</div>
              <div class="stat-detail">活跃: {{ dashboardStore.performanceStats.active_tcp_connections }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快速操作区域 -->
    <div class="quick-actions pixel-card">
      <div class="card-header">
        <span class="glitch-text" data-text="QUICK ACTIONS">QUICK ACTIONS</span>
      </div>
      <div class="action-buttons">
        <button class="pixel-btn action-btn scan-btn" @click="navigateToScan">
          <el-icon><Search /></el-icon>
          <span>PORT SCAN</span>
        </button>
        <button class="pixel-btn action-btn ping-btn" @click="navigateToPing">
          <el-icon><Connection /></el-icon>
          <span>PING MONITOR</span>
        </button>
        <button class="pixel-btn action-btn tcp-btn" @click="navigateToTcp">
          <el-icon><Link /></el-icon>
          <span>TCP LAB</span>
        </button>
        <button class="pixel-btn action-btn info-btn" @click="handleSystemInfo">
          <el-icon><Setting /></el-icon>
          <span>SYSTEM INFO</span>
        </button>
      </div>
    </div>

    <!-- 服务状态列表 -->
    <div v-if="dashboardStore.serviceStatus.length > 0" class="pixel-card service-status">
      <div class="card-header">
        <span class="glitch-text" data-text="SERVICE STATUS">SERVICE STATUS</span>
      </div>
      <div class="service-list">
        <div v-for="service in dashboardStore.serviceStatus" :key="service.service_name" class="service-item">
          <div class="service-name">{{ service.service_name }}</div>
          <div class="service-status" :class="getServiceStatusClass(service.status)">
            {{ getServiceStatusText(service.status) }}
          </div>
          <div class="service-port">:{{ service.port }}</div>
          <div class="service-uptime">{{ formatUptime(service.uptime) }}</div>
        </div>
      </div>
    </div>

    <!-- 网络状态雷达 -->
    <div class="pixel-card network-radar-section">
      <div class="card-header">
        <span class="glitch-text" data-text="NETWORK RADAR">NETWORK RADAR</span>
      </div>
      <NetworkRadar 
        :animated="true"
        :refresh-interval="10000"
        @refresh="handleNetworkRadarRefresh"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { 
  Monitor, 
  Search, 
  Connection, 
  Link, 
  Grid,
  Cpu,
  DataLine,
  Setting,
  Refresh
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useDashboardStore } from '../stores/dashboard'
import NetworkRadar from '../components/charts/NetworkRadar.vue'

const router = useRouter()
const dashboardStore = useDashboardStore()

// 计算系统状态文本
const systemStatusText = computed(() => {
  if (!dashboardStore.systemStatus) return '未知'
  
  switch (dashboardStore.systemStatus.status) {
    case 'healthy':
      return '正常'
    case 'warning':
      return '警告'
    case 'error':
      return '错误'
    default:
      return '未知'
  }
})

// 页面跳转方法
const navigateToScan = () => {
  router.push('/scan')
}

const navigateToPing = () => {
  router.push('/ping')
}

const navigateToTcp = () => {
  router.push('/tcp')
}

const handleSystemInfo = () => {
  router.push('/settings')
}

// 格式化时间
const formatTime = (date: Date) => {
  return date.toLocaleString()
}

// 格式化百分比
const formatPercentage = (value: number | undefined) => {
  if (value === undefined) return '0%'
  return `${value.toFixed(1)}%`
}

// 格式化运行时间
const formatUptime = (uptime: number) => {
  const hours = Math.floor(uptime / 3600)
  const minutes = Math.floor((uptime % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

// 获取服务状态文本
const getServiceStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '运行中'
    case 'stopped':
      return '已停止'
    case 'error':
      return '错误'
    default:
      return '未知'
  }
}

// 获取服务状态CSS类
const getServiceStatusClass = (status: string) => {
  switch (status) {
    case 'running':
      return 'running'
    case 'stopped':
      return 'stopped'
    case 'error':
      return 'warning'
    default:
      return 'warning'
  }
}

// 刷新数据
const handleRefresh = async () => {
  try {
    await dashboardStore.fetchAllData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  handleRefresh()
})

// 处理网络状态雷达刷新
const handleNetworkRadarRefresh = () => {
  // 实现网络状态雷达刷新逻辑
  ElMessage.info('网络状态雷达刷新功能开发中...')
}

// 处理系统状态双击事件
const handleSystemDoubleClick = async () => {
  try {
    console.log('🖱️ Dashboard系统状态区域被双击了！')
    
    // 动态导入Ming彩蛋引擎
    const { mingEasterEgg } = await import('../utils/mingEasterEgg')
    
    // 尝试触发dashboardCard彩蛋
    const triggered = await mingEasterEgg.attemptTrigger('dashboardCard')
    
    if (triggered) {
      ElMessage({
        type: 'success',
        message: '🎁 系统检测到特殊信号！',
        duration: 3000
      })
    } else {
      // 给出技术风格的暗示
      const hints = [
        '⚡ 系统运行正常，所有参数稳定...',
        '🔍 深度扫描中...发现异常信号...',
        '💾 内存缓存优化完成',
        '🌐 网络连接稳定，延迟优化中...'
      ]
      ElMessage({
        type: 'info',
        message: hints[Math.floor(Math.random() * hints.length)],
        duration: 2000
      })
    }
  } catch (error) {
    console.warn('Ming彩蛋系统加载失败:', error)
    ElMessage({
      type: 'info', 
      message: '🔧 系统状态检查完成',
      duration: 1500
    })
  }
}
</script>

<style scoped>
/* 像素风格仪表板 */
.pixel-dashboard {
  padding: 24px;
  background: var(--bg-dark);
  min-height: 100vh;
}

/* 像素风格页面头部 */
.pixel-header {
  margin-bottom: 32px;
  padding: 20px;
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  box-shadow: var(--pixel-shadow);
}

.page-title {
  font-size: 24px;
  margin: 0 0 8px 0;
  color: var(--pixel-primary);
  text-shadow: 0 0 15px var(--pixel-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.page-subtitle {
  font-size: 12px;
  color: var(--pixel-accent);
  margin: 0 0 16px 0;
  opacity: 0.8;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.refresh-btn {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  color: var(--pixel-primary);
  padding: 8px 16px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.refresh-btn:hover {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  box-shadow: 0 0 20px var(--pixel-primary);
}

.pixel-text {
  font-size: 10px;
  color: var(--pixel-accent);
  text-shadow: 0 0 5px var(--pixel-accent);
}

/* 像素风格警告 */
.pixel-alert {
  background: var(--bg-darker) !important;
  border: 2px solid var(--pixel-danger) !important;
  color: var(--pixel-danger) !important;
  margin-bottom: 24px;
  box-shadow: 0 0 15px rgba(255, 68, 68, 0.3);
}

/* 统计卡片行 */
.stats-row {
  margin-bottom: 24px;
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

/* 统计内容 */
.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pixel-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--pixel-primary);
  border-radius: 8px;
  font-size: 24px;
  color: var(--pixel-primary);
  background: rgba(0, 255, 65, 0.1);
  box-shadow: inset 0 0 10px rgba(0, 255, 65, 0.2);
}

.pixel-icon.system-status.success {
  border-color: var(--pixel-success);
  color: var(--pixel-success);
  background: rgba(68, 255, 68, 0.1);
  box-shadow: inset 0 0 10px rgba(68, 255, 68, 0.2);
}

.pixel-icon.system-status.warning {
  border-color: var(--pixel-warning);
  color: var(--pixel-warning);
  background: rgba(255, 255, 0, 0.1);
  box-shadow: inset 0 0 10px rgba(255, 255, 0, 0.2);
}

.pixel-icon.system-status.danger {
  border-color: var(--pixel-danger);
  color: var(--pixel-danger);
  background: rgba(255, 68, 68, 0.1);
  box-shadow: inset 0 0 10px rgba(255, 68, 68, 0.2);
}

.pixel-icon.services {
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.1);
}

.pixel-icon.cpu {
  border-color: var(--neon-orange);
  color: var(--neon-orange);
  background: rgba(255, 102, 0, 0.1);
}

.pixel-icon.memory {
  border-color: var(--neon-purple);
  color: var(--neon-purple);
  background: rgba(191, 0, 255, 0.1);
}

.pixel-icon.scans {
  border-color: var(--pixel-accent);
  color: var(--pixel-accent);
  background: rgba(0, 212, 255, 0.1);
}

.pixel-icon.pings {
  border-color: var(--neon-green);
  color: var(--neon-green);
  background: rgba(57, 255, 20, 0.1);
}

.pixel-icon.connections {
  border-color: var(--neon-pink);
  color: var(--neon-pink);
  background: rgba(255, 0, 255, 0.1);
}

.stat-info {
  flex: 1;
}

.pixel-number {
  font-size: 20px;
  font-weight: bold;
  color: var(--pixel-primary);
  text-shadow: 0 0 10px var(--pixel-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 10px;
  color: var(--pixel-accent);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.stat-detail {
  font-size: 8px;
  color: var(--pixel-primary);
  opacity: 0.7;
}

/* 卡片头部 */
.card-header {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--pixel-primary);
  font-size: 14px;
  color: var(--pixel-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 快速操作按钮 */
.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 20px;
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  color: var(--pixel-primary);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 4px;
}

.action-btn:hover {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  box-shadow: 0 0 20px var(--pixel-primary);
  transform: translateY(-2px);
}

.scan-btn:hover {
  border-color: var(--pixel-accent);
  background: var(--pixel-accent);
  box-shadow: 0 0 20px var(--pixel-accent);
}

.ping-btn:hover {
  border-color: var(--neon-green);
  background: var(--neon-green);
  box-shadow: 0 0 20px var(--neon-green);
}

.tcp-btn:hover {
  border-color: var(--neon-pink);
  background: var(--neon-pink);
  box-shadow: 0 0 20px var(--neon-pink);
}

.info-btn:hover {
  border-color: var(--pixel-warning);
  background: var(--pixel-warning);
  box-shadow: 0 0 20px var(--pixel-warning);
}

/* 服务状态列表 */
.service-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.service-item {
  display: grid;
  grid-template-columns: 2fr 1fr 80px 120px;
  gap: 16px;
  padding: 12px 16px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 4px;
  align-items: center;
  transition: all 0.2s ease;
}

.service-item:hover {
  background: rgba(0, 255, 65, 0.05);
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
}

.service-name {
  font-size: 12px;
  color: var(--pixel-primary);
  font-weight: bold;
}

.service-status {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.service-status.running {
  background: rgba(68, 255, 68, 0.2);
  color: var(--pixel-success);
  border: 1px solid var(--pixel-success);
}

.service-status.stopped {
  background: rgba(255, 68, 68, 0.2);
  color: var(--pixel-danger);
  border: 1px solid var(--pixel-danger);
}

.service-status.warning {
  background: rgba(255, 255, 0, 0.2);
  color: var(--pixel-warning);
  border: 1px solid var(--pixel-warning);
}

.service-port {
  font-size: 10px;
  color: var(--pixel-accent);
  text-align: center;
}

.service-uptime {
  font-size: 10px;
  color: var(--pixel-primary);
  opacity: 0.8;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pixel-dashboard {
    padding: 16px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .pixel-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .pixel-number {
    font-size: 16px;
  }
  
  .service-item {
    grid-template-columns: 1fr;
    gap: 8px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .pixel-dashboard {
    padding: 12px;
  }
  
  .page-title {
    font-size: 16px;
  }
  
  .pixel-card {
    padding: 16px;
  }
  
  .pixel-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .pixel-number {
    font-size: 14px;
  }
  
  .action-btn {
    padding: 12px 16px;
    font-size: 9px;
  }
}

/* 动画效果 */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px var(--pixel-primary);
  }
  50% {
    box-shadow: 0 0 20px var(--pixel-primary), 0 0 30px var(--pixel-primary);
  }
}

.pixel-card.performance {
  animation: pulse-glow 3s ease-in-out infinite;
}
</style> 