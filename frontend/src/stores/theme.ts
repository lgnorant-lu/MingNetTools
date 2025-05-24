import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 主题类型定义
export type ThemeMode = 'dark' | 'light' | 'ocean' | 'forest' | 'sunset' | 'aurora'

// 主题触发条件
export interface ThemeTrigger {
  condition: 'manual' | 'time' | 'system' | 'auto'
  description: string
  timeRange?: { start: string; end: string }
}

// 主题配色方案
export interface ThemeColors {
  // 主要颜色
  primary: string
  secondary: string
  accent: string
  warning: string
  danger: string
  success: string
  
  // 霓虹色系
  neonCyan: string
  neonPink: string
  neonGreen: string
  neonPurple: string
  neonOrange: string
  
  // 背景色
  bgDark: string
  bgDarker: string
  bgGrid: string
  
  // 文字颜色
  textPrimary: string
  textSecondary: string
  textAccent: string
}

// 主题定义
export interface ThemeDefinition {
  name: string
  description: string
  icon: string
  colors: ThemeColors
  trigger: ThemeTrigger
}

// 黑夜主题（现有的像素风格）
const darkTheme: ThemeDefinition = {
  name: '赛博夜晚',
  description: '经典赛博朋克风格，适合夜间使用',
  icon: '🌙',
  trigger: {
    condition: 'time',
    description: '自动切换：18:00-6:00',
    timeRange: { start: '18:00', end: '06:00' }
  },
  colors: {
    primary: '#00ff41',
    secondary: '#ff0080', 
    accent: '#00d4ff',
    warning: '#ffff00',
    danger: '#ff4444',
    success: '#44ff44',
    
    neonCyan: '#00ffff',
    neonPink: '#ff00ff',
    neonGreen: '#39ff14',
    neonPurple: '#bf00ff',
    neonOrange: '#ff6600',
    
    bgDark: '#0a0a0a',
    bgDarker: '#050505',
    bgGrid: '#1a1a1a',
    
    textPrimary: '#00ff41',
    textSecondary: '#00d4ff',
    textAccent: '#00d4ff'
  }
}

// 白天主题（马卡龙风格）
const lightTheme: ThemeDefinition = {
  name: '马卡龙白天',
  description: '柔和的马卡龙配色，护眼舒适',
  icon: '☀️',
  trigger: {
    condition: 'time',
    description: '自动切换：6:00-18:00',
    timeRange: { start: '06:00', end: '18:00' }
  },
  colors: {
    primary: '#1a365d',
    secondary: '#2c5aa0',
    accent: '#0891b2',
    warning: '#d97706',
    danger: '#dc2626',
    success: '#047857',
    
    neonCyan: '#0891b2',
    neonPink: '#be185d',
    neonGreen: '#047857',
    neonPurple: '#7c3aed',
    neonOrange: '#ea580c',
    
    bgDark: '#f0fdfa',
    bgDarker: '#fefefe',
    bgGrid: '#e6fffa',
    
    textPrimary: '#1a365d',
    textSecondary: '#0891b2',
    textAccent: '#047857'
  }
}

// 海洋主题
const oceanTheme: ThemeDefinition = {
  name: '深海探索',
  description: '深海蓝色系，宁静深邃',
  icon: '🌊',
  trigger: {
    condition: 'manual',
    description: '手动切换：适合专注工作时使用'
  },
  colors: {
    primary: '#0ea5e9',
    secondary: '#0284c7',
    accent: '#06b6d4',
    warning: '#f59e0b',
    danger: '#ef4444',
    success: '#10b981',
    
    neonCyan: '#06b6d4',
    neonPink: '#ec4899',
    neonGreen: '#10b981',
    neonPurple: '#8b5cf6',
    neonOrange: '#f97316',
    
    bgDark: '#0c1219',
    bgDarker: '#020617',
    bgGrid: '#1e293b',
    
    textPrimary: '#0ea5e9',
    textSecondary: '#06b6d4',
    textAccent: '#10b981'
  }
}

// 森林主题
const forestTheme: ThemeDefinition = {
  name: '翠绿森林',
  description: '自然绿色系，清新护眼',
  icon: '🌲',
  trigger: {
    condition: 'manual',
    description: '手动切换：适合长时间阅读'
  },
  colors: {
    primary: '#15803d',
    secondary: '#059669',
    accent: '#0d9488',
    warning: '#eab308',
    danger: '#dc2626',
    success: '#16a34a',
    
    neonCyan: '#0d9488',
    neonPink: '#db2777',
    neonGreen: '#16a34a',
    neonPurple: '#7c3aed',
    neonOrange: '#ea580c',
    
    bgDark: '#0f1f13',
    bgDarker: '#051f08',
    bgGrid: '#1e3a1e',
    
    textPrimary: '#15803d',
    textSecondary: '#0d9488',
    textAccent: '#16a34a'
  }
}

// 夕阳主题
const sunsetTheme: ThemeDefinition = {
  name: '黄昏夕阳',
  description: '温暖橙红色系，温馨舒适',
  icon: '🌅',
  trigger: {
    condition: 'time',
    description: '自动切换：17:00-19:00（黄昏时段）',
    timeRange: { start: '17:00', end: '19:00' }
  },
  colors: {
    primary: '#ea580c',
    secondary: '#dc2626',
    accent: '#f59e0b',
    warning: '#eab308',
    danger: '#dc2626',
    success: '#16a34a',
    
    neonCyan: '#06b6d4',
    neonPink: '#ec4899',
    neonGreen: '#16a34a',
    neonPurple: '#a855f7',
    neonOrange: '#ea580c',
    
    bgDark: '#1f0f0a',
    bgDarker: '#120805',
    bgGrid: '#2d1b14',
    
    textPrimary: '#ea580c',
    textSecondary: '#f59e0b',
    textAccent: '#dc2626'
  }
}

// 极光主题
const auroraTheme: ThemeDefinition = {
  name: '北极极光',
  description: '梦幻紫绿色系，神秘绚烂',
  icon: '🌌',
  trigger: {
    condition: 'manual',
    description: '手动切换：特殊场景和演示'
  },
  colors: {
    primary: '#8b5cf6',
    secondary: '#a855f7',
    accent: '#c084fc',
    warning: '#fbbf24',
    danger: '#f87171',
    success: '#34d399',
    
    neonCyan: '#06d6a0',
    neonPink: '#f72585',
    neonGreen: '#34d399',
    neonPurple: '#8b5cf6',
    neonOrange: '#ff8500',
    
    bgDark: '#1a0f1f',
    bgDarker: '#0f051a',
    bgGrid: '#2d1b3d',
    
    textPrimary: '#8b5cf6',
    textSecondary: '#c084fc',
    textAccent: '#34d399'
  }
}

// 所有主题
const themes = {
  dark: darkTheme,
  light: lightTheme,
  ocean: oceanTheme,
  forest: forestTheme,
  sunset: sunsetTheme,
  aurora: auroraTheme
} as const

export const useThemeStore = defineStore('theme', () => {
  // 当前主题模式
  const currentMode = ref<ThemeMode>('dark')
  
  // 从localStorage恢复主题设置
  const loadThemeFromStorage = () => {
    const savedTheme = localStorage.getItem('nettools-theme')
    if (savedTheme && (savedTheme === 'dark' || savedTheme === 'light')) {
      currentMode.value = savedTheme
    }
  }
  
  // 保存主题设置到localStorage
  const saveThemeToStorage = () => {
    localStorage.setItem('nettools-theme', currentMode.value)
  }
  
  // 当前主题颜色
  const currentTheme = computed<ThemeDefinition>(() => {
    return themes[currentMode.value]
  })
  
  // 应用主题到CSS变量
  const applyThemeToCSS = () => {
    const theme = currentTheme.value
    const root = document.documentElement
    
    // 主要颜色
    root.style.setProperty('--pixel-primary', theme.colors.primary)
    root.style.setProperty('--pixel-secondary', theme.colors.secondary)
    root.style.setProperty('--pixel-accent', theme.colors.accent)
    root.style.setProperty('--pixel-warning', theme.colors.warning)
    root.style.setProperty('--pixel-danger', theme.colors.danger)
    root.style.setProperty('--pixel-success', theme.colors.success)
    
    // 霓虹色系
    root.style.setProperty('--neon-cyan', theme.colors.neonCyan)
    root.style.setProperty('--neon-pink', theme.colors.neonPink)
    root.style.setProperty('--neon-green', theme.colors.neonGreen)
    root.style.setProperty('--neon-purple', theme.colors.neonPurple)
    root.style.setProperty('--neon-orange', theme.colors.neonOrange)
    
    // 背景色
    root.style.setProperty('--bg-dark', theme.colors.bgDark)
    root.style.setProperty('--bg-darker', theme.colors.bgDarker)
    root.style.setProperty('--bg-grid', theme.colors.bgGrid)
    
    // 文字颜色
    root.style.setProperty('--text-primary', theme.colors.textPrimary)
    root.style.setProperty('--text-secondary', theme.colors.textSecondary)
    root.style.setProperty('--text-accent', theme.colors.textAccent)
    
    // 像素边框和阴影
    root.style.setProperty('--pixel-border', `2px solid ${theme.colors.primary}`)
    root.style.setProperty('--pixel-shadow', `0 0 10px ${theme.colors.primary}`)
    
    // 根据主题调整故障效果颜色
    if (currentMode.value === 'light') {
      root.style.setProperty('--glitch-shadow', `2px 2px ${theme.colors.neonPink}, -2px -2px ${theme.colors.neonCyan}`)
    } else {
      root.style.setProperty('--glitch-shadow', `2px 2px ${theme.colors.neonPink}, -2px -2px ${theme.colors.neonCyan}`)
    }
  }
  
  // 切换主题
  const toggleTheme = () => {
    const themeOrder: ThemeMode[] = ['dark', 'light', 'ocean', 'forest', 'sunset', 'aurora']
    const currentIndex = themeOrder.indexOf(currentMode.value)
    const nextIndex = (currentIndex + 1) % themeOrder.length
    currentMode.value = themeOrder[nextIndex]
    
    applyThemeToCSS()
    saveThemeToStorage()
    
    // 发送主题变化事件给桌宠
    window.dispatchEvent(new CustomEvent('theme-change', {
      detail: { theme: currentMode.value }
    }))
  }
  
  // 设置特定主题
  const setTheme = (mode: ThemeMode) => {
    currentMode.value = mode
    applyThemeToCSS()
    saveThemeToStorage()
    
    window.dispatchEvent(new CustomEvent('theme-change', {
      detail: { theme: currentMode.value }
    }))
  }
  
  // 初始化主题
  const initTheme = () => {
    loadThemeFromStorage()
    applyThemeToCSS()
  }
  
  // 获取主题显示名称
  const getThemeName = computed(() => {
    return themes[currentMode.value].name
  })
  
  // 获取主题图标
  const getThemeIcon = computed(() => {
    return themes[currentMode.value].icon
  })
  
  // 获取切换提示文本
  const getToggleHint = computed(() => {
    return themes[currentMode.value].trigger.description
  })
  
  // 获取所有可用主题
  const getAllThemes = computed(() => {
    return Object.entries(themes).map(([key, theme]) => ({
      key: key as ThemeMode,
      ...theme
    }))
  })
  
  // 检查当前时间是否应该切换主题
  const checkTimeBasedTheme = () => {
    const now = new Date()
    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    for (const [key, theme] of Object.entries(themes)) {
      if (theme.trigger.condition === 'time' && theme.trigger.timeRange) {
        const { start, end } = theme.trigger.timeRange
        
        // 处理跨日的时间范围（如18:00-06:00）
        if (start > end) {
          if (currentTime >= start || currentTime < end) {
            return key as ThemeMode
          }
        } else {
          if (currentTime >= start && currentTime < end) {
            return key as ThemeMode
          }
        }
      }
    }
    
    return null
  }
  
  // 自动主题切换（定时检查）
  const autoThemeInterval = ref<number | null>(null)

  const startAutoTheme = () => {
    // 立即检查一次
    const suggestedTheme = checkTimeBasedTheme()
    if (suggestedTheme && suggestedTheme !== currentMode.value) {
      setTheme(suggestedTheme)
    }
    
    // 每分钟检查一次
    autoThemeInterval.value = window.setInterval(() => {
      const suggestedTheme = checkTimeBasedTheme()
      if (suggestedTheme && suggestedTheme !== currentMode.value) {
        setTheme(suggestedTheme)
      }
    }, 60000)
  }

  const stopAutoTheme = () => {
    if (autoThemeInterval.value) {
      clearInterval(autoThemeInterval.value)
      autoThemeInterval.value = null
    }
  }
  
  // 获取主题推荐
  const getThemeRecommendation = computed(() => {
    const suggestedTheme = checkTimeBasedTheme()
    if (suggestedTheme && suggestedTheme !== currentMode.value) {
      return {
        current: themes[currentMode.value].name,
        suggested: themes[suggestedTheme].name,
        reason: themes[suggestedTheme].trigger.description
      }
    }
    return null
  })
  
  return {
    // 状态
    currentMode,
    currentTheme,
    
    // 计算属性
    getThemeName,
    getThemeIcon, 
    getToggleHint,
    getAllThemes,
    getThemeRecommendation,
    
    // 方法
    toggleTheme,
    setTheme,
    initTheme,
    startAutoTheme,
    stopAutoTheme,
    checkTimeBasedTheme
  }
}) 