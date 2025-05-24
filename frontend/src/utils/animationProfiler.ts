/**
 * ---------------------------------------------------------------
 * File name:                  animationProfiler.ts
 * Author:                     Ignorant-lu
 * Date created:               2025/05/24
 * Description:                动画性能分析和优化工具
 * ----------------------------------------------------------------
 * 
 * Changed history:            
 *                             2025/05/24: 初始创建，动画性能监控;
 * ----
 */

// 动画性能指标接口
export interface AnimationMetrics {
  name: string
  startTime: number
  endTime?: number
  duration?: number
  frameCount: number
  averageFPS: number
  minFPS: number
  maxFPS: number
  droppedFrames: number
  cpuUsage: number
  memoryUsage: number
  isGPUAccelerated: boolean
}

// 动画配置接口
export interface AnimationConfig {
  name: string
  element: HTMLElement
  duration: number
  easing: string
  properties: string[]
  useGPU: boolean
  priority: 'low' | 'normal' | 'high'
}

// 性能阈值配置
export interface PerformanceThresholds {
  minFPS: number
  maxDroppedFrames: number
  maxCPUUsage: number
  maxMemoryUsage: number
}

// 动画性能分析器类
export class AnimationProfiler {
  private static instance: AnimationProfiler
  private activeAnimations: Map<string, AnimationMetrics> = new Map()
  private performanceObserver?: PerformanceObserver
  private frameCallbacks: Map<string, number> = new Map()
  private thresholds: PerformanceThresholds = {
    minFPS: 30,
    maxDroppedFrames: 5,
    maxCPUUsage: 80,
    maxMemoryUsage: 100 * 1024 * 1024 // 100MB
  }

  private constructor() {
    this.initPerformanceObserver()
  }

  public static getInstance(): AnimationProfiler {
    if (!AnimationProfiler.instance) {
      AnimationProfiler.instance = new AnimationProfiler()
    }
    return AnimationProfiler.instance
  }

