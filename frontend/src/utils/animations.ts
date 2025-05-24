/**
---------------------------------------------------------------
File name:                  animations.ts
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                像素风格动画工具类，封装anime.js实现游戏化交互效果
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，集成anime.js动画库;
----
*/

// 由于依赖问题，我们先用原生CSS动画和Web API实现
// import anime from 'animejs'

// 动画配置类型
export interface AnimationConfig {
  duration?: number
  delay?: number
  easing?: string
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse'
  loop?: boolean | number
  autoplay?: boolean
}

// 像素风格动画类
export class PixelAnimations {
  // 默认配置
  private static defaultConfig: AnimationConfig = {
    duration: 300,
    delay: 0,
    easing: 'ease-out',
    direction: 'normal',
    loop: false,
    autoplay: true
  }

  /**
   * 像素按钮点击动画
   * @param element 目标元素
   * @param config 动画配置
   */
  static pixelButtonClick(element: HTMLElement, config?: AnimationConfig): void {
    const finalConfig = { ...this.defaultConfig, ...config }
    
    // 添加点击效果类
    element.classList.add('pixel-btn-clicked')
    
    // 创建粒子爆炸效果
    this.createParticleExplosion(element, 6)
    
    // 按钮缩放动画
    element.style.transform = 'scale(0.95)'
    element.style.transition = `transform ${finalConfig.duration}ms ${finalConfig.easing}`
    
    setTimeout(() => {
      element.style.transform = 'scale(1)'
      element.classList.remove('pixel-btn-clicked')
    }, finalConfig.duration)
  }

  /**
   * 创建粒子爆炸效果
   * @param element 触发元素
   * @param particleCount 粒子数量
   */
  static createParticleExplosion(element: HTMLElement, particleCount: number = 8): void {
    const rect = element.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2

    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div')
      particle.className = 'animation-particle'
      
      // 粒子样式
      Object.assign(particle.style, {
        position: 'fixed',
        left: centerX + 'px',
        top: centerY + 'px',
        width: '4px',
        height: '4px',
        background: 'var(--pixel-primary)',
        borderRadius: '50%',
        pointerEvents: 'none',
        zIndex: '9999',
        transition: 'all 0.8s ease-out'
      })

      document.body.appendChild(particle)

      // 计算粒子运动方向
      const angle = (i * 360 / particleCount) * Math.PI / 180
      const distance = 50 + Math.random() * 30
      const endX = centerX + Math.cos(angle) * distance
      const endY = centerY + Math.sin(angle) * distance

      // 延迟启动动画
      setTimeout(() => {
        Object.assign(particle.style, {
          left: endX + 'px',
          top: endY + 'px',
          opacity: '0',
          transform: 'scale(0)'
        })
      }, 10)

      // 清理粒子
      setTimeout(() => {
        document.body.removeChild(particle)
      }, 800)
    }
  }

  /**
   * 像素文字打字机效果
   * @param element 目标元素
   * @param text 要显示的文字
   * @param config 动画配置
   */
  static pixelTypewriter(
    element: HTMLElement, 
    text: string, 
    config?: AnimationConfig
  ): Promise<void> {
    return new Promise((resolve) => {
      const finalConfig = { ...this.defaultConfig, duration: 50, ...config }
      element.textContent = ''
      
      let currentIndex = 0
      const typeInterval = setInterval(() => {
        if (currentIndex < text.length) {
          element.textContent += text[currentIndex]
          currentIndex++
          
          // 添加打字音效类
          element.classList.add('typing-effect')
          setTimeout(() => element.classList.remove('typing-effect'), 100)
        } else {
          clearInterval(typeInterval)
          resolve()
        }
      }, finalConfig.duration)
    })
  }

  /**
   * 像素卡片翻转动画
   * @param element 目标元素
   * @param config 动画配置
   */
  static pixelCardFlip(element: HTMLElement, config?: AnimationConfig): void {
    const finalConfig = { ...this.defaultConfig, duration: 600, ...config }
    
    element.style.transition = `transform ${finalConfig.duration}ms ease-in-out`
    element.style.transform = 'rotateY(180deg)'
    
    setTimeout(() => {
      element.style.transform = 'rotateY(0deg)'
    }, finalConfig.duration / 2)
  }

  /**
   * 数据流动画效果
   * @param element 目标元素
   * @param config 动画配置
   */
  static dataFlowEffect(element: HTMLElement, config?: AnimationConfig): void {
    const finalConfig = { ...this.defaultConfig, duration: 2000, loop: true, ...config }
    
    // 创建数据流元素
    const dataFlow = document.createElement('div')
    dataFlow.className = 'data-flow-animation'
    dataFlow.textContent = '01010101'
    
    Object.assign(dataFlow.style, {
      position: 'absolute',
      top: '0',
      left: '-100%',
      width: '100%',
      height: '100%',
      color: 'var(--neon-green)',
      fontSize: '8px',
      opacity: '0.3',
      pointerEvents: 'none',
      fontFamily: 'var(--pixel-font)',
      display: 'flex',
      alignItems: 'center',
      overflow: 'hidden'
    })

    element.style.position = 'relative'
    element.appendChild(dataFlow)

    // 启动动画
    const animate = () => {
      dataFlow.style.transition = `left ${finalConfig.duration}ms linear`
      dataFlow.style.left = '100%'
      
      setTimeout(() => {
        dataFlow.style.transition = 'none'
        dataFlow.style.left = '-100%'
        
        if (finalConfig.loop) {
          setTimeout(animate, 100)
        }
      }, finalConfig.duration)
    }

    animate()
  }

  /**
   * 霓虹灯发光动画
   * @param element 目标元素
   * @param color 发光颜色
   * @param config 动画配置
   */
  static neonGlowPulse(
    element: HTMLElement, 
    color: string = 'var(--pixel-primary)', 
    config?: AnimationConfig
  ): void {
    const finalConfig = { ...this.defaultConfig, duration: 2000, loop: true, ...config }
    
    element.style.animation = `neonPulse ${finalConfig.duration}ms ease-in-out infinite`
    element.style.setProperty('--glow-color', color)
    
    // 添加CSS动画定义
    if (!document.querySelector('#neon-pulse-style')) {
      const style = document.createElement('style')
      style.id = 'neon-pulse-style'
      style.textContent = `
        @keyframes neonPulse {
          0%, 100% { 
            box-shadow: 0 0 10px var(--glow-color); 
            filter: brightness(1);
          }
          50% { 
            box-shadow: 0 0 25px var(--glow-color), 0 0 35px var(--glow-color); 
            filter: brightness(1.2);
          }
        }
      `
      document.head.appendChild(style)
    }
  }

  /**
   * 页面切换滑动动画
   * @param fromElement 离开的元素
   * @param toElement 进入的元素
   * @param direction 方向：'left' | 'right' | 'up' | 'down'
   * @param config 动画配置
   */
  static pageSlideTransition(
    fromElement: HTMLElement,
    toElement: HTMLElement,
    direction: 'left' | 'right' | 'up' | 'down' = 'left',
    config?: AnimationConfig
  ): Promise<void> {
    return new Promise((resolve) => {
      const finalConfig = { ...this.defaultConfig, duration: 500, ...config }
      
      // 设置初始位置
      const transforms = {
        left: { from: 'translateX(0)', to: 'translateX(-100%)', enter: 'translateX(100%)' },
        right: { from: 'translateX(0)', to: 'translateX(100%)', enter: 'translateX(-100%)' },
        up: { from: 'translateY(0)', to: 'translateY(-100%)', enter: 'translateY(100%)' },
        down: { from: 'translateY(0)', to: 'translateY(100%)', enter: 'translateY(-100%)' }
      }
      
      const transform = transforms[direction]
      
      // 设置过渡
      fromElement.style.transition = `transform ${finalConfig.duration}ms ease-in-out`
      toElement.style.transition = `transform ${finalConfig.duration}ms ease-in-out`
      
      // 设置进入元素初始位置
      toElement.style.transform = transform.enter
      toElement.style.display = 'block'
      
      // 启动动画
      setTimeout(() => {
        fromElement.style.transform = transform.to
        toElement.style.transform = 'translateX(0) translateY(0)'
      }, 10)
      
      // 完成回调
      setTimeout(() => {
        fromElement.style.display = 'none'
        fromElement.style.transform = transform.from
        resolve()
      }, finalConfig.duration)
    })
  }

  /**
   * 状态变化动画（成功/错误/警告）
   * @param element 目标元素
   * @param status 状态类型
   * @param config 动画配置
   */
  static statusChangeAnimation(
    element: HTMLElement,
    status: 'success' | 'error' | 'warning' | 'info',
    config?: AnimationConfig
  ): void {
    const finalConfig = { ...this.defaultConfig, duration: 600, ...config }
    
    // 状态颜色映射
    const statusColors = {
      success: 'var(--pixel-success)',
      error: 'var(--pixel-danger)',
      warning: 'var(--pixel-warning)',
      info: 'var(--pixel-accent)'
    }
    
    // 状态动画类型
    const statusAnimations = {
      success: 'success-flash',
      error: 'error-shake', 
      warning: 'warning-bounce',
      info: 'info-glow'
    }
    
    // 添加动画类
    element.classList.add(statusAnimations[status])
    element.style.setProperty('--status-color', statusColors[status])
    
    // 移除动画类
    setTimeout(() => {
      element.classList.remove(statusAnimations[status])
    }, finalConfig.duration)
  }

  /**
   * 加载动画
   * @param element 目标元素
   * @param type 加载类型
   * @param config 动画配置
   */
  static loadingAnimation(
    element: HTMLElement,
    type: 'dots' | 'spinner' | 'wave' | 'matrix' = 'dots',
    config?: AnimationConfig
  ): void {
    const finalConfig = { ...this.defaultConfig, duration: 1500, loop: true, ...config }
    
    element.classList.add(`loading-${type}`)
    
    if (type === 'matrix') {
      // 特殊的矩阵雨效果
      this.createMatrixRain(element, finalConfig)
    }
  }

  /**
   * 创建矩阵雨效果
   * @param element 目标元素
   * @param config 动画配置
   */
  private static createMatrixRain(element: HTMLElement, config: AnimationConfig): void {
    const matrix = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    if (!ctx) return
    
    canvas.width = element.offsetWidth
    canvas.height = element.offsetHeight
    canvas.style.position = 'absolute'
    canvas.style.top = '0'
    canvas.style.left = '0'
    canvas.style.pointerEvents = 'none'
    
    element.style.position = 'relative'
    element.appendChild(canvas)
    
    const drops: number[] = []
    const columns = canvas.width / 10
    
    for (let i = 0; i < columns; i++) {
      drops[i] = 1
    }
    
    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      ctx.fillStyle = '#00ff41'
      ctx.font = '10px monospace'
      
      for (let i = 0; i < drops.length; i++) {
        const text = matrix[Math.floor(Math.random() * matrix.length)]
        ctx.fillText(text, i * 10, drops[i] * 10)
        
        if (drops[i] * 10 > canvas.height && Math.random() > 0.975) {
          drops[i] = 0
        }
        drops[i]++
      }
    }
    
    const interval = setInterval(draw, 33)
    
    // 存储定时器以便清理
    element.dataset.matrixInterval = interval.toString()
  }

  /**
   * 停止加载动画
   * @param element 目标元素
   */
  static stopLoadingAnimation(element: HTMLElement): void {
    element.classList.remove('loading-dots', 'loading-spinner', 'loading-wave', 'loading-matrix')
    
    // 清理矩阵雨
    const interval = element.dataset.matrixInterval
    if (interval) {
      clearInterval(parseInt(interval))
      const canvas = element.querySelector('canvas')
      if (canvas) {
        element.removeChild(canvas)
      }
    }
  }

  /**
   * 游戏化点击反馈
   * @param element 目标元素
   * @param config 动画配置
   */
  static gamingClickFeedback(element: HTMLElement, config?: AnimationConfig): void {
    const finalConfig = { ...this.defaultConfig, duration: 200, ...config }
    
    // 创建点击波纹效果
    const ripple = document.createElement('div')
    ripple.className = 'click-ripple'
    
    Object.assign(ripple.style, {
      position: 'absolute',
      borderRadius: '50%',
      background: 'rgba(0, 255, 65, 0.6)',
      transform: 'scale(0)',
      animation: `rippleEffect ${finalConfig.duration * 2}ms ease-out`,
      pointerEvents: 'none'
    })
    
    element.style.position = 'relative'
    element.appendChild(ripple)
    
    // 添加CSS动画
    if (!document.querySelector('#ripple-effect-style')) {
      const style = document.createElement('style')
      style.id = 'ripple-effect-style'
      style.textContent = `
        @keyframes rippleEffect {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }
      `
      document.head.appendChild(style)
    }
    
    // 清理波纹
    setTimeout(() => {
      if (element.contains(ripple)) {
        element.removeChild(ripple)
      }
    }, finalConfig.duration * 2)
  }
}

// 导出默认实例
export const pixelAnimations = PixelAnimations

// 工具函数：为元素添加游戏化交互
export function addGamingInteractions(element: HTMLElement): void {
  element.addEventListener('click', () => {
    PixelAnimations.gamingClickFeedback(element)
    PixelAnimations.pixelButtonClick(element)
  })
  
  element.addEventListener('mouseenter', () => {
    PixelAnimations.neonGlowPulse(element)
  })
  
  element.addEventListener('mouseleave', () => {
    element.style.animation = ''
  })
} 