import apiClient from './client'

// 扫描相关类型定义
export interface ScanConfig {
  target: string
  ports: string
  scan_type: 'tcp' | 'udp' | 'syn'
  timeout: number
  max_threads: number
}

export interface ScanResult {
  scan_id: string
  target: string
  port: number
  status: 'open' | 'closed' | 'filtered'
  service?: string
  timestamp: string
}

export interface ScanStatus {
  scan_id: string
  status: 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  total_ports: number
  scanned_ports: number
  found_ports: number
  start_time: string
  end_time?: string
  error?: string
}

// API响应类型定义
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 扫描WebSocket参数类型
export interface ScanWebSocketParams {
  targets: string
  ports: string
  scan_type: string
  max_threads?: number
}

// 扫描API接口
export class ScanApi {
  // 开始扫描
  static async startScan(config: ScanConfig) {
    const response = await apiClient.post('/scan/start', config, {
      timeout: 30000 // 🔧 修复：扫描启动需要更长时间，设置30秒超时
    })
    return response.data
  }

  // 获取扫描状态
  static async getScanStatus(scanId: string): Promise<ScanStatus> {
    const response = await apiClient.get(`/scan/status/${scanId}`)
    return response.data
  }

  // 获取扫描结果
  static async getScanResults(scanId: string): Promise<ScanResult[]> {
    const response = await apiClient.get(`/scan/results/${scanId}`)
    return response.data
  }

  // 停止扫描
  static async stopScan(scanId: string) {
    if (!scanId || scanId === 'undefined') {
      return Promise.reject({ 
        error: 'invalid_scan_id', 
        message: '无效的扫描ID', 
        data: { scan_id: scanId }
      });
    }
    const response = await apiClient.post(`/scan/stop/${scanId}`);
    return response.data;
  }

  // 获取扫描历史
  static async getScanHistory() {
    const response = await apiClient.get('/scan/history')
    return response.data
  }

  // 删除扫描记录
  static async deleteScan(scanId: string) {
    const response = await apiClient.delete(`/scan/${scanId}`)
    return response.data
  }

  // 获取扫描统计信息
  static async getScanStats() {
    const response = await apiClient.get('/scan/stats')
    return response.data
  }

  // 导出扫描结果
  static async exportResults(scanId: string, format: 'json' | 'csv' | 'xml' = 'json') {
    const response = await apiClient.get(`/scan/export/${scanId}`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }
}

// WebSocket连接管理
export class ScanWebSocket {
  private url: string
  private ws: WebSocket | null = null
  private heartbeatInterval: number | null = null
  private readonly HEARTBEAT_INTERVAL = 30000 // 30秒
  private isConnected = false

  constructor(params: ScanWebSocketParams) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.host
    
    // 构建完整 URL，确保使用正确路径
    let url = `${wsProtocol}//${wsHost}/api/v1/ws/scan`
    
    console.log(`[ScanWebSocket] 初始 URL: ${url}`)
    
    // 添加查询参数
    const queryParams = new URLSearchParams()
    if (params.targets) queryParams.append('targets', params.targets)
    if (params.ports) queryParams.append('ports', params.ports)
    if (params.scan_type) queryParams.append('scan_type', params.scan_type)
    if (params.max_threads !== undefined) queryParams.append('max_threads', params.max_threads.toString())
    
    const queryString = queryParams.toString()
    if (queryString) {
      url = `${url}?${queryString}`
    }
    
    this.url = url
    console.log(`[ScanWebSocket] 最终WebSocket URL: ${this.url}`)
  }

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void): void {
    this.disconnect() // 确保没有现有连接
    
    this.ws = new WebSocket(this.url)
    
    this.ws.onopen = () => {
      console.log('[ScanWebSocket] 连接成功')
      this.isConnected = true
      this.startHeartbeat() // 启动心跳
    }
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.resetHeartbeat() // 重置心跳定时器
        onMessage(data)
      } catch (error) {
        console.error('[ScanWebSocket] 解析消息失败:', error)
      }
    }
    
    this.ws.onerror = (error) => {
      console.error('[ScanWebSocket] WebSocket错误:', error)
      this.isConnected = false
      this.stopHeartbeat()
      if (onError) {
        onError(error)
      }
    }
    
    this.ws.onclose = () => {
      console.log('[ScanWebSocket] 连接关闭')
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
        console.error('[ScanWebSocket] 发送心跳失败:', error)
        this.isConnected = false
        this.stopHeartbeat()
      }
    }
  }

  disconnect(): void {
    this.stopHeartbeat()
    if (this.ws) {
      this.isConnected = false
      this.ws.close()
      this.ws = null
    }
  }

  getConnectionState(): boolean {
    return this.isConnected && this.ws?.readyState === WebSocket.OPEN
  }
} 