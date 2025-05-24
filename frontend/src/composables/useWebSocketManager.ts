/**
 * WebSocket全局管理器
 * 解决页面切换时WebSocket连接断开的问题
 */

import { ref, onUnmounted, onBeforeUnmount } from 'vue'
import { ScanWebSocket } from '@/api/scanApi'
import { PingWebSocket } from '@/api/pingApi'

// 全局WebSocket连接池
const globalConnections = new Map<string, {
  socket: ScanWebSocket | PingWebSocket | null,
  lastActivity: number,
  type: 'scan' | 'ping',
  keepAlive: boolean
}>()

// 心跳间隔(30秒)
const HEARTBEAT_INTERVAL = 30000
// 连接超时时间(5分钟无活动自动断开)
const CONNECTION_TIMEOUT = 5 * 60 * 1000

export function useWebSocketManager() {
  const activeConnections = ref<string[]>([])
  
  // 清理过期连接的定时器
  const cleanupTimer = setInterval(() => {
    const now = Date.now()
    const expiredKeys: string[] = []
    
    globalConnections.forEach((connection, key) => {
      if (!connection.keepAlive && (now - connection.lastActivity) > CONNECTION_TIMEOUT) {
        expiredKeys.push(key)
      }
    })
    
    expiredKeys.forEach(key => {
      const connection = globalConnections.get(key)
      if (connection?.socket) {
        connection.socket.disconnect()
      }
      globalConnections.delete(key)
      const index = activeConnections.value.indexOf(key)
      if (index > -1) {
        activeConnections.value.splice(index, 1)
      }
    })
  }, 60000) // 每分钟清理一次

  /**
   * 获取或创建WebSocket连接
   */
  const getOrCreateConnection = <T extends ScanWebSocket | PingWebSocket>(
    connectionId: string,
    type: 'scan' | 'ping',
    factory: () => T,
    keepAlive: boolean = true
  ): T => {
    let connection = globalConnections.get(connectionId)
    
    if (!connection || !connection.socket) {
      // 创建新连接
      const socket = factory()
      connection = {
        socket,
        lastActivity: Date.now(),
        type,
        keepAlive
      }
      globalConnections.set(connectionId, connection)
      
      if (!activeConnections.value.includes(connectionId)) {
        activeConnections.value.push(connectionId)
      }
      
      // 为WebSocket添加心跳保持活跃
      if (keepAlive) {
        const heartbeatTimer = setInterval(() => {
          if (connection?.socket && globalConnections.has(connectionId)) {
            // 发送心跳保持连接活跃
            try {
              if ('sendHeartbeat' in connection.socket) {
                (connection.socket as any).sendHeartbeat()
              }
              connection.lastActivity = Date.now()
            } catch (error) {
              console.warn(`WebSocket心跳失败 (${connectionId}):`, error)
              // 心跳失败，清理连接
              clearInterval(heartbeatTimer)
              removeConnection(connectionId)
            }
          } else {
            clearInterval(heartbeatTimer)
          }
        }, HEARTBEAT_INTERVAL)
      }
    } else {
      // 更新活动时间
      connection.lastActivity = Date.now()
      connection.keepAlive = keepAlive
    }
    
    return connection.socket as T
  }

  /**
   * 移除连接
   */
  const removeConnection = (connectionId: string) => {
    const connection = globalConnections.get(connectionId)
    if (connection?.socket) {
      connection.socket.disconnect()
    }
    globalConnections.delete(connectionId)
    
    const index = activeConnections.value.indexOf(connectionId)
    if (index > -1) {
      activeConnections.value.splice(index, 1)
    }
  }

  /**
   * 标记连接为活跃状态
   */
  const markConnectionActive = (connectionId: string) => {
    const connection = globalConnections.get(connectionId)
    if (connection) {
      connection.lastActivity = Date.now()
    }
  }

  /**
   * 设置连接的保持活跃状态
   */
  const setConnectionKeepAlive = (connectionId: string, keepAlive: boolean) => {
    const connection = globalConnections.get(connectionId)
    if (connection) {
      connection.keepAlive = keepAlive
    }
  }

  /**
   * 获取所有活跃连接
   */
  const getAllActiveConnections = () => {
    return Array.from(globalConnections.keys())
  }

  /**
   * 清理所有连接
   */
  const cleanupAllConnections = () => {
    globalConnections.forEach((connection) => {
      if (connection.socket) {
        connection.socket.disconnect()
      }
    })
    globalConnections.clear()
    activeConnections.value = []
  }

  /**
   * 获取现有连接
   */
  const getConnection = (connectionId: string) => {
    const connection = globalConnections.get(connectionId)
    return connection?.socket || null
  }

  // 组件卸载时清理
  onBeforeUnmount(() => {
    clearInterval(cleanupTimer)
  })

  return {
    activeConnections,
    getOrCreateConnection,
    removeConnection,
    markConnectionActive,
    setConnectionKeepAlive,
    getAllActiveConnections,
    cleanupAllConnections,
    getConnection
  }
}

// 单例模式导出全局管理器
let globalManager: ReturnType<typeof useWebSocketManager> | null = null

export function getGlobalWebSocketManager() {
  if (!globalManager) {
    globalManager = useWebSocketManager()
  }
  return globalManager
} 