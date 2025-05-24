import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  PingApi, 
  PingWebSocket,
  type PingConfig, 
  type PingResult, 
  type PingStatistics 
} from '@/api/pingApi'
import { getGlobalWebSocketManager } from '@/composables/useWebSocketManager'

export const usePingMonitorStore = defineStore('pingMonitor', () => {
  // 状态
  const currentPing = ref<PingStatistics | null>(null)
  const pingResults = ref<PingResult[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isPinging = ref(false)
  
  // 全局WebSocket管理器
  const wsManager = getGlobalWebSocketManager()
  
  // PING配置
  const pingConfig = ref<PingConfig>({
    target: '',
    count: 10,
    interval: 1,
    timeout: 3,
    packet_size: 64,
    continuous: false
  })

  // 计算属性
  const successRate = computed(() => {
    if (pingResults.value.length === 0) return 0
    const successCount = pingResults.value.filter(r => r.status === 'success').length
    return (successCount / pingResults.value.length) * 100
  })

  const packetLoss = computed(() => {
    return 100 - successRate.value
  })

  const averageTime = computed(() => {
    const successResults = pingResults.value.filter(r => r.status === 'success' && r.response_time)
    if (successResults.length === 0) return 0
    const totalTime = successResults.reduce((sum, r) => sum + (r.response_time || 0), 0)
    return totalTime / successResults.length
  })

  const canStartPing = computed(() => {
    return !isPinging.value && pingConfig.value.target.trim() !== ''
  })
  
  // WebSocket监控
  const setupWebSocketMonitoring = (pingId: string) => {
    const connectionId = `ping_${pingId}`
    
    const pingSocket = wsManager.getOrCreateConnection(
      connectionId,
      'ping',
      () => new PingWebSocket({
        target: pingConfig.value.target,
        count: pingConfig.value.continuous ? -1 : pingConfig.value.count,
        interval: pingConfig.value.interval
      }),
      true // 保持连接活跃
    )
    
    pingSocket.connect((data) => {
      console.log('[PingWebSocket] 接收消息:', data)
      wsManager.markConnectionActive(connectionId)

      if (data.type === 'ping_result') {
        // 使用后端返回的完整数据，不要重新计算状态
        const pingResult: PingResult = {
          ping_id: pingId,
          target: data.target,
          sequence: data.sequence || pingResults.value.length + 1,
          response_time: data.response_time !== undefined && data.response_time !== null ? data.response_time : null,
          ttl: data.ttl !== undefined && data.ttl !== null ? data.ttl : null,
          packet_size: data.packet_size || 64,
          timestamp: data.timestamp ? new Date(data.timestamp * 1000).toISOString() : new Date().toISOString(), // 修复时间戳转换
          status: data.status || (data.success ? 'success' : 'timeout'), // 优先使用后端status
          error: data.error_message || data.error
        }
        
        // 添加新的PING结果到列表顶部
        pingResults.value.unshift(pingResult)
        
        // 保留最近的100条结果
        if (pingResults.value.length > 100) {
          pingResults.value = pingResults.value.slice(0, 100)
        }
        
        // 更新统计信息
        updateStatistics()
        
      } else if (data.type === 'ping_monitor_connected') {
        console.log('[PingWebSocket] 监控连接成功:', data.message)
      } else if (data.type === 'ping_error') {
        error.value = data.error || 'PING执行出错'
        isPinging.value = false
        wsManager.setConnectionKeepAlive(connectionId, false)
      }
    }, (err) => {
      console.error('[PingWebSocket] 错误:', err)
      error.value = 'WebSocket连接错误，无法接收实时PING结果'
      isPinging.value = false
    })
  }

  // 更新统计信息
  const updateStatistics = () => {
    if (pingResults.value.length === 0) {
      currentPing.value = null
      return
    }

    const successResults = pingResults.value.filter(r => r.status === 'success')
    const packets_sent = pingResults.value.length
    const packets_received = successResults.length
    const packet_loss = ((packets_sent - packets_received) / packets_sent) * 100

    const responseTimes = successResults
      .map(r => r.response_time)
      .filter(t => t !== null && t !== undefined) as number[]

    let min_time = 0, max_time = 0, avg_time = 0
    if (responseTimes.length > 0) {
      min_time = Math.min(...responseTimes)
      max_time = Math.max(...responseTimes)
      avg_time = responseTimes.reduce((sum, t) => sum + t, 0) / responseTimes.length
    }

    // 🔧 强制修复：确保ping_id总是纯数字字符串，去除任何前缀
    let cleanPingId = currentPing.value?.ping_id || Date.now().toString()
    console.log('[DEBUG] updateStatistics - 原始ping_id:', currentPing.value?.ping_id)
    
    if (cleanPingId.startsWith('ping_')) {
      console.log('[DEBUG] updateStatistics - 检测到前缀，清理前:', cleanPingId)
      cleanPingId = cleanPingId.replace('ping_', '')
      console.log('[DEBUG] updateStatistics - 清理后:', cleanPingId)
    }

    currentPing.value = {
      ping_id: cleanPingId,
      target: pingConfig.value.target,
      packets_sent,
      packets_received,
      packet_loss,
      min_time,
      max_time,
      avg_time,
      total_time: Date.now() - (pingResults.value[pingResults.value.length - 1]?.timestamp ? new Date(pingResults.value[pingResults.value.length - 1].timestamp).getTime() : Date.now()),
      start_time: pingResults.value.length > 0 ? pingResults.value[pingResults.value.length - 1].timestamp : new Date().toISOString(),
      status: isPinging.value ? 'running' : 'completed'
    }
  }

  // 操作方法
  const startPing = async () => {
    try {
      loading.value = true
      error.value = null
      
      // 1. 使用API启动PING（如果有API端点）
      // 注意：根据后端实现，可能不需要API调用，直接使用WebSocket
      
      const pingId = Date.now().toString()  // 🔧 修复：简化ID格式，避免双重前缀
      console.log('[DEBUG] startPing - 生成的pingId:', pingId)
      
      isPinging.value = true
      pingResults.value = []
      
      // 2. 建立WebSocket连接开始PING
      setupWebSocketMonitoring(pingId)
      
      // 3. 初始化统计信息
      currentPing.value = {
        ping_id: pingId,
        target: pingConfig.value.target,
        packets_sent: 0,
        packets_received: 0,
        packet_loss: 0,
        min_time: 0,
        max_time: 0,
        avg_time: 0,
        total_time: 0,
        start_time: new Date().toISOString(),
        status: 'running'
      }
      
      console.log('[DEBUG] startPing - 设置的currentPing.ping_id:', currentPing.value.ping_id)
      
      // 如果不是连续模式，设置定时器停止
      if (!pingConfig.value.continuous && pingConfig.value.count > 0) {
        setTimeout(() => {
          if (isPinging.value) {
            stopPing()
          }
        }, pingConfig.value.count * pingConfig.value.interval * 1000 + 5000) // 额外5秒缓冲
      }
      
      return { ping_id: pingId }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '启动PING失败'
      console.error('Failed to start ping:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const stopPing = async () => {
    if (!currentPing.value?.ping_id) {
      isPinging.value = false
      return
    }
    
    try {
      loading.value = true
      
      const connectionId = `ping_${currentPing.value.ping_id}`
      console.log('[DEBUG] 停止PING - ping_id:', currentPing.value.ping_id)
      console.log('[DEBUG] 停止PING - connectionId:', connectionId)
      
      // 先发送停止信号给后端
      const connection = wsManager.getConnection(connectionId)
      console.log('[DEBUG] 查找WebSocket连接结果:', connection)
      
      if (connection && 'sendStopSignal' in connection) {
        try {
          console.log('[DEBUG] 发送停止信号到WebSocket连接')
          ;(connection as any).sendStopSignal()
          // 等待一段时间让后端处理停止信号
          await new Promise(resolve => setTimeout(resolve, 500))
        } catch (error) {
          console.warn('发送停止信号失败:', error)
        }
      } else {
        console.error('[ERROR] 未找到WebSocket连接，connectionId:', connectionId)
        console.error('[ERROR] 可能的连接ID:', wsManager.getAllActiveConnections())
      }
      
      // 设置状态为停止
      isPinging.value = false
      
      // 然后关闭WebSocket连接
      wsManager.removeConnection(connectionId)
      
      // 更新状态
      if (currentPing.value) {
        currentPing.value.status = 'completed'
        updateStatistics()
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '停止PING失败'
      console.error('Failed to stop ping:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const singlePing = async (target: string) => {
    try {
      loading.value = true
      error.value = null
      const result = await PingApi.singlePing(target)
      
      console.log('[DEBUG] 单次PING原始结果:', result)
      
      // 🔧 修复：API返回格式为 {success, message, data, timestamp}，需要提取data字段
      let actualResult = result
      if (result && typeof result === 'object' && 'data' in result) {
        actualResult = result.data
        console.log('[DEBUG] 提取API响应data字段:', actualResult)
      }
      
      // 如果data是数组，提取第一个元素
      if (Array.isArray(actualResult) && actualResult.length > 0) {
        actualResult = actualResult[0]
        console.log('[DEBUG] 提取数组第一个元素:', actualResult)
      }
      
      // 添加单次PING结果到列表，确保数据格式统一
      if (actualResult) {
        const pingResult: PingResult = {
          ping_id: 'single',
          target: target,
          sequence: pingResults.value.length + 1,
          response_time: actualResult.response_time !== undefined && actualResult.response_time !== null ? actualResult.response_time : null,
          ttl: actualResult.ttl !== undefined && actualResult.ttl !== null ? actualResult.ttl : null,
          packet_size: actualResult.packet_size || 64,
          timestamp: actualResult.timestamp ? new Date(actualResult.timestamp * 1000).toISOString() : new Date().toISOString(),
          status: actualResult.success ? 'success' : (actualResult.error_type === 'timeout' ? 'timeout' : 'error'),
          error: actualResult.error_message
        }
        
        console.log('[DEBUG] 处理后的PING结果:', pingResult)
        
        pingResults.value.unshift(pingResult)
        updateStatistics()
      }
      
      return actualResult
    } catch (err) {
      error.value = err instanceof Error ? err.message : '单次PING失败'
      console.error('Failed to single ping:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const reset = () => {
    if (currentPing.value?.ping_id) {
      wsManager.removeConnection(`ping_${currentPing.value.ping_id}`)
    }
    currentPing.value = null
    pingResults.value = []
    loading.value = false
    error.value = null
    isPinging.value = false
  }

  return {
    // 状态
    currentPing,
    pingResults,
    loading,
    error,
    isPinging,
    pingConfig,
    
    // 计算属性
    successRate,
    packetLoss,
    averageTime,
    canStartPing,
    
    // 方法
    startPing,
    stopPing,
    singlePing,
    clearError,
    reset
  }
}) 