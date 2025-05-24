/**
---------------------------------------------------------------
File name:                  font.ts
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                字体设置管理store，控制字体类型、大小和舒适度
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现字体管理系统;
----
*/

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 字体类型枚举
export type FontType = 'pixel' | 'standard' | 'hybrid'

// 字体大小枚举  
export type FontSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl'

// 舒适度级别枚举
export type ComfortLevel = 'normal' | 'soft' | 'comfortable'

// 字体配置接口
export interface FontConfig {
  type: FontType
  size: FontSize
  comfortLevel: ComfortLevel
  lineHeight: number
  letterSpacing: number
}

export const useFontStore = defineStore('font', () => {
  // 状态
  const fontConfig = ref<FontConfig>({
    type: 'hybrid',
    size: 'base', 
    comfortLevel: 'normal',
    lineHeight: 1.4,
    letterSpacing: 0
  })

  // 预设配置
  const presets = ref({
    gaming: {
      type: 'pixel' as FontType,
      size: 'sm' as FontSize,
      comfortLevel: 'normal' as ComfortLevel,
      lineHeight: 1.2,
      letterSpacing: 1
    },
    comfortable: {
      type: 'standard' as FontType,
      size: 'base' as FontSize,
      comfortLevel: 'comfortable' as ComfortLevel,
      lineHeight: 1.6,
      letterSpacing: 0.5
    },
    accessibility: {
      type: 'standard' as FontType,
      size: 'lg' as FontSize,
      comfortLevel: 'comfortable' as ComfortLevel,
      lineHeight: 1.8,
      letterSpacing: 1
    }
  })

  // 计算属性
  const currentFontFamily = computed(() => {
    switch (fontConfig.value.type) {
      case 'pixel':
        return 'var(--pixel-font)'
      case 'standard':
        return 'var(--standard-font)'
      case 'hybrid':
        return 'var(--standard-font)' // 混合模式主要使用标准字体
      default:
        return 'var(--standard-font)'
    }
  })

  const currentFontSize = computed(() => {
    return `var(--font-size-${fontConfig.value.size})`
  })

  const cssVars = computed(() => ({
    '--current-font-family': currentFontFamily.value,
    '--current-font-size': currentFontSize.value,
    '--current-line-height': fontConfig.value.lineHeight.toString(),
    '--current-letter-spacing': `${fontConfig.value.letterSpacing}px`
  }))

  // 方法
  
  /**
   * 设置字体类型
   */
  const setFontType = (type: FontType): void => {
    fontConfig.value.type = type
    applyFontSettings()
    saveFontSettings()
  }

  /**
   * 设置字体大小
   */
  const setFontSize = (size: FontSize): void => {
    fontConfig.value.size = size
    applyFontSettings()
    saveFontSettings()
  }

  /**
   * 设置舒适度级别
   */
  const setComfortLevel = (level: ComfortLevel): void => {
    fontConfig.value.comfortLevel = level
    applyComfortLevel()
    saveFontSettings()
  }

  /**
   * 设置行高
   */
  const setLineHeight = (height: number): void => {
    fontConfig.value.lineHeight = Math.max(1, Math.min(3, height))
    applyFontSettings()
    saveFontSettings()
  }

  /**
   * 设置字符间距
   */
  const setLetterSpacing = (spacing: number): void => {
    fontConfig.value.letterSpacing = Math.max(-2, Math.min(5, spacing))
    applyFontSettings()
    saveFontSettings()
  }

  /**
   * 应用预设配置
   */
  const applyPreset = (presetName: keyof typeof presets.value): void => {
    const preset = presets.value[presetName]
    if (preset) {
      fontConfig.value = { ...preset }
      applyFontSettings()
      applyComfortLevel()
      saveFontSettings()
    }
  }

  /**
   * 应用字体设置到DOM
   */
  const applyFontSettings = (): void => {
    const root = document.documentElement
    
    Object.entries(cssVars.value).forEach(([key, value]) => {
      root.style.setProperty(key, value)
    })

    // 应用字体类到body
    const body = document.body
    body.classList.remove('font-pixel', 'font-standard', 'font-hybrid')
    body.classList.add(`font-${fontConfig.value.type}`)
  }

  /**
   * 应用舒适度设置
   */
  const applyComfortLevel = (): void => {
    const body = document.body
    
    // 移除现有舒适度属性
    body.removeAttribute('data-comfort')
    
    // 应用新的舒适度级别
    if (fontConfig.value.comfortLevel !== 'normal') {
      body.setAttribute('data-comfort', fontConfig.value.comfortLevel)
    }
  }

  /**
   * 重置到默认设置
   */
  const resetToDefault = (): void => {
    fontConfig.value = {
      type: 'hybrid',
      size: 'base',
      comfortLevel: 'normal',
      lineHeight: 1.4,
      letterSpacing: 0
    }
    applyFontSettings()
    applyComfortLevel()
    saveFontSettings()
  }

  /**
   * 保存设置到localStorage
   */
  const saveFontSettings = (): void => {
    try {
      localStorage.setItem('fontSettings', JSON.stringify(fontConfig.value))
    } catch (error) {
      console.warn('Failed to save font settings:', error)
    }
  }

  /**
   * 从localStorage加载设置
   */
  const loadFontSettings = (): void => {
    try {
      const saved = localStorage.getItem('fontSettings')
      if (saved) {
        const settings = JSON.parse(saved)
        
        // 验证设置有效性
        if (isValidFontConfig(settings)) {
          fontConfig.value = settings
        } else {
          console.warn('Invalid font settings, using defaults')
          resetToDefault()
        }
      }
    } catch (error) {
      console.warn('Failed to load font settings:', error)
      resetToDefault()
    }
  }

  /**
   * 验证字体配置有效性
   */
  const isValidFontConfig = (config: any): config is FontConfig => {
    const validTypes: FontType[] = ['pixel', 'standard', 'hybrid']
    const validSizes: FontSize[] = ['xs', 'sm', 'base', 'lg', 'xl', '2xl']
    const validComfort: ComfortLevel[] = ['normal', 'soft', 'comfortable']

    return (
      config &&
      typeof config === 'object' &&
      validTypes.includes(config.type) &&
      validSizes.includes(config.size) &&
      validComfort.includes(config.comfortLevel) &&
      typeof config.lineHeight === 'number' &&
      typeof config.letterSpacing === 'number'
    )
  }

  /**
   * 初始化字体系统
   */
  const initFontSystem = (): void => {
    loadFontSettings()
    applyFontSettings()
    applyComfortLevel()
  }

  /**
   * 获取可读性评分（基于当前设置）
   */
  const getReadabilityScore = computed(() => {
    let score = 50 // 基础分

    // 字体类型评分
    switch (fontConfig.value.type) {
      case 'standard':
        score += 25
        break
      case 'hybrid':
        score += 15
        break
      case 'pixel':
        score += 5
        break
    }

    // 字体大小评分
    switch (fontConfig.value.size) {
      case 'lg':
      case 'xl':
        score += 15
        break
      case 'base':
        score += 10
        break
      case 'sm':
        score += 5
        break
      case 'xs':
        score -= 5
        break
      case '2xl':
        score += 10 // 过大也不好
        break
    }

    // 舒适度评分
    switch (fontConfig.value.comfortLevel) {
      case 'comfortable':
        score += 20
        break
      case 'soft':
        score += 10
        break
      case 'normal':
        score += 5
        break
    }

    // 行高评分
    if (fontConfig.value.lineHeight >= 1.4 && fontConfig.value.lineHeight <= 1.8) {
      score += 10
    } else {
      score -= 5
    }

    return Math.max(0, Math.min(100, score))
  })

  return {
    // 状态
    fontConfig,
    presets,
    
    // 计算属性
    currentFontFamily,
    currentFontSize,
    cssVars,
    getReadabilityScore,
    
    // 方法
    setFontType,
    setFontSize,
    setComfortLevel,
    setLineHeight,
    setLetterSpacing,
    applyPreset,
    resetToDefault,
    initFontSystem,
    applyFontSettings,
    applyComfortLevel
  }
}) 