  /**
   * 初始化性能观察器
   */
  private initPerformanceObserver(): void {
    if ('PerformanceObserver' in window) {
      this.performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry) => {
          if (entry.entryType === 'measure') {
            this.updateAnimationMetrics(entry.name, entry)
          }
        })
      })

      this.performanceObserver.observe({ 
        entryTypes: ['measure', 'navigation', 'paint'] 
      })
    }
  }

  /**
   * 开始监控动画
   */
  public startProfiling(animationName: string, element: HTMLElement): void {
    const metrics: AnimationMetrics = {
      name: animationName,
      startTime: performance.now(),
      frameCount: 0,
      averageFPS: 0,
      minFPS: Infinity,
      maxFPS: 0,
      droppedFrames: 0,
      cpuUsage: 0,
      memoryUsage: 0,
      isGPUAccelerated: this.isElementGPUAccelerated(element)
    }

    this.activeAnimations.set(animationName, metrics)
    
    // 开始帧率监控
    this.startFrameRateMonitoring(animationName)
    
    // 标记性能测量开始
    performance.mark(`${animationName}-start`)
    
    console.log(`🎬 开始监控动画: ${animationName}`)
  }

  /**
   * 停止监控动画
   */
  public stopProfiling(animationName: string): AnimationMetrics | null {
    const metrics = this.activeAnimations.get(animationName)
    if (!metrics) return null

    metrics.endTime = performance.now()
    metrics.duration = metrics.endTime - metrics.startTime

    // 停止帧率监控
    this.stopFrameRateMonitoring(animationName)

    // 标记性能测量结束
    performance.mark(`${animationName}-end`)
    performance.measure(animationName, `${animationName}-start`, `${animationName}-end`)

    // 计算最终指标
    this.calculateFinalMetrics(metrics)

    // 性能分析
    this.analyzePerformance(metrics)

    this.activeAnimations.delete(animationName)
    
    console.log(`🏁 动画监控完成: ${animationName}`, metrics)
    return metrics
  }

  /**
   * 开始帧率监控
   */
  private startFrameRateMonitoring(animationName: string): void {
    let lastTime = performance.now()
    let frameCount = 0
    const fpsSamples: number[] = []

    const measureFrame = () => {
      const currentTime = performance.now()
      const deltaTime = currentTime - lastTime
      
      if (deltaTime > 0) {
        const fps = 1000 / deltaTime
        fpsSamples.push(fps)
        frameCount++

        const metrics = this.activeAnimations.get(animationName)
        if (metrics) {
          metrics.frameCount = frameCount
          metrics.minFPS = Math.min(metrics.minFPS, fps)
          metrics.maxFPS = Math.max(metrics.maxFPS, fps)
          
          // 检测掉帧（FPS低于阈值）
          if (fps < this.thresholds.minFPS) {
            metrics.droppedFrames++
          }
        }
      }

      lastTime = currentTime

      if (this.activeAnimations.has(animationName)) {
        const frameId = requestAnimationFrame(measureFrame)
        this.frameCallbacks.set(animationName, frameId)
      }
    }

    const frameId = requestAnimationFrame(measureFrame)
    this.frameCallbacks.set(animationName, frameId)
  }

  /**
   * 停止帧率监控
   */
  private stopFrameRateMonitoring(animationName: string): void {
    const frameId = this.frameCallbacks.get(animationName)
    if (frameId) {
      cancelAnimationFrame(frameId)
      this.frameCallbacks.delete(animationName)
    }
  }

  /**
   * 检测元素是否启用GPU加速
   */
  private isElementGPUAccelerated(element: HTMLElement): boolean {
    const style = window.getComputedStyle(element)
    
    // 检查是否有3D变换
    const transform = style.transform
    const willChange = style.willChange
    const backfaceVisibility = style.backfaceVisibility
    
    return (
      transform.includes('matrix3d') ||
      transform.includes('translate3d') ||
      transform.includes('translateZ') ||
      willChange.includes('transform') ||
      backfaceVisibility === 'hidden'
    )
  }

  /**
   * 更新动画指标
   */
  private updateAnimationMetrics(animationName: string, entry: PerformanceEntry): void {
    const metrics = this.activeAnimations.get(animationName)
    if (!metrics) return

    // 更新CPU和内存使用情况（如果可用）
    if ('memory' in performance) {
      const memInfo = (performance as any).memory
      metrics.memoryUsage = memInfo.usedJSHeapSize
    }
  }

  /**
   * 计算最终指标
   */
  private calculateFinalMetrics(metrics: AnimationMetrics): void {
    if (metrics.frameCount > 0 && metrics.duration) {
      metrics.averageFPS = (metrics.frameCount / metrics.duration) * 1000
    }

    // 重置无限值
    if (metrics.minFPS === Infinity) {
      metrics.minFPS = 0
    }
  }

  /**
   * 性能分析和建议
   */
  private analyzePerformance(metrics: AnimationMetrics): void {
    const issues: string[] = []
    const suggestions: string[] = []

    // 检查FPS
    if (metrics.averageFPS < this.thresholds.minFPS) {
      issues.push(`平均FPS过低: ${metrics.averageFPS.toFixed(1)}`)
      suggestions.push('考虑启用GPU加速或简化动画')
    }

    // 检查掉帧
    if (metrics.droppedFrames > this.thresholds.maxDroppedFrames) {
      issues.push(`掉帧过多: ${metrics.droppedFrames}帧`)
      suggestions.push('优化动画复杂度或增加动画时长')
    }

    // 检查GPU加速
    if (!metrics.isGPUAccelerated) {
      suggestions.push('启用GPU加速: 添加transform3d(0,0,0)或will-change: transform')
    }

    // 检查内存使用
    if (metrics.memoryUsage > this.thresholds.maxMemoryUsage) {
      issues.push(`内存使用过高: ${(metrics.memoryUsage / 1024 / 1024).toFixed(1)}MB`)
      suggestions.push('检查内存泄漏或减少动画元素数量')
    }

    if (issues.length > 0) {
      console.warn(`⚠️ 动画性能问题 [${metrics.name}]:`, issues)
      console.info(`💡 优化建议:`, suggestions)
    } else {
      console.log(`✅ 动画性能良好 [${metrics.name}]`)
    }
  }

  /**
   * 获取所有活跃动画的性能报告
   */
  public getPerformanceReport(): AnimationMetrics[] {
    return Array.from(this.activeAnimations.values())
  }

  /**
   * 设置性能阈值
   */
  public setThresholds(thresholds: Partial<PerformanceThresholds>): void {
    this.thresholds = { ...this.thresholds, ...thresholds }
  }

  /**
   * 清理资源
   */
  public cleanup(): void {
    // 停止所有活跃的监控
    for (const animationName of this.activeAnimations.keys()) {
      this.stopFrameRateMonitoring(animationName)
    }
    
    this.activeAnimations.clear()
    this.frameCallbacks.clear()

    // 断开性能观察器
    if (this.performanceObserver) {
      this.performanceObserver.disconnect()
    }
  }
}

// 动画优化工具类
export class AnimationOptimizer {
  /**
   * 为元素启用GPU加速
   */
  public static enableGPUAcceleration(element: HTMLElement): void {
    const style = element.style
    
    // 添加3D变换触发GPU加速
    if (!style.transform.includes('translate3d') && !style.transform.includes('translateZ')) {
      style.transform = style.transform ? 
        `${style.transform} translateZ(0)` : 
        'translateZ(0)'
    }
    
    // 设置will-change属性
    if (!style.willChange.includes('transform')) {
      style.willChange = style.willChange ? 
        `${style.willChange}, transform` : 
        'transform'
    }
    
    // 设置backface-visibility
    style.backfaceVisibility = 'hidden'
  }

  /**
   * 禁用GPU加速（节省资源）
   */
  public static disableGPUAcceleration(element: HTMLElement): void {
    const style = element.style
    
    // 移除3D变换
    style.transform = style.transform
      .replace(/translateZ\(0\)/g, '')
      .replace(/translate3d\([^)]*\)/g, '')
      .trim()
    
    // 清除will-change
    style.willChange = style.willChange
      .replace(/transform/g, '')
      .replace(/,\s*,/g, ',')
      .replace(/^,|,$/g, '')
      .trim()
    
    // 重置backface-visibility
    style.backfaceVisibility = 'visible'
  }

  /**
   * 批量优化动画元素
   */
  public static optimizeAnimationElements(elements: HTMLElement[]): void {
    elements.forEach(element => {
      this.enableGPUAcceleration(element)
      
      // 添加性能优化CSS类
      element.classList.add('animation-optimized')
    })
  }

  /**
   * 创建高性能动画
   */
  public static createOptimizedAnimation(
    element: HTMLElement,
    keyframes: Keyframe[],
    options: KeyframeAnimationOptions
  ): Animation {
    // 启用GPU加速
    this.enableGPUAcceleration(element)
    
    // 创建动画
    const animation = element.animate(keyframes, {
      ...options,
      // 优化选项
      composite: 'replace',
      iterationComposite: 'replace'
    })
    
    // 监控性能
    const profiler = AnimationProfiler.getInstance()
    const animationName = `optimized-${Date.now()}`
    
    profiler.startProfiling(animationName, element)
    
    animation.addEventListener('finish', () => {
      profiler.stopProfiling(animationName)
      // 动画完成后清理GPU加速（可选）
      // this.disableGPUAcceleration(element)
    })
    
    return animation
  }
}

// 导出单例实例
export const animationProfiler = AnimationProfiler.getInstance()

// 导出工具函数
export const optimizeAnimation = AnimationOptimizer.optimizeAnimationElements
export const enableGPU = AnimationOptimizer.enableGPUAcceleration
export const disableGPU = AnimationOptimizer.disableGPUAcceleration 