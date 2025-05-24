import axios, { type AxiosInstance, type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

// 检查环境变量
console.log('环境变量检查:', {
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  VITE_WS_HOST: import.meta.env.VITE_WS_HOST,
  mode: import.meta.env.MODE,
})

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`)
    return response
  },
  (error: AxiosError) => {
    console.error('[API Response Error]', error)
    
    // 统一错误处理
    let message = '网络请求失败'
    
    if (error.response) {
      const status = error.response.status
      const data = error.response.data as any
      
      switch (status) {
        case 400:
          message = data?.detail || '请求参数错误'
          break
        case 401:
          message = '未授权访问'
          break
        case 403:
          message = '禁止访问'
          break
        case 404:
          message = '接口不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data?.detail || `请求失败 (${status})`
      }
    } else if (error.request) {
      message = '网络连接失败，请检查后端服务是否启动'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default apiClient

// API响应类型定义
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 健康检查
export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health')
    return response.status === 200
  } catch (error) {
    console.error('Health check failed:', error)
    return false
  }
} 