import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { SystemApi, type SystemStatus, type ServiceStatus, type PerformanceStats } from '@/api/systemApi'

export const useDashboardStore = defineStore('dashboard', () => {
  // 状态
  const systemStatus = ref<SystemStatus | null>(null)
  const serviceStatus = ref<ServiceStatus[]>([])
  const performanceStats = ref<PerformanceStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdated = ref<Date | null>(null)

  // 计算属性
  const isSystemHealthy = computed(() => {
    return systemStatus.value?.status === 'healthy'
  })

  const activeServices = computed(() => {
    return serviceStatus.value.filter(service => service.status === 'running')
  })

  const totalServices = computed(() => {
    return serviceStatus.value.length
  })

  const systemUptime = computed(() => {
    if (!systemStatus.value) return '0分钟'
    
    const hours = Math.floor(systemStatus.value.uptime / 3600)
    const minutes = Math.floor((systemStatus.value.uptime % 3600) / 60)
    
    if (hours > 0) {
      return `${hours}小时${minutes}分钟`
    }
    return `${minutes}分钟`
  })

  const resourceUsage = computed(() => {
    if (!systemStatus.value) return {}
    
    return {
      cpu: systemStatus.value.cpu_usage,
      memory: systemStatus.value.memory_usage,
      disk: systemStatus.value.disk_usage
    }
  })

  // 获取系统状态的严重程度
  const systemStatusSeverity = computed(() => {
    if (!systemStatus.value) return 'info'
    
    switch (systemStatus.value.status) {
      case 'healthy':
        return 'success'
      case 'warning':
        return 'warning'
      case 'error':
        return 'danger'
      default:
        return 'info'
    }
  })

  // 操作方法
  const fetchSystemStatus = async () => {
    try {
      loading.value = true
      error.value = null
      
      systemStatus.value = await SystemApi.getSystemStatus()
      lastUpdated.value = new Date()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取系统状态失败'
      console.error('Failed to fetch system status:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchServiceStatus = async () => {
    try {
      serviceStatus.value = await SystemApi.getServiceStatus()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取服务状态失败'
      console.error('Failed to fetch service status:', err)
    }
  }

  const fetchPerformanceStats = async () => {
    try {
      performanceStats.value = await SystemApi.getPerformanceStats()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取性能统计失败'
      console.error('Failed to fetch performance stats:', err)
    }
  }

  const fetchAllData = async () => {
    await Promise.all([
      fetchSystemStatus(),
      fetchServiceStatus(),
      fetchPerformanceStats()
    ])
  }

  const refresh = async () => {
    await fetchAllData()
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  // 重置状态
  const reset = () => {
    systemStatus.value = null
    serviceStatus.value = []
    performanceStats.value = null
    loading.value = false
    error.value = null
    lastUpdated.value = null
  }

  return {
    // 状态
    systemStatus,
    serviceStatus,
    performanceStats,
    loading,
    error,
    lastUpdated,
    
    // 计算属性
    isSystemHealthy,
    activeServices,
    totalServices,
    systemUptime,
    resourceUsage,
    systemStatusSeverity,
    
    // 方法
    fetchSystemStatus,
    fetchServiceStatus,
    fetchPerformanceStats,
    fetchAllData,
    refresh,
    clearError,
    reset
  }
}) 