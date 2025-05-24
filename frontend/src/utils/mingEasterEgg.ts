/**
 * ---------------------------------------------------------------
 * File name:                  mingEasterEgg.ts
 * Author:                     Ming (鹿鸣)
 * Date created:               2025/05/24
 * Description:                Ming的神秘彩蛋系统 - 分布式随机触发引擎
 * ----------------------------------------------------------------
 * 
 * Changed history:            
 *                             2025/05/24: 初始创建，Ming的秘密彩蛋系统;
 * ----
 */

// 动画类型枚举
export enum MingAnimationType {
  ESCAPE = 'escape',      // 逃脱冒险版
  RETURN = 'return',      // 温馨回家版  
  DIRECT = 'direct'       // 害羞直降版
}

// 触发点配置
export interface TriggerConfig {
  id: string
  element: string
  action: string
  count: number
  probability: number
  cooldown?: number // 冷却时间(ms)
}

// 随机事件配置
export interface RandomEventConfig {
  doubleTrigger: number     // 连续播放概率
  withBadge: number        // 显示徽章概率
  withMessage: number      // 特殊消息概率
  withSound: number        // 音效概率
}

// 时间特殊事件
export interface TimeBasedEvent {
  time: string
  message: string
  effect?: 'guaranteed' | 'double_chance' | 'rare_only'
  animation?: MingAnimationType
}

// 成就触发记录
export interface MingAchievement {
  id: string
  name: string
  description: string
  icon: string
  unlocked: boolean
  unlockedAt?: Date
  hidden: boolean
}

/**
 * Ming彩蛋随机事件引擎
 */
export class MingEasterEggEngine {
  private static instance: MingEasterEggEngine
  private triggerCounts = new Map<string, number>()
  private lastTriggerTime = new Map<string, number>()
  private seenAnimations = new Set<MingAnimationType>()
  private achievements = new Map<string, MingAchievement>()
  private totalTriggers = 0

  // 触发点配置
  private readonly triggers: TriggerConfig[] = [
    {
      id: 'pixelPet',
      element: '.pixel-pet',
      action: 'click',
      count: 5,
      probability: 0.3,
      cooldown: 10000
    },
    {
      id: 'settingsAbout',
      element: '.settings-about-section',
      action: 'click',
      count: 3,
      probability: 0.25,
      cooldown: 15000
    },
    {
      id: 'dashboardCard',
      element: '.dashboard-system-info',
      action: 'dblclick',
      count: 1,
      probability: 0.2,
      cooldown: 20000
    },
    {
      id: 'audioTest',
      element: '.audio-test-button',
      action: 'click',
      count: 7,
      probability: 0.15,
      cooldown: 30000
    }
  ]

  // 动画权重配置
  private readonly animationWeights = {
    [MingAnimationType.ESCAPE]: 0.4,
    [MingAnimationType.RETURN]: 0.35,
    [MingAnimationType.DIRECT]: 0.25
  }

  // 随机事件配置
  private readonly randomEvents: RandomEventConfig = {
    doubleTrigger: 0.1,
    withBadge: 0.05,
    withMessage: 0.15,
    withSound: 0.8
  }

  // 时间特殊事件
  private readonly timeEvents: TimeBasedEvent[] = [
    {
      time: '17:19',
      message: '时间魔法！Ming在17:19向你问好！',
      effect: 'double_chance'
    },
    {
      time: '23:33',
      message: '深夜惊喜！小猫咪在月光下向你招手～',
      animation: MingAnimationType.ESCAPE
    },
    {
      time: '00:00',
      message: '新的一天开始了！Ming的祝福伴随着你！',
      effect: 'guaranteed'
    }
  ]

  // 成就定义
  private readonly achievementDefinitions: MingAchievement[] = [
    {
      id: 'first_discovery',
      name: '神秘礼物发现者',
      description: '发现了Ming留下的神秘礼盒',
      icon: '🎁',
      unlocked: false,
      hidden: false
    },
    {
      id: 'curious_explorer',
      name: '好奇心重',
      description: '多次打开了神秘礼盒...',
      icon: '👀',
      unlocked: false,
      hidden: false
    },
    {
      id: 'animation_collector',
      name: '动画收集家',
      description: '见证了所有三种小猫咪的表演',
      icon: '🐱',
      unlocked: false,
      hidden: false
    },
    {
      id: 'ming_best_friend',
      name: 'Ming的挚友',
      description: '你已经是Ming最信任的朋友了！',
      icon: '💎',
      unlocked: false,
      hidden: true
    },
    {
      id: 'time_wizard',
      name: '时间魔法师',
      description: '在特殊时刻发现了时间的秘密',
      icon: '⏰',
      unlocked: false,
      hidden: true
    }
  ]

  private constructor() {
    this.initializeAchievements()
    this.loadProgress()
    this.setupEventListeners()
  }

  public static getInstance(): MingEasterEggEngine {
    if (!MingEasterEggEngine.instance) {
      MingEasterEggEngine.instance = new MingEasterEggEngine()
    }
    return MingEasterEggEngine.instance
  }

  /**
   * 初始化成就系统
   */
  private initializeAchievements(): void {
    this.achievementDefinitions.forEach(achievement => {
      this.achievements.set(achievement.id, { ...achievement })
    })
  }

  /**
   * 加载进度数据
   */
  private loadProgress(): void {
    try {
      const saved = localStorage.getItem('ming-easter-egg-progress')
      if (saved) {
        const data = JSON.parse(saved)
        this.totalTriggers = data.totalTriggers || 0
        this.triggerCounts = new Map(data.triggerCounts || [])
        this.seenAnimations = new Set(data.seenAnimations || [])
        
        // 恢复成就状态
        if (data.achievements) {
          data.achievements.forEach((achievement: any) => {
            this.achievements.set(achievement.id, achievement)
          })
        }
      }
    } catch (error) {
      console.warn('Failed to load Ming easter egg progress:', error)
    }
  }

  /**
   * 保存进度数据
   */
  private saveProgress(): void {
    try {
      const data = {
        totalTriggers: this.totalTriggers,
        triggerCounts: Array.from(this.triggerCounts.entries()),
        seenAnimations: Array.from(this.seenAnimations),
        achievements: Array.from(this.achievements.values())
      }
      localStorage.setItem('ming-easter-egg-progress', JSON.stringify(data))
    } catch (error) {
      console.warn('Failed to save Ming easter egg progress:', error)
    }
  }

  /**
   * 设置事件监听器
   */
  private setupEventListeners(): void {
    // 监听控制台命令
    this.setupConsoleListener()
    
    // 监听键盘序列
    this.setupKonamiListener()
    
    // 监听开发者工具
    this.setupDevToolsListener()
  }

  /**
   * 检查是否可以触发
   */
  public canTrigger(triggerId: string): boolean {
    const config = this.triggers.find(t => t.id === triggerId)
    if (!config) return false

    const now = Date.now()
    const lastTime = this.lastTriggerTime.get(triggerId) || 0
    
    // 检查冷却时间
    if (config.cooldown && now - lastTime < config.cooldown) {
      return false
    }

    return true
  }

  /**
   * 尝试触发彩蛋
   */
  public async attemptTrigger(triggerId: string): Promise<boolean> {
    if (!this.canTrigger(triggerId)) return false

    const config = this.triggers.find(t => t.id === triggerId)
    if (!config) return false

    // 增加计数
    const currentCount = this.triggerCounts.get(triggerId) || 0
    this.triggerCounts.set(triggerId, currentCount + 1)

    // 检查是否达到触发条件
    if ((currentCount + 1) % config.count !== 0) {
      return false
    }

    // 检查概率
    const enhancedProbability = this.calculateEnhancedProbability(config.probability)
    if (Math.random() > enhancedProbability) {
      return false
    }

    // 触发成功
    this.lastTriggerTime.set(triggerId, Date.now())
    this.totalTriggers++
    
    // 播放彩蛋
    await this.playEasterEgg()
    
    // 检查成就
    this.checkAchievements()
    
    // 保存进度
    this.saveProgress()
    
    return true
  }

  /**
   * 计算增强概率（基于时间和特殊事件）
   */
  private calculateEnhancedProbability(baseProbability: number): number {
    let probability = baseProbability

    // 时间加成
    const now = new Date()
    const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    const timeEvent = this.timeEvents.find(event => event.time === timeString)
    if (timeEvent) {
      switch (timeEvent.effect) {
        case 'guaranteed':
          return 1.0
        case 'double_chance':
          probability *= 2
          break
      }
    }

    // 整点加成
    if (now.getMinutes() === 0) {
      probability *= 1.5
    }

    // 节日加成
    if (this.isChristmasSeason()) {
      probability *= 1.5
    }

    return Math.min(probability, 1.0)
  }

  /**
   * 播放彩蛋动画
   */
  private async playEasterEgg(): Promise<void> {
    // 选择动画类型
    const animationType = this.selectAnimation()
    this.seenAnimations.add(animationType)

    // 检查特殊事件
    const shouldDouble = Math.random() < this.randomEvents.doubleTrigger
    const showBadge = Math.random() < this.randomEvents.withBadge
    const showMessage = Math.random() < this.randomEvents.withMessage
    const playSound = Math.random() < this.randomEvents.withSound

    console.log(`🎁 Ming的神秘礼盒被打开了！`)
    console.log(`🐱 小猫咪表演: ${animationType}`)
    console.log(`✨ Created with love by Ming (鹿鸣) ✨`)

    // 触发自定义事件
    window.dispatchEvent(new CustomEvent('ming-easter-egg', {
      detail: {
        animationType,
        shouldDouble,
        showBadge,
        showMessage,
        playSound,
        triggerCount: this.totalTriggers
      }
    }))

    // 播放音效
    if (playSound && (window as any).audioManager) {
      (window as any).audioManager.playSound('success')
    }
  }

  /**
   * 选择动画类型
   */
  private selectAnimation(): MingAnimationType {
    const now = new Date()
    const hour = now.getHours()
    const timeString = `${hour.toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    // 检查时间特殊事件
    const timeEvent = this.timeEvents.find(event => event.time === timeString)
    if (timeEvent && timeEvent.animation) {
      return timeEvent.animation
    }

    // 时间感知选择
    if (hour >= 22 || hour <= 6) {
      return MingAnimationType.ESCAPE  // 深夜冒险
    } else if (hour >= 18) {
      return MingAnimationType.RETURN  // 温馨回家
    } else if (hour >= 9) {
      return MingAnimationType.DIRECT  // 工作时间害羞
    }

    // 随机选择
    const random = Math.random()
    let cumulative = 0
    
    for (const [type, weight] of Object.entries(this.animationWeights)) {
      cumulative += weight
      if (random < cumulative) {
        return type as MingAnimationType
      }
    }

    return MingAnimationType.DIRECT
  }

  /**
   * 检查成就解锁
   */
  private checkAchievements(): void {
    // 首次发现
    if (this.totalTriggers === 1) {
      this.unlockAchievement('first_discovery')
    }

    // 好奇心重
    if (this.totalTriggers === 3) {
      this.unlockAchievement('curious_explorer')
    }

    // 动画收集家
    if (this.seenAnimations.size === 3) {
      this.unlockAchievement('animation_collector')
    }

    // Ming的挚友
    if (this.totalTriggers >= 10) {
      this.unlockAchievement('ming_best_friend')
    }

    // 时间魔法师
    const now = new Date()
    const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    if (this.timeEvents.some(event => event.time === timeString)) {
      this.unlockAchievement('time_wizard')
    }
  }

  /**
   * 解锁成就
   */
  private unlockAchievement(achievementId: string): void {
    const achievement = this.achievements.get(achievementId)
    if (achievement && !achievement.unlocked) {
      achievement.unlocked = true
      achievement.unlockedAt = new Date()
      
      console.log(`🏆 成就解锁: ${achievement.name}`)
      console.log(`📖 ${achievement.description}`)
      
      // 触发成就解锁事件
      window.dispatchEvent(new CustomEvent('ming-achievement-unlocked', {
        detail: achievement
      }))
    }
  }

  /**
   * 设置控制台监听
   */
  private setupConsoleListener(): void {
    // 监听控制台输入（简化版）
    const originalLog = console.log
    console.log = (...args) => {
      const message = args.join(' ').toLowerCase()
      if (message.includes('ming') || message.includes('鹿鸣')) {
        this.attemptTrigger('console')
      }
      originalLog.apply(console, args)
    }
  }

  /**
   * 设置Konami Code监听
   */
  private setupKonamiListener(): void {
    const sequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA']
    let currentSequence: string[] = []

    document.addEventListener('keydown', (event) => {
      currentSequence.push(event.code)
      
      if (currentSequence.length > sequence.length) {
        currentSequence = currentSequence.slice(-sequence.length)
      }
      
      if (currentSequence.length === sequence.length && 
          currentSequence.every((key, index) => key === sequence[index])) {
        this.unlockAchievement('konami_master')
        this.playEasterEgg()
        currentSequence = []
      }
    })
  }

  /**
   * 设置开发者工具监听
   */
  private setupDevToolsListener(): void {
    // 检测开发者工具打开
    let devtools = false
    setInterval(() => {
      if ((window as any).outerHeight - (window as any).innerHeight > 200) {
        if (!devtools) {
          devtools = true
          console.log(`
🔍 欢迎来到Ming的开发者世界！
🎯 你是一个真正的探索者！
🎁 输入 "ming.secret()" 来获取特殊奖励！
          `)
          ;(window as any).ming = {
            secret: () => {
              this.unlockAchievement('developer_explorer')
              this.playEasterEgg()
              return '🎉 恭喜你发现了开发者彩蛋！'
            }
          }
        }
      } else {
        devtools = false
      }
    }, 500)
  }

  /**
   * 检查是否为圣诞季节
   */
  private isChristmasSeason(): boolean {
    const now = new Date()
    return now.getMonth() === 11 // 12月
  }

  /**
   * 获取统计信息
   */
  public getStats() {
    return {
      totalTriggers: this.totalTriggers,
      seenAnimations: Array.from(this.seenAnimations),
      unlockedAchievements: Array.from(this.achievements.values()).filter(a => a.unlocked),
      triggerCounts: Object.fromEntries(this.triggerCounts)
    }
  }

  /**
   * 重置所有进度
   */
  public reset(): void {
    this.totalTriggers = 0
    this.triggerCounts.clear()
    this.seenAnimations.clear()
    this.lastTriggerTime.clear()
    this.achievements.forEach(achievement => {
      achievement.unlocked = false
      achievement.unlockedAt = undefined
    })
    localStorage.removeItem('ming-easter-egg-progress')
    console.log('🔄 Ming彩蛋系统已重置')
  }
}

// 导出单例实例
export const mingEasterEgg = MingEasterEggEngine.getInstance()

// 全局暴露（调试用）
if (typeof window !== 'undefined') {
  ;(window as any).mingEasterEgg = mingEasterEgg
} 