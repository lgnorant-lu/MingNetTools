import apiClient from './client'

// PING相关类型定义
export interface PingConfig {
  target: string
  count: number
  interval: number
  timeout: number
  packet_size: number
  continuous: boolean
}

export interface PingResult {
  ping_id: string
  target: string
  sequence: number
  response_time: number | null
  ttl: number | null
  packet_size: number
  timestamp: string
  status: 'success' | 'timeout' | 'error'
  error?: string
}

export interface PingStatistics {
  ping_id: string
  target: string
  packets_sent: number
  packets_received: number
  packet_loss: number
  min_time: number
  max_time: number
  avg_time: number
  total_time: number
  start_time: string
  end_time?: string
  status: 'running' | 'completed' | 'stopped' | 'error'
}

export interface NetworkLatency {
  timestamp: string
  latency: number
  jitter: number
  packet_loss: number
}

// PING WebSocket参数类型
export interface PingWebSocketParams {
  target: string
  count: number
  interval: number
}

// PING API接口
export class PingApi {
  // 开始PING测试
  static async startPing(config: PingConfig) {
    const response = await apiClient.post('/ping/start', config)
    return response.data
  }

  // 停止PING测试
  static async stopPing(pingId: string) {
    const response = await apiClient.post(`/ping/stop/${pingId}`)
    return response.data
  }

  // 获取PING统计信息
  static async getPingStats(pingId: string): Promise<PingStatistics> {
    const response = await apiClient.get(`/ping/stats/${pingId}`)
    return response.data
  }

  // 获取PING结果
  static async getPingResults(pingId: string, limit?: number): Promise<PingResult[]> {
    const params = limit ? { limit } : {}
    const response = await apiClient.get(`/ping/results/${pingId}`, { params })
    return response.data
  }

  // 获取PING历史
  static async getPingHistory() {
    const response = await apiClient.get('/ping/history')
    return response.data
  }

  // 删除PING记录
  static async deletePing(pingId: string) {
    const response = await apiClient.delete(`/ping/${pingId}`)
    return response.data
  }

  // 单次PING测试
  static async singlePing(target: string, timeout: number = 3) {
    const response = await apiClient.post('/ping/single', { target, timeout })
    return response.data
  }

  // 批量PING测试
  static async batchPing(targets: string[], timeout: number = 3) {
    const response = await apiClient.post('/ping/batch', { targets, timeout })
    return response.data
  }

  // 网络延迟监控
  static async getNetworkLatency(target: string, hours: number = 24): Promise<NetworkLatency[]> {
    const response = await apiClient.get('/ping/latency', {
      params: { target, hours }
    })
    return response.data
  }

  // 网络质量评估
  static async getNetworkQuality(target: string) {
    const response = await apiClient.get('/ping/quality', {
      params: { target }
    })
    return response.data
  }

  // 导出PING结果
  static async exportResults(pingId: string, format: 'json' | 'csv' = 'json') {
    const response = await apiClient.get(`/ping/export/${pingId}`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }
}

// PING WebSocket连接管理
export class PingWebSocket {
  private url: string
  private ws: WebSocket | null = null
  private heartbeatInterval: number | null = null
  private readonly HEARTBEAT_INTERVAL = 30000 // 30秒
  private isConnected = false
  private subscriptions = new Set<string>()

  constructor(params: PingWebSocketParams) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.host
    let url = `${wsProtocol}//${wsHost}/api/v1/ws/ping`
    
    // 添加查询参数
    const queryParams = new URLSearchParams()
    if (params.target) queryParams.append('target', params.target)
    if (params.count !== undefined) queryParams.append('count', params.count.toString())
    if (params.interval !== undefined) queryParams.append('interval', params.interval.toString())
    
    const queryString = queryParams.toString()
    if (queryString) {
      url = `${url}?${queryString}`
    }
    
    this.url = url
  }

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void): void {
    this.disconnect() // 确保没有现有连接
    
    this.ws = new WebSocket(this.url)
    
    this.ws.onopen = () => {
      console.log('[PingWebSocket] 连接成功')
      this.isConnected = true
      this.startHeartbeat() // 启动心跳
    }
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.resetHeartbeat() // 重置心跳定时器
        onMessage(data)
      } catch (error) {
        console.error('[PingWebSocket] 解析消息失败:', error)
      }
    }
    
    this.ws.onerror = (error) => {
      console.error('[PingWebSocket] WebSocket错误:', error)
      this.isConnected = false
      this.stopHeartbeat()
      if (onError) {
        onError(error)
      }
    }
    
    this.ws.onclose = () => {
      console.log('[PingWebSocket] 连接关闭')
      this.isConnected = false
      this.stopHeartbeat()
    }
  }

  /**
   * 启动心跳
   */
  private startHeartbeat(): void {
    this.stopHeartbeat() // 先停止现有心跳
    this.heartbeatInterval = setInterval(() => {
      this.sendHeartbeat()
    }, this.HEARTBEAT_INTERVAL)
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 重置心跳定时器
   */
  private resetHeartbeat(): void {
    if (this.isConnected) {
      this.startHeartbeat()
    }
  }

  /**
   * 发送心跳
   */
  sendHeartbeat(): void {
    if (this.ws && this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }))
      } catch (error) {
        console.error('[PingWebSocket] 发送心跳失败:', error)
        this.isConnected = false
        this.stopHeartbeat()
      }
    }
  }

  subscribe(pingId: string): void {
    this.subscriptions.add(pingId)
    if (this.ws && this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        ping_id: pingId
      }))
    }
  }

  unsubscribe(pingId: string): void {
    this.subscriptions.delete(pingId)
    if (this.ws && this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'unsubscribe',
        ping_id: pingId
      }))
    }
  }

  disconnect(): void {
    this.stopHeartbeat()
    if (this.ws) {
      this.isConnected = false
      this.ws.close()
      this.ws = null
    }
    this.subscriptions.clear()
  }

  getConnectionState(): boolean {
    return this.isConnected && this.ws?.readyState === WebSocket.OPEN
  }

  /**
   * 发送停止信号
   */
  sendStopSignal(): void {
    if (this.ws && this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify({ type: 'stop_ping', timestamp: Date.now() }))
      } catch (error) {
        console.error('[PingWebSocket] 发送停止信号失败:', error)
      }
    }
  }
} 