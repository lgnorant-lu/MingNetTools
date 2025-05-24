/**
---------------------------------------------------------------
File name:                  i18n.ts
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                国际化语言设置store，支持中英文切换
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现多语言管理系统;
----
*/

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 支持的语言类型
export type Language = 'zh' | 'en'

// 翻译数据结构
export interface TranslationData {
  [key: string]: string | TranslationData
}

// 语言配置
export interface LanguageConfig {
  code: Language
  name: string
  nativeName: string
  flag: string
}

export const useI18nStore = defineStore('i18n', () => {
  // 状态
  const currentLanguage = ref<Language>('zh')
  const isLoading = ref(false)
  
  // 支持的语言配置
  const supportedLanguages: LanguageConfig[] = [
    {
      code: 'zh',
      name: 'Chinese',
      nativeName: '中文',
      flag: '🇨🇳'
    },
    {
      code: 'en', 
      name: 'English',
      nativeName: 'English',
      flag: '🇺🇸'
    }
  ]

  // 翻译数据
  const translations = ref<Record<Language, TranslationData>>({
    zh: {
      // 通用
      common: {
        ok: '确定',
        cancel: '取消',
        save: '保存',
        delete: '删除',
        edit: '编辑',
        add: '添加',
        search: '搜索',
        loading: '加载中...',
        error: '错误',
        success: '成功',
        warning: '警告',
        info: '信息',
        refresh: '刷新',
        reset: '重置',
        close: '关闭',
        back: '返回',
        next: '下一步',
        previous: '上一步',
        confirm: '确认',
        copy: '复制',
        export: '导出',
        import: '导入'
      },
      
      // 导航
      nav: {
        dashboard: '仪表板',
        scan: '扫描工具',
        ping: 'PING监控',
        tcp: 'TCP通信',
        settings: '设置',
        about: '关于'
      },
      
      // 仪表板
      dashboard: {
        title: '系统仪表板',
        subtitle: '网络安全工具监控中心',
        systemStatus: '系统状态',
        networkStatus: '网络状态',
        apiStatus: 'API状态',
        performance: '性能监控',
        recentActivity: '最近活动',
        quickActions: '快速操作'
      },
      
      // PING监控
      ping: {
        title: 'PING网络监控',
        subtitle: '实时网络延迟监控和连通性检测',
        config: '监控配置',
        target: '目标主机',
        targetPlaceholder: '输入IP地址或域名，如: google.com',
        count: 'PING次数',
        interval: '时间间隔 (秒)',
        timeout: '超时时间 (秒)',
        packetSize: '数据包大小 (字节)',
        continuous: '连续监控模式',
        start: '开始PING',
        stop: '停止PING',
        single: '单次PING',
        running: 'PING中...',
        monitoring: '监控中',
        statistics: 'PING统计',
        results: 'PING结果',
        sent: '已发送',
        received: '已接收',
        minTime: '最小延迟',
        maxTime: '最大延迟',
        avgTime: '平均延迟',
        successRate: '成功率',
        packetLoss: '丢包率',
        success: '成功',
        failed: '失败'
      },
      
      // 端口扫描
      scan: {
        title: '端口扫描工具',
        subtitle: '强大的网络端口扫描和服务发现工具',
        config: '扫描配置',
        target: '扫描目标',
        targetPlaceholder: '输入IP地址或域名，如: 192.168.1.1',
        ports: '端口范围',
        portsPlaceholder: '如: 1-1000, 80,443 或 22,80,443',
        scanType: '扫描类型',
        tcpScan: 'TCP连接扫描',
        udpScan: 'UDP扫描',
        synScan: 'SYN扫描',
        timeout: '超时时间 (秒)',
        threads: '最大线程数',
        quickScan: '快速扫描',
        fullScan: '全端口扫描',
        stealthScan: '隐蔽扫描',
        start: '开始扫描',
        stop: '停止扫描',
        scanning: '扫描中...',
        progress: '扫描进度',
        status: '扫描状态',
        scanned: '已扫描',
        found: '发现端口',
        startTime: '开始时间',
        results: '扫描结果',
        open: '开放',
        closed: '关闭',
        filtered: '过滤',
        total: '总计'
      },
      
      // TCP通信
      tcp: {
        title: 'TCP通信实验室',
        subtitle: '实时TCP客户端和服务器通信工具',
        server: '服务器',
        client: '客户端',
        port: '端口',
        host: '主机',
        start: '启动',
        stop: '停止',
        connect: '连接',
        disconnect: '断开',
        send: '发送',
        clear: '清空',
        status: '状态',
        running: '运行中',
        stopped: '已停止',
        connected: '已连接',
        disconnected: '已断开',
        message: '消息',
        messagePlaceholder: '输入要发送的消息...',
        log: '通信日志',
        connections: '连接数'
      },
      
      // 设置
      settings: {
        title: '系统设置',
        theme: '主题设置',
        font: '字体设置',
        language: '语言设置',
        accessibility: '无障碍设置',
        performance: '性能设置',
        export: '导出设置',
        import: '导入设置',
        reset: '重置设置'
      },
      
      // 字体设置
      font: {
        type: '字体类型',
        pixel: '像素字体',
        standard: '标准字体',
        hybrid: '混合字体',
        size: '字体大小',
        comfort: '舒适度',
        normal: '正常',
        soft: '柔和',
        comfortable: '舒适',
        lineHeight: '行高',
        letterSpacing: '字符间距',
        preset: '预设',
        gaming: '游戏风格',
        readability: '可读性',
        accessibility: '无障碍'
      },
      
      // 主题设置
      theme: {
        mode: '主题模式',
        dark: '黑夜模式',
        light: '白天模式',
        auto: '自动切换',
        colors: '色彩配置',
        primary: '主色调',
        secondary: '辅助色',
        accent: '强调色'
      },
      
      // 错误信息
      errors: {
        networkError: '网络连接错误',
        serverError: '服务器错误', 
        invalidInput: '输入无效',
        timeout: '请求超时',
        unauthorized: '未授权访问',
        notFound: '资源不存在',
        unknown: '未知错误'
      },
      
      // 成功信息
      success: {
        saved: '保存成功',
        deleted: '删除成功',
        connected: '连接成功',
        disconnected: '断开连接成功',
        copied: '复制成功',
        exported: '导出成功',
        imported: '导入成功'
      }
    },
    
    en: {
      // Common
      common: {
        ok: 'OK',
        cancel: 'Cancel',
        save: 'Save',
        delete: 'Delete',
        edit: 'Edit',
        add: 'Add',
        search: 'Search',
        loading: 'Loading...',
        error: 'Error',
        success: 'Success',
        warning: 'Warning',
        info: 'Info',
        refresh: 'Refresh',
        reset: 'Reset',
        close: 'Close',
        back: 'Back',
        next: 'Next',
        previous: 'Previous',
        confirm: 'Confirm',
        copy: 'Copy',
        export: 'Export',
        import: 'Import'
      },
      
      // Navigation
      nav: {
        dashboard: 'Dashboard',
        scan: 'Scan Tools',
        ping: 'PING Monitor',
        tcp: 'TCP Lab',
        settings: 'Settings',
        about: 'About'
      },
      
      // Dashboard
      dashboard: {
        title: 'System Dashboard',
        subtitle: 'Network Security Tools Monitoring Center',
        systemStatus: 'System Status',
        networkStatus: 'Network Status',
        apiStatus: 'API Status',
        performance: 'Performance Monitor',
        recentActivity: 'Recent Activity',
        quickActions: 'Quick Actions'
      },
      
      // PING Monitor
      ping: {
        title: 'PING Network Monitor',
        subtitle: 'Real-time network latency monitoring and connectivity detection',
        config: 'Monitor Configuration',
        target: 'Target Host',
        targetPlaceholder: 'Enter IP address or domain, e.g: google.com',
        count: 'PING Count',
        interval: 'Interval (seconds)',
        timeout: 'Timeout (seconds)',
        packetSize: 'Packet Size (bytes)',
        continuous: 'Continuous Monitoring Mode',
        start: 'Start PING',
        stop: 'Stop PING',
        single: 'Single PING',
        running: 'PING Running...',
        monitoring: 'Monitoring',
        statistics: 'PING Statistics',
        results: 'PING Results',
        sent: 'Sent',
        received: 'Received',
        minTime: 'Min Time',
        maxTime: 'Max Time',
        avgTime: 'Avg Time',
        successRate: 'Success Rate',
        packetLoss: 'Packet Loss',
        success: 'Success',
        failed: 'Failed'
      },
      
      // Port Scanner
      scan: {
        title: 'Port Scanner Tool',
        subtitle: 'Powerful network port scanning and service discovery tool',
        config: 'Scan Configuration',
        target: 'Scan Target',
        targetPlaceholder: 'Enter IP address or domain, e.g: 192.168.1.1',
        ports: 'Port Range',
        portsPlaceholder: 'e.g: 1-1000, 80,443 or 22,80,443',
        scanType: 'Scan Type',
        tcpScan: 'TCP Connect Scan',
        udpScan: 'UDP Scan',
        synScan: 'SYN Scan',
        timeout: 'Timeout (seconds)',
        threads: 'Max Threads',
        quickScan: 'Quick Scan',
        fullScan: 'Full Port Scan',
        stealthScan: 'Stealth Scan',
        start: 'Start Scan',
        stop: 'Stop Scan',
        scanning: 'Scanning...',
        progress: 'Scan Progress',
        status: 'Scan Status',
        scanned: 'Scanned',
        found: 'Found Ports',
        startTime: 'Start Time',
        results: 'Scan Results',
        open: 'Open',
        closed: 'Closed',
        filtered: 'Filtered',
        total: 'Total'
      },
      
      // TCP Lab
      tcp: {
        title: 'TCP Communication Lab',
        subtitle: 'Real-time TCP client and server communication tool',
        server: 'Server',
        client: 'Client',
        port: 'Port',
        host: 'Host',
        start: 'Start',
        stop: 'Stop',
        connect: 'Connect',
        disconnect: 'Disconnect',
        send: 'Send',
        clear: 'Clear',
        status: 'Status',
        running: 'Running',
        stopped: 'Stopped',
        connected: 'Connected',
        disconnected: 'Disconnected',
        message: 'Message',
        messagePlaceholder: 'Enter message to send...',
        log: 'Communication Log',
        connections: 'Connections'
      },
      
      // Settings
      settings: {
        title: 'System Settings',
        theme: 'Theme Settings',
        font: 'Font Settings',
        language: 'Language Settings',
        accessibility: 'Accessibility Settings',
        performance: 'Performance Settings',
        export: 'Export Settings',
        import: 'Import Settings',
        reset: 'Reset Settings'
      },
      
      // Font Settings
      font: {
        type: 'Font Type',
        pixel: 'Pixel Font',
        standard: 'Standard Font',
        hybrid: 'Hybrid Font',
        size: 'Font Size',
        comfort: 'Comfort Level',
        normal: 'Normal',
        soft: 'Soft',
        comfortable: 'Comfortable',
        lineHeight: 'Line Height',
        letterSpacing: 'Letter Spacing',
        preset: 'Preset',
        gaming: 'Gaming Style',
        readability: 'Readability',
        accessibility: 'Accessibility'
      },
      
      // Theme Settings
      theme: {
        mode: 'Theme Mode',
        dark: 'Dark Mode',
        light: 'Light Mode',
        auto: 'Auto Switch',
        colors: 'Color Configuration',
        primary: 'Primary Color',
        secondary: 'Secondary Color',
        accent: 'Accent Color'
      },
      
      // Error Messages
      errors: {
        networkError: 'Network Connection Error',
        serverError: 'Server Error',
        invalidInput: 'Invalid Input',
        timeout: 'Request Timeout',
        unauthorized: 'Unauthorized Access',
        notFound: 'Resource Not Found',
        unknown: 'Unknown Error'
      },
      
      // Success Messages
      success: {
        saved: 'Saved Successfully',
        deleted: 'Deleted Successfully',
        connected: 'Connected Successfully',
        disconnected: 'Disconnected Successfully',
        copied: 'Copied Successfully',
        exported: 'Exported Successfully',
        imported: 'Imported Successfully'
      }
    }
  })

  // 计算属性
  const currentLanguageConfig = computed(() => {
    return supportedLanguages.find(lang => lang.code === currentLanguage.value) || supportedLanguages[0]
  })

  const currentTranslations = computed(() => {
    return translations.value[currentLanguage.value] || translations.value.zh
  })

  // 方法
  
  /**
   * 切换语言
   */
  const setLanguage = async (language: Language): Promise<void> => {
    if (language === currentLanguage.value) return
    
    isLoading.value = true
    
    try {
      // 模拟加载延迟
      await new Promise(resolve => setTimeout(resolve, 100))
      
      currentLanguage.value = language
      saveLanguageSettings()
      
      // 更新HTML lang属性
      document.documentElement.lang = language
      
      // 触发语言切换事件
      window.dispatchEvent(new CustomEvent('language-changed', {
        detail: { language, config: currentLanguageConfig.value }
      }))
      
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取翻译文本
   */
  const t = (key: string, fallback?: string): string => {
    const keys = key.split('.')
    let value: any = currentTranslations.value
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        return fallback || key
      }
    }
    
    return typeof value === 'string' ? value : fallback || key
  }

  /**
   * 检查是否存在翻译
   */
  const hasTranslation = (key: string): boolean => {
    const keys = key.split('.')
    let value: any = currentTranslations.value
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        return false
      }
    }
    
    return typeof value === 'string'
  }

  /**
   * 获取支持的语言列表
   */
  const getSupportedLanguages = (): LanguageConfig[] => {
    return [...supportedLanguages]
  }

  /**
   * 保存语言设置
   */
  const saveLanguageSettings = (): void => {
    try {
      localStorage.setItem('language', currentLanguage.value)
    } catch (error) {
      console.warn('Failed to save language settings:', error)
    }
  }

  /**
   * 加载语言设置
   */
  const loadLanguageSettings = (): void => {
    try {
      const saved = localStorage.getItem('language')
      if (saved && supportedLanguages.find(lang => lang.code === saved)) {
        currentLanguage.value = saved as Language
      }
    } catch (error) {
      console.warn('Failed to load language settings:', error)
    }
  }

  /**
   * 获取浏览器首选语言
   */
  const getBrowserLanguage = (): Language => {
    const browserLang = navigator.language.toLowerCase()
    
    if (browserLang.startsWith('zh')) {
      return 'zh'
    } else if (browserLang.startsWith('en')) {
      return 'en'
    }
    
    // 默认返回中文
    return 'zh'
  }

  /**
   * 初始化国际化系统
   */
  const initI18n = (): void => {
    loadLanguageSettings()
    
    // 如果没有保存的设置，使用浏览器语言
    if (!localStorage.getItem('language')) {
      currentLanguage.value = getBrowserLanguage()
    }
    
    // 设置HTML lang属性
    document.documentElement.lang = currentLanguage.value
  }

  /**
   * 添加新的翻译
   */
  const addTranslation = (language: Language, key: string, value: string): void => {
    const keys = key.split('.')
    let target = translations.value[language]
    
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i]
      if (!(k in target) || typeof target[k] !== 'object') {
        target[k] = {}
      }
      target = target[k] as TranslationData
    }
    
    target[keys[keys.length - 1]] = value
  }

  return {
    // 状态
    currentLanguage,
    isLoading,
    supportedLanguages,
    
    // 计算属性
    currentLanguageConfig,
    currentTranslations,
    
    // 方法
    setLanguage,
    t,
    hasTranslation,
    getSupportedLanguages,
    initI18n,
    addTranslation,
    getBrowserLanguage
  }
}) 