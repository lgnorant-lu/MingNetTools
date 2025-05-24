/**
 * ---------------------------------------------------------------
 * File name:                  animation.ts
 * Author:                     Ignorant-lu
 * Date created:               2025/05/24
 * Description:                动画舒适度控制和性能管理store
 * ----------------------------------------------------------------
 * 
 * Changed history:            
 *                             2025/05/24: 初始创建，动画舒适度控制;
 * ----
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { animationProfiler, type AnimationMetrics } from '../utils/animationProfiler'

// 动画强度级别
export type AnimationIntensity = 'none' | 'reduced' | 'normal' | 'enhanced'

// 动画类型
export type AnimationType = 
  | 'transition' 
  | 'transform' 
  | 'opacity' 
  | 'scale' 
  | 'rotate' 
  | 'translate' 
  | 'particle' 
  | 'glow' 
  | 'glitch'

// 动画配置接口
export interface AnimationSettings {
  intensity: AnimationIntensity
  respectMotionPreference: boolean
  enableGPUAcceleration: boolean
  maxConcurrentAnimations: number
  performanceMode: boolean
  customDurations: Record<AnimationType, number>
  enabledTypes: Record<AnimationType, boolean>
}

// 性能统计接口
export interface PerformanceStats {
  averageFPS: number
  totalAnimations: number
  droppedFrames: number
  memoryUsage: number
  gpuAcceleratedCount: number
}

export const useAnimationStore = defineStore('animation', () => {
  // 基础设置
  const settings = ref<AnimationSettings>({
    intensity: 'normal',
    respectMotionPreference: true,
    enableGPUAcceleration: true,
    maxConcurrentAnimations: 10,
    performanceMode: false,
    customDurations: {
      transition: 300,
      transform: 250,
      opacity: 200,
      scale: 300,
      rotate: 400,
      translate: 250,
      particle: 1000,
      glow: 500,
      glitch: 150
    },
    enabledTypes: {
      transition: true,
      transform: true,
      opacity: true,
      scale: true,
      rotate: true,
      translate: true,
      particle: true,
      glow: true,
      glitch: true
    }
  })

  // 性能统计
  const performanceStats = ref<PerformanceStats>({
    averageFPS: 60,
    totalAnimations: 0,
    droppedFrames: 0,
    memoryUsage: 0,
    gpuAcceleratedCount: 0
  })

  // 活跃动画计数
  const activeAnimationCount = ref(0)

  // 用户偏好检测
  const prefersReducedMotion = ref(false)

  // 计算属性

  /**
   * 获取当前有效的动画强度
   */
  const effectiveIntensity = computed(() => {
    if (settings.value.respectMotionPreference && prefersReducedMotion.value) {
      return 'reduced'
    }
    return settings.value.intensity
  })

  /**
   * 检查是否应该禁用动画
   */
  const shouldDisableAnimations = computed(() => {
    return effectiveIntensity.value === 'none' || 
           (settings.value.performanceMode && performanceStats.value.averageFPS < 30)
  })

  /**
   * 获取动画持续时间倍数
   */
  const durationMultiplier = computed(() => {
    switch (effectiveIntensity.value) {
      case 'none': return 0
      case 'reduced': return 0.5
      case 'normal': return 1
      case 'enhanced': return 1.5
      default: return 1
    }
  })

  /**
   * 检查是否可以启动新动画
   */
  const canStartNewAnimation = computed(() => {
    return activeAnimationCount.value < settings.value.maxConcurrentAnimations &&
           !shouldDisableAnimations.value
  })

  // 方法

  /**
   * 设置动画强度
   */
  const setIntensity = (intensity: AnimationIntensity): void => {
    settings.value.intensity = intensity
    applyGlobalAnimationSettings()
    saveSettings()
  }

  /**
   * 切换动画类型启用状态
   */
  const toggleAnimationType = (type: AnimationType, enabled: boolean): void => {
    settings.value.enabledTypes[type] = enabled
    applyGlobalAnimationSettings()
    saveSettings()
  }

  /**
   * 设置自定义动画持续时间
   */
  const setCustomDuration = (type: AnimationType, duration: number): void => {
    settings.value.customDurations[type] = duration
    saveSettings()
  }

  /**
   * 获取动画持续时间
   */
  const getAnimationDuration = (type: AnimationType): number => {
    if (shouldDisableAnimations.value) return 0
    
    const baseDuration = settings.value.customDurations[type]
    return Math.round(baseDuration * durationMultiplier.value)
  }

  /**
   * 检查动画类型是否启用
   */
  const isAnimationTypeEnabled = (type: AnimationType): boolean => {
    return settings.value.enabledTypes[type] && !shouldDisableAnimations.value
  }

  /**
   * 应用全局动画设置到CSS
   */
  const applyGlobalAnimationSettings = (): void => {
    const root = document.documentElement
    
    // 设置动画持续时间变量
    Object.entries(settings.value.customDurations).forEach(([type, duration]) => {
      const adjustedDuration = Math.round(duration * durationMultiplier.value)
      root.style.setProperty(`--animation-duration-${type}`, `${adjustedDuration}ms`)
    })

    // 设置动画强度类
    root.classList.remove('animation-none', 'animation-reduced', 'animation-normal', 'animation-enhanced')
    root.classList.add(`animation-${effectiveIntensity.value}`)

    // 设置GPU加速
    if (settings.value.enableGPUAcceleration) {
      root.classList.add('gpu-acceleration-enabled')
    } else {
      root.classList.remove('gpu-acceleration-enabled')
    }

    // 设置性能模式
    if (settings.value.performanceMode) {
      root.classList.add('performance-mode')
    } else {
      root.classList.remove('performance-mode')
    }
  }

  /**
   * 检测用户动画偏好
   */
  const detectMotionPreference = (): void => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      prefersReducedMotion.value = mediaQuery.matches
      
      mediaQuery.addEventListener('change', (e) => {
        prefersReducedMotion.value = e.matches
        applyGlobalAnimationSettings()
      })
    }
  }

  /**
   * 开始动画监控
   */
  const startAnimationMonitoring = (name: string, element: HTMLElement): void => {
    if (!canStartNewAnimation.value) {
      console.warn(`动画被限制: ${name} (活跃动画: ${activeAnimationCount.value})`)
      return
    }

    activeAnimationCount.value++
    animationProfiler.startProfiling(name, element)
    
    // 更新统计
    performanceStats.value.totalAnimations++
  }

  /**
   * 停止动画监控
   */
  const stopAnimationMonitoring = (name: string): AnimationMetrics | null => {
    activeAnimationCount.value = Math.max(0, activeAnimationCount.value - 1)
    const metrics = animationProfiler.stopProfiling(name)
    
    if (metrics) {
      updatePerformanceStats(metrics)
    }
    
    return metrics
  }

  /**
   * 更新性能统计
   */
  const updatePerformanceStats = (metrics: AnimationMetrics): void => {
    // 更新平均FPS（简单移动平均）
    const alpha = 0.1
    performanceStats.value.averageFPS = 
      performanceStats.value.averageFPS * (1 - alpha) + metrics.averageFPS * alpha

    // 累计掉帧数
    performanceStats.value.droppedFrames += metrics.droppedFrames

    // 更新内存使用
    performanceStats.value.memoryUsage = metrics.memoryUsage

    // 统计GPU加速动画
    if (metrics.isGPUAccelerated) {
      performanceStats.value.gpuAcceleratedCount++
    }

    // 自动性能调整
    if (settings.value.performanceMode && performanceStats.value.averageFPS < 30) {
      autoOptimizePerformance()
    }
  }

  /**
   * 自动性能优化
   */
  const autoOptimizePerformance = (): void => {
    console.warn('🔧 检测到性能问题，自动优化动画设置')
    
    // 降低动画强度
    if (settings.value.intensity === 'enhanced') {
      settings.value.intensity = 'normal'
    } else if (settings.value.intensity === 'normal') {
      settings.value.intensity = 'reduced'
    }

    // 禁用复杂动画
    settings.value.enabledTypes.particle = false
    settings.value.enabledTypes.glitch = false

    // 减少并发动画数量
    settings.value.maxConcurrentAnimations = Math.max(3, settings.value.maxConcurrentAnimations - 2)

    applyGlobalAnimationSettings()
    saveSettings()
  }

  /**
   * 重置性能统计
   */
  const resetPerformanceStats = (): void => {
    performanceStats.value = {
      averageFPS: 60,
      totalAnimations: 0,
      droppedFrames: 0,
      memoryUsage: 0,
      gpuAcceleratedCount: 0
    }
  }

  /**
   * 获取性能报告
   */
  const getPerformanceReport = () => {
    return {
      ...performanceStats.value,
      activeAnimations: activeAnimationCount.value,
      settings: { ...settings.value },
      recommendations: generatePerformanceRecommendations()
    }
  }

  /**
   * 生成性能建议
   */
  const generatePerformanceRecommendations = (): string[] => {
    const recommendations: string[] = []
    
    if (performanceStats.value.averageFPS < 30) {
      recommendations.push('考虑降低动画强度或启用性能模式')
    }
    
    if (performanceStats.value.droppedFrames > 50) {
      recommendations.push('检测到大量掉帧，建议禁用复杂动画')
    }
    
    if (performanceStats.value.gpuAcceleratedCount < performanceStats.value.totalAnimations * 0.5) {
      recommendations.push('建议启用GPU加速以提升性能')
    }
    
    if (activeAnimationCount.value >= settings.value.maxConcurrentAnimations) {
      recommendations.push('并发动画过多，考虑增加限制或优化动画队列')
    }
    
    return recommendations
  }

  /**
   * 保存设置到localStorage
   */
  const saveSettings = (): void => {
    try {
      localStorage.setItem('animation-settings', JSON.stringify(settings.value))
    } catch (error) {
      console.warn('保存动画设置失败:', error)
    }
  }

  /**
   * 从localStorage加载设置
   */
  const loadSettings = (): void => {
    try {
      const saved = localStorage.getItem('animation-settings')
      if (saved) {
        const parsed = JSON.parse(saved)
        settings.value = { ...settings.value, ...parsed }
      }
    } catch (error) {
      console.warn('加载动画设置失败:', error)
    }
  }

  /**
   * 重置设置为默认值
   */
  const resetSettings = (): void => {
    settings.value = {
      intensity: 'normal',
      respectMotionPreference: true,
      enableGPUAcceleration: true,
      maxConcurrentAnimations: 10,
      performanceMode: false,
      customDurations: {
        transition: 300,
        transform: 250,
        opacity: 200,
        scale: 300,
        rotate: 400,
        translate: 250,
        particle: 1000,
        glow: 500,
        glitch: 150
      },
      enabledTypes: {
        transition: true,
        transform: true,
        opacity: true,
        scale: true,
        rotate: true,
        translate: true,
        particle: true,
        glow: true,
        glitch: true
      }
    }
    
    applyGlobalAnimationSettings()
    saveSettings()
  }

  /**
   * 初始化动画系统
   */
  const initAnimationSystem = (): void => {
    loadSettings()
    detectMotionPreference()
    applyGlobalAnimationSettings()
    
    console.log('🎬 动画系统初始化完成')
  }

  // 监听设置变化
  watch(
    () => settings.value,
    () => {
      applyGlobalAnimationSettings()
    },
    { deep: true }
  )

  return {
    // 状态
    settings,
    performanceStats,
    activeAnimationCount,
    prefersReducedMotion,
    
    // 计算属性
    effectiveIntensity,
    shouldDisableAnimations,
    durationMultiplier,
    canStartNewAnimation,
    
    // 方法
    setIntensity,
    toggleAnimationType,
    setCustomDuration,
    getAnimationDuration,
    isAnimationTypeEnabled,
    startAnimationMonitoring,
    stopAnimationMonitoring,
    resetPerformanceStats,
    getPerformanceReport,
    resetSettings,
    initAnimationSystem
  }
}) 