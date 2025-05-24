import apiClient from './client'

// 系统监控相关类型定义
export interface SystemStatus {
  timestamp: string
  status: 'healthy' | 'warning' | 'error'
  uptime: number
  cpu_usage: number
  memory_usage: number
  disk_usage: number
}

export interface ServiceStatus {
  service_name: string
  status: 'running' | 'stopped' | 'error'
  port?: number
  uptime: number
  last_check: string
}

export interface PerformanceStats {
  total_scans: number
  active_scans: number
  total_pings: number
  active_pings: number
  total_tcp_connections: number
  active_tcp_connections: number
  avg_response_time: number
  success_rate: number
  error_rate: number
  uptime_hours: number
}

// 系统监控API
export class SystemApi {
  // 获取系统健康状态
  static async getHealth() {
    const response = await apiClient.get('/health')
    return response.data
  }

  // 获取系统状态
  static async getSystemStatus(): Promise<SystemStatus> {
    const response = await apiClient.get('/api/v1/system/status')
    return response.data
  }

  // 获取服务状态
  static async getServiceStatus(): Promise<ServiceStatus[]> {
    const response = await apiClient.get('/api/v1/system/services')
    return response.data
  }

  // 获取性能统计
  static async getPerformanceStats(): Promise<PerformanceStats> {
    const response = await apiClient.get('/api/v1/system/performance')
    return response.data
  }

  // 获取系统信息
  static async getSystemInfo() {
    const response = await apiClient.get('/api/v1/system/info')
    return response.data
  }
} 