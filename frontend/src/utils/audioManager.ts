/**
---------------------------------------------------------------
File name:                  audioManager.ts
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                音效管理器，为界面交互提供音效支持
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现音效管理系统;
----
*/

// 音效类型枚举
export type SoundType = 
  | 'click'
  | 'hover'
  | 'success'
  | 'error'
  | 'warning'
  | 'notification'
  | 'scan'
  | 'connect'
  | 'disconnect'
  | 'achievement'
  | 'combo'
  | 'beep'
  | 'whoosh'
  | 'ping'

// 音效配置接口
interface SoundConfig {
  volume: number
  pitch: number
  duration: number
  oscillatorType: OscillatorType
  frequency: number
  fadeOut?: boolean
  filterFrequency?: number
}

// 音效预设配置
const SOUND_PRESETS: Record<SoundType, SoundConfig> = {
  click: {
    volume: 0.1,
    pitch: 1,
    duration: 0.1,
    oscillatorType: 'square',
    frequency: 800,
    fadeOut: true
  },
  hover: {
    volume: 0.05,
    pitch: 1.2,
    duration: 0.05,
    oscillatorType: 'sine',
    frequency: 1200,
    fadeOut: true
  },
  success: {
    volume: 0.15,
    pitch: 1,
    duration: 0.3,
    oscillatorType: 'triangle',
    frequency: 880,
    fadeOut: true
  },
  error: {
    volume: 0.2,
    pitch: 0.8,
    duration: 0.4,
    oscillatorType: 'sawtooth',
    frequency: 220,
    fadeOut: true
  },
  warning: {
    volume: 0.12,
    pitch: 1,
    duration: 0.25,
    oscillatorType: 'square',
    frequency: 660,
    fadeOut: true
  },
  notification: {
    volume: 0.1,
    pitch: 1,
    duration: 0.2,
    oscillatorType: 'sine',
    frequency: 1000,
    fadeOut: true
  },
  scan: {
    volume: 0.08,
    pitch: 1,
    duration: 1.5,
    oscillatorType: 'sine',
    frequency: 440,
    fadeOut: true,
    filterFrequency: 2000
  },
  connect: {
    volume: 0.12,
    pitch: 1,
    duration: 0.3,
    oscillatorType: 'triangle',
    frequency: 523,
    fadeOut: true
  },
  disconnect: {
    volume: 0.1,
    pitch: 0.9,
    duration: 0.4,
    oscillatorType: 'sine',
    frequency: 392,
    fadeOut: true
  },
  achievement: {
    volume: 0.2,
    pitch: 1,
    duration: 0.5,
    oscillatorType: 'square',
    frequency: 783,
    fadeOut: true
  },
  combo: {
    volume: 0.15,
    pitch: 1.5,
    duration: 0.2,
    oscillatorType: 'triangle',
    frequency: 1046,
    fadeOut: true
  },
  beep: {
    volume: 0.1,
    pitch: 1,
    duration: 0.1,
    oscillatorType: 'square',
    frequency: 1000,
    fadeOut: false
  },
  whoosh: {
    volume: 0.08,
    pitch: 1,
    duration: 0.4,
    oscillatorType: 'sawtooth',
    frequency: 200,
    fadeOut: true,
    filterFrequency: 500
  },
  ping: {
    volume: 0.06,
    pitch: 1,
    duration: 0.15,
    oscillatorType: 'sine',
    frequency: 2000,
    fadeOut: true
  }
}

// 音效管理器类
export class AudioManager {
  private audioContext: AudioContext | null = null
  private masterVolume: number = 0.5
  private enabled: boolean = true
  private initialized: boolean = false

  /**
   * 初始化音频系统
   */
  async init(): Promise<void> {
    if (this.initialized) return

    try {
      // 创建音频上下文
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      
      // 确保音频上下文已启动
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume()
      }

      this.initialized = true
      console.log('Audio Manager initialized successfully')
    } catch (error) {
      console.warn('Failed to initialize Audio Manager:', error)
      this.enabled = false
    }
  }

  /**
   * 播放音效
   */
  play(soundType: SoundType, options?: Partial<SoundConfig>): void {
    if (!this.enabled || !this.audioContext || !this.initialized) {
      return
    }

    try {
      const config = { ...SOUND_PRESETS[soundType], ...options }
      this.synthesizeSound(config)
    } catch (error) {
      console.warn(`Failed to play sound ${soundType}:`, error)
    }
  }

  /**
   * 播放连续音效序列
   */
  playSequence(sounds: Array<{ type: SoundType; delay: number; options?: Partial<SoundConfig> }>): void {
    sounds.forEach(({ type, delay, options }) => {
      setTimeout(() => this.play(type, options), delay)
    })
  }

  /**
   * 播放组合音效
   */
  playCombo(soundTypes: SoundType[], interval: number = 100): void {
    soundTypes.forEach((type, index) => {
      setTimeout(() => this.play(type), index * interval)
    })
  }

  /**
   * 播放成功序列音效
   */
  playSuccessSequence(): void {
    this.playSequence([
      { type: 'success', delay: 0 },
      { type: 'achievement', delay: 200, options: { pitch: 1.2 } },
      { type: 'combo', delay: 400, options: { pitch: 1.5 } }
    ])
  }

  /**
   * 播放扫描音效
   */
  playScanSound(): void {
    this.play('scan', {
      volume: 0.06,
      duration: 2,
      frequency: 440
    })
  }

  /**
   * 播放连接建立音效
   */
  playConnectionSound(): void {
    this.playSequence([
      { type: 'beep', delay: 0, options: { frequency: 800 } },
      { type: 'beep', delay: 150, options: { frequency: 1000 } },
      { type: 'connect', delay: 300 }
    ])
  }

  /**
   * 播放网络活动音效
   */
  playNetworkActivity(): void {
    this.play('ping', {
      volume: 0.04,
      frequency: 1500 + Math.random() * 500
    })
  }

  /**
   * 生成合成音效
   */
  private synthesizeSound(config: SoundConfig): void {
    if (!this.audioContext) return

    const now = this.audioContext.currentTime
    
    // 创建振荡器
    const oscillator = this.audioContext.createOscillator()
    oscillator.type = config.oscillatorType
    oscillator.frequency.setValueAtTime(config.frequency, now)

    // 创建音量节点
    const gainNode = this.audioContext.createGain()
    const volume = config.volume * this.masterVolume
    
    if (config.fadeOut) {
      gainNode.gain.setValueAtTime(volume, now)
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + config.duration)
    } else {
      gainNode.gain.setValueAtTime(volume, now)
      gainNode.gain.setValueAtTime(0, now + config.duration)
    }

    // 创建滤波器（如果配置了）
    let finalNode: AudioNode = gainNode
    if (config.filterFrequency) {
      const filter = this.audioContext.createBiquadFilter()
      filter.type = 'lowpass'
      filter.frequency.setValueAtTime(config.filterFrequency, now)
      filter.Q.setValueAtTime(5, now)
      
      gainNode.connect(filter)
      finalNode = filter
    }

    // 连接音频图
    oscillator.connect(gainNode)
    finalNode.connect(this.audioContext.destination)

    // 启动和停止振荡器
    oscillator.start(now)
    oscillator.stop(now + config.duration)
  }

  /**
   * 设置主音量
   */
  setMasterVolume(volume: number): void {
    this.masterVolume = Math.max(0, Math.min(1, volume))
    this.saveSettings()
  }

  /**
   * 获取主音量
   */
  getMasterVolume(): number {
    return this.masterVolume
  }

  /**
   * 启用/禁用音效
   */
  setEnabled(enabled: boolean): void {
    this.enabled = enabled
    this.saveSettings()
  }

  /**
   * 检查是否启用音效
   */
  isEnabled(): boolean {
    return this.enabled && this.initialized
  }

  /**
   * 静音/取消静音
   */
  toggleMute(): void {
    this.setEnabled(!this.enabled)
  }

  /**
   * 保存设置到本地存储
   */
  private saveSettings(): void {
    try {
      const settings = {
        masterVolume: this.masterVolume,
        enabled: this.enabled
      }
      localStorage.setItem('audioSettings', JSON.stringify(settings))
    } catch (error) {
      console.warn('Failed to save audio settings:', error)
    }
  }

  /**
   * 从本地存储加载设置
   */
  loadSettings(): void {
    try {
      const saved = localStorage.getItem('audioSettings')
      if (saved) {
        const settings = JSON.parse(saved)
        this.masterVolume = settings.masterVolume ?? 0.5
        this.enabled = settings.enabled ?? true
      }
    } catch (error) {
      console.warn('Failed to load audio settings:', error)
    }
  }

  /**
   * 检查浏览器音频支持
   */
  static isSupported(): boolean {
    return !!(window.AudioContext || (window as any).webkitAudioContext)
  }

  /**
   * 创建自定义音效
   */
  createCustomSound(config: SoundConfig): (options?: Partial<SoundConfig>) => void {
    return (options?: Partial<SoundConfig>) => {
      const finalConfig = { ...config, ...options }
      this.synthesizeSound(finalConfig)
    }
  }

  /**
   * 测试音效
   */
  testSound(): void {
    this.playSequence([
      { type: 'click', delay: 0 },
      { type: 'hover', delay: 200 },
      { type: 'success', delay: 400 },
      { type: 'notification', delay: 800 }
    ])
  }

  /**
   * 清理资源
   */
  dispose(): void {
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close()
    }
    this.audioContext = null
    this.initialized = false
  }
}

// 创建全局音效管理器实例
export const audioManager = new AudioManager()

// 初始化音效管理器
export const initAudioManager = async (): Promise<void> => {
  if (AudioManager.isSupported()) {
    audioManager.loadSettings()
    await audioManager.init()
  } else {
    console.warn('Audio not supported in this browser')
  }
}

// 便捷的音效播放函数
export const playSound = (soundType: SoundType, options?: Partial<SoundConfig>): void => {
  audioManager.play(soundType, options)
}

// 交互音效助手类
export class InteractionSounds {
  /**
   * 为元素添加点击音效
   */
  static addClickSound(element: HTMLElement, soundType: SoundType = 'click'): void {
    element.addEventListener('click', () => {
      playSound(soundType)
    })
  }

  /**
   * 为元素添加悬停音效
   */
  static addHoverSound(element: HTMLElement, soundType: SoundType = 'hover'): void {
    let hoverTimeout: number | null = null
    
    element.addEventListener('mouseenter', () => {
      if (hoverTimeout) {
        clearTimeout(hoverTimeout)
      }
      hoverTimeout = window.setTimeout(() => {
        playSound(soundType)
      }, 100) // 延迟100ms避免过于频繁
    })

    element.addEventListener('mouseleave', () => {
      if (hoverTimeout) {
        clearTimeout(hoverTimeout)
        hoverTimeout = null
      }
    })
  }

  /**
   * 为表单元素添加音效
   */
  static addFormSounds(form: HTMLFormElement): void {
    // 输入框焦点音效
    const inputs = form.querySelectorAll('input, textarea, select')
    inputs.forEach(input => {
      input.addEventListener('focus', () => playSound('hover'))
      input.addEventListener('blur', () => playSound('click', { volume: 0.05 }))
    })

    // 提交音效
    form.addEventListener('submit', (e) => {
      e.preventDefault()
      playSound('success')
    })
  }

  /**
   * 为按钮组添加音效
   */
  static addButtonGroupSounds(container: HTMLElement): void {
    const buttons = container.querySelectorAll('button, .btn')
    buttons.forEach(button => {
      this.addClickSound(button as HTMLElement)
      this.addHoverSound(button as HTMLElement)
    })
  }

  /**
   * 为菜单添加音效
   */
  static addMenuSounds(menu: HTMLElement): void {
    const menuItems = menu.querySelectorAll('.menu-item, .nav-item, li')
    menuItems.forEach((item, index) => {
      this.addClickSound(item as HTMLElement, 'click')
      this.addHoverSound(item as HTMLElement, 'hover')
    })
  }
}

// Vue 3 组合式函数
export const useAudio = () => {
  const playClickSound = () => playSound('click')
  const playHoverSound = () => playSound('hover')
  const playSuccessSound = () => playSound('success')
  const playErrorSound = () => playSound('error')
  const playNotificationSound = () => playSound('notification')

  return {
    playSound,
    playClickSound,
    playHoverSound,
    playSuccessSound,
    playErrorSound,
    playNotificationSound,
    audioManager
  }
}

export default audioManager 