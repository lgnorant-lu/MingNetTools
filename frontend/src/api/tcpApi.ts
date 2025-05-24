import apiClient from './client'

// TCP相关类型定义
export interface TcpServerConfig {
  host: string
  port: number
  max_connections: number
  buffer_size: number
  auto_start: boolean
}

export interface TcpClientConfig {
  host: string
  port: number
  timeout: number
  auto_reconnect: boolean
  reconnect_interval: number
}

export interface TcpConnection {
  connection_id: string
  client_ip: string
  client_port: number
  server_port: number
  connected_time: string
  last_activity: string
  bytes_sent: number
  bytes_received: number
  status: 'connected' | 'disconnected' | 'error'
}

export interface TcpMessage {
  message_id: string
  connection_id: string
  direction: 'sent' | 'received'
  content: string
  message_type: 'text' | 'binary' | 'json'
  timestamp: string
  size: number
}

export interface TcpServerStatus {
  server_id: string
  host: string
  port: number
  status: 'running' | 'stopped' | 'error'
  connections_count: number
  max_connections: number
  start_time?: string
  total_bytes_sent: number
  total_bytes_received: number
  total_messages: number
}

// TCP服务器API
export class TcpServerApi {
  // 创建TCP服务器
  static async createServer(config: TcpServerConfig) {
    const response = await apiClient.post('/api/v1/tcp/server/create', config)
    return response.data
  }

  // 启动服务器
  static async startServer(serverId: string) {
    const response = await apiClient.post(`/api/v1/tcp/server/${serverId}/start`)
    return response.data
  }

  // 停止服务器
  static async stopServer(serverId: string) {
    const response = await apiClient.post(`/api/v1/tcp/server/${serverId}/stop`)
    return response.data
  }

  // 获取服务器状态
  static async getServerStatus(serverId: string): Promise<TcpServerStatus> {
    const response = await apiClient.get(`/api/v1/tcp/server/${serverId}/status`)
    return response.data
  }

  // 获取所有服务器
  static async getServers() {
    const response = await apiClient.get('/api/v1/tcp/servers')
    return response.data
  }

  // 获取服务器连接列表
  static async getConnections(serverId: string): Promise<TcpConnection[]> {
    const response = await apiClient.get(`/api/v1/tcp/server/${serverId}/connections`)
    return response.data
  }

  // 向指定连接发送消息
  static async sendToConnection(serverId: string, connectionId: string, message: string) {
    const response = await apiClient.post(`/api/v1/tcp/server/${serverId}/send/${connectionId}`, {
      message
    })
    return response.data
  }

  // 广播消息
  static async broadcast(serverId: string, message: string) {
    const response = await apiClient.post(`/api/v1/tcp/server/${serverId}/broadcast`, {
      message
    })
    return response.data
  }
}

// TCP客户端API
export class TcpClientApi {
  // 创建TCP客户端
  static async createClient(config: TcpClientConfig) {
    const response = await apiClient.post('/api/v1/tcp/client/create', config)
    return response.data
  }

  // 连接到服务器
  static async connect(clientId: string) {
    const response = await apiClient.post(`/api/v1/tcp/client/${clientId}/connect`)
    return response.data
  }

  // 断开连接
  static async disconnect(clientId: string) {
    const response = await apiClient.post(`/api/v1/tcp/client/${clientId}/disconnect`)
    return response.data
  }

  // 发送消息
  static async sendMessage(clientId: string, message: string) {
    const response = await apiClient.post(`/api/v1/tcp/client/${clientId}/send`, {
      message
    })
    return response.data
  }

  // 获取客户端状态
  static async getClientStatus(clientId: string) {
    const response = await apiClient.get(`/api/v1/tcp/client/${clientId}/status`)
    return response.data
  }

  // 获取所有客户端
  static async getClients() {
    const response = await apiClient.get('/api/v1/tcp/clients')
    return response.data
  }
} 