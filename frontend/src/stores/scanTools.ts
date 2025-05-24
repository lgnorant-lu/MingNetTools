import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  ScanApi, 
  ScanWebSocket,
  type ScanConfig, 
  type ScanResult, 
  type ScanStatus 
} from '@/api/scanApi'
import { getGlobalWebSocketManager } from '@/composables/useWebSocketManager'

export const useScanToolsStore = defineStore('scanTools', () => {
  // 状态
  const currentScan = ref<ScanStatus | null>(null)
  const scanResults = ref<ScanResult[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isScanning = ref(false)
  
  // 全局WebSocket管理器
  const wsManager = getGlobalWebSocketManager()
  
  // 扫描配置
  const scanConfig = ref<ScanConfig>({
    target: '',
    ports: '1-1000',
    scan_type: 'tcp',
    timeout: 3,
    max_threads: 200
  })

  // 计算属性
  const scanProgress = computed(() => {
    if (!currentScan.value) return 0
    return currentScan.value.progress
  })

  const openPorts = computed(() => {
    return scanResults.value.filter(result => result.status === 'open')
  })

  const canStartScan = computed(() => {
    return !isScanning.value && scanConfig.value.target.trim() !== ''
  })

  // WebSocket进度监控
  const setupWebSocketMonitoring = (scanId: string) => {
    const connectionId = `scan_${scanId}`
    
    const scanSocket = wsManager.getOrCreateConnection(
      connectionId,
      'scan',
      () => new ScanWebSocket({
        targets: scanConfig.value.target,
        ports: scanConfig.value.ports,
        scan_type: scanConfig.value.scan_type,
        max_threads: scanConfig.value.max_threads
      }),
      true // 保持连接活跃
    )
    
    scanSocket.connect((data) => {
      console.log('[ScanWebSocket] 接收消息:', data)
      wsManager.markConnectionActive(connectionId)

      if (data.type === 'scan_progress') {
        // 更新扫描进度
        if (currentScan.value) {
          currentScan.value.progress = data.progress
          currentScan.value.scanned_ports = data.ports_scanned
          currentScan.value.found_ports = data.open_ports_found
        }
      } else if (data.type === 'scan_port_found') {
        // 发现开放端口
        scanResults.value.push({
          scan_id: data.task_id,
          target: data.target,
          port: data.port,
          status: data.result?.status || 'open',
          service: data.result?.service || '未知',
          timestamp: new Date().toISOString()
        })
      } else if (data.type === 'scan_completed') {
        // 扫描完成
        if (currentScan.value) {
          currentScan.value.status = 'completed'
          currentScan.value.progress = 100
          currentScan.value.end_time = new Date().toISOString()
        }
        isScanning.value = false
        // 扫描完成后可以释放连接
        wsManager.setConnectionKeepAlive(connectionId, false)
      } else if (data.type === 'scan_error') {
        error.value = data.error
        isScanning.value = false
        wsManager.setConnectionKeepAlive(connectionId, false)
      }
    }, (err) => {
      console.error('[ScanWebSocket] 错误:', err)
      error.value = 'WebSocket连接错误，无法接收实时扫描结果'
    })
  }

  // 操作方法
  const startScan = async () => {
    try {
      loading.value = true
      error.value = null
      
      // 1. 使用API启动扫描，获取scan_id
      const response = await ScanApi.startScan(scanConfig.value)
      
      // 2. 解析响应，获取scan_id
      const scanData = response.data || response
      currentScan.value = {
        scan_id: scanData.scan_id,
        status: 'running',
        progress: 0,
        total_ports: scanData.total_ports || 1000,
        scanned_ports: 0,
        found_ports: 0,
        start_time: scanData.start_time || new Date().toISOString()
      }
      
      isScanning.value = true
      scanResults.value = []
      
      // 3. 建立WebSocket连接监控进度
      setupWebSocketMonitoring(currentScan.value.scan_id)
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '启动扫描失败'
      console.error('Failed to start scan:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const stopScan = async () => {
    if (!currentScan.value?.scan_id) {
      error.value = '没有正在运行的扫描任务'
      return
    }
    
    try {
      loading.value = true
      await ScanApi.stopScan(currentScan.value.scan_id)
      isScanning.value = false
      
      // 关闭WebSocket连接
      wsManager.removeConnection(`scan_${currentScan.value.scan_id}`)
      
      // 更新状态
      if (currentScan.value) {
        currentScan.value.status = 'cancelled'
        currentScan.value.end_time = new Date().toISOString()
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '停止扫描失败'
      console.error('Failed to stop scan:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  // 重置所有状态
  const reset = () => {
    if (currentScan.value?.scan_id) {
      wsManager.removeConnection(`scan_${currentScan.value.scan_id}`)
    }
    currentScan.value = null
    scanResults.value = []
    loading.value = false
    error.value = null
    isScanning.value = false
  }

  return {
    // 状态
    currentScan,
    scanResults,
    loading,
    error,
    isScanning,
    scanConfig,
    
    // 计算属性
    scanProgress,
    openPorts,
    canStartScan,
    
    // 方法
    startScan,
    stopScan,
    clearError,
    reset
  }
}) 