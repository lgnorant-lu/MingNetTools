<template>
  <div class="pixel-pet" :class="{ 'pet-active': isActive }">
    <div class="pet-container" @click="handleEnhancedClick" ref="petRef">
      <!-- 猫咪像素图 -->
      <div v-if="petType === 'cat'" class="pet-sprite cat-sprite" :class="currentAnimation">
        <div class="pixel-art cat-body">
          <div class="cat-ear-left"></div>
          <div class="cat-ear-right"></div>
          <div class="cat-head">
            <div class="cat-eye-left" :class="{ blink: isBlinking }"></div>
            <div class="cat-eye-right" :class="{ blink: isBlinking }"></div>
            <div class="cat-nose"></div>
          </div>
          <div class="cat-body-main"></div>
          <div class="cat-tail" :class="{ wag: isWagging }"></div>
        </div>
      </div>
      
      <!-- 狗狗像素图 -->
      <div v-else class="pet-sprite dog-sprite" :class="currentAnimation">
        <div class="pixel-art dog-body">
          <div class="dog-ear-left"></div>
          <div class="dog-ear-right"></div>
          <div class="dog-head">
            <div class="dog-eye-left" :class="{ blink: isBlinking }"></div>
            <div class="dog-eye-right" :class="{ blink: isBlinking }"></div>
            <div class="dog-nose"></div>
            <div class="dog-tongue" v-if="isHappy"></div>
          </div>
          <div class="dog-body-main"></div>
          <div class="dog-tail" :class="{ wag: isWagging }"></div>
        </div>
      </div>
      
      <!-- 粒子容器 -->
      <div ref="particleContainer" class="particle-container"></div>
    </div>
    
    <!-- 状态气泡 -->
    <div class="status-bubble" v-if="statusMessage" :class="statusType">
      <div class="bubble-text">{{ statusMessage }}</div>
      <div class="combo-indicator" v-if="interactionCombo > 1">
        {{ interactionCombo }}x COMBO!
      </div>
    </div>
    
    <!-- 切换按钮 -->
    <button class="pet-switch pixel-btn" @click="switchPet">
      {{ petType === 'cat' ? '🐕' : '🐱' }}
    </button>
    
    <!-- 工作模式切换按钮 -->
    <button class="work-toggle pixel-btn" @click="toggleWorkMode" title="切换工作模式">
      {{ currentAnimation === 'working' ? '😴' : '💻' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { PixelAnimations } from '../../utils/animations'
import { useThemeStore } from '../../stores/theme'
import { playSound, useAudio } from '../../utils/audioManager'
import type { ThemeMode } from '../../stores/theme'

// Store
const themeStore = useThemeStore()

// Audio
const audio = useAudio()

// 宠物类型
const petType = ref<'cat' | 'dog'>('cat')
const isActive = ref(false)
const isBlinking = ref(false)
const isWagging = ref(false)
const isHappy = ref(false)
const currentAnimation = ref('')
const statusMessage = ref('')
const statusType = ref<'success' | 'warning' | 'error' | 'info'>('info')

// 新增状态
const isFloating = ref(false)
const showParticles = ref(false)
const interactionCombo = ref(0)
const lastInteractionTime = ref(0)
const petRef = ref<HTMLElement>()
const particleContainer = ref<HTMLElement>()
const isBouncing = ref(false)

// 动画定时器
let blinkTimer: number
let wagTimer: number
let statusTimer: number

// 宠物点击事件
const petClick = () => {
  handleEnhancedClick()
}

// 普通点击处理
const handleClick = () => {
  isActive.value = true
  isHappy.value = true
  showStatus('喵~ / 汪~', 'success')
  
  // 播放点击音效
  audio.playSuccessSound()
  
  setTimeout(() => {
    isActive.value = false
    isHappy.value = false
  }, 1000)
}

// 切换宠物
const switchPet = () => {
  petType.value = petType.value === 'cat' ? 'dog' : 'cat'
  showStatus('切换成功!', 'info')
  
  // 播放切换音效
  playSound('whoosh')
}

// 显示状态消息
const showStatus = (message: string, type: 'success' | 'warning' | 'error' | 'info' = 'info') => {
  statusMessage.value = message
  statusType.value = type
  
  if (statusTimer) clearTimeout(statusTimer)
  statusTimer = setTimeout(() => {
    statusMessage.value = ''
  }, 2000)
}

// 显示消息的别名方法
const showMessage = (message: string): void => {
  // 发送消息事件给父组件或全局消息系统
  window.dispatchEvent(new CustomEvent('pet-message', {
    detail: { message, timestamp: Date.now() }
  }))
  
  console.log(`🐾 ${petData.value.name}: ${message}`)
}

// 设置心情状态
const setMood = (mood: string) => {
  currentAnimation.value = mood
}

// 随机眨眼动画
const startBlinking = () => {
  const blink = () => {
    isBlinking.value = true
    setTimeout(() => {
      isBlinking.value = false
    }, 150)
  }
  
  blinkTimer = setInterval(() => {
    if (Math.random() < 0.3) {
      blink()
    }
  }, 2000)
}

// 随机摇尾巴动画
const startWagging = () => {
  wagTimer = setInterval(() => {
    if (Math.random() < 0.4) {
      isWagging.value = true
      setTimeout(() => {
        isWagging.value = false
      }, 1000)
    }
  }, 3000)
}

// 响应系统状态
const respondToSystemStatus = (status: string) => {
  switch (status) {
    case 'scanning':
      currentAnimation.value = 'alert'
      showStatus('正在扫描...', 'warning')
      audio.playNotificationSound()
      break
    case 'success':
      currentAnimation.value = 'happy'
      showStatus('任务完成!', 'success')
      audio.playSuccessSound()
      break
    case 'error':
      currentAnimation.value = 'sad'
      showStatus('出错了...', 'error')
      audio.playErrorSound()
      break
    default:
      currentAnimation.value = ''
  }
}

// 计算属性 - 修正版本
const petClass = computed(() => ({
  [`pixel-pet-${petType.value}`]: true,
  'blinking': isBlinking.value,
  'tail-wagging': isWagging.value,
  'floating': isFloating.value,
  [`animation-${currentAnimation.value}`]: currentAnimation.value
}))

const statusBubbleClass = computed(() => ({
  'status-bubble': true,
  'visible': !!statusMessage.value
}))

// 监听主题变化
watch(() => themeStore.currentMode, (newTheme) => {
  handleThemeChange(newTheme)
})

onMounted(() => {
  startBlinking()
  startWagging()
  
  // 监听系统状态变化
  window.addEventListener('system-status-change', (event: any) => {
    respondToSystemStatus(event.detail.status)
  })
})

onUnmounted(() => {
  if (blinkTimer) clearInterval(blinkTimer)
  if (wagTimer) clearInterval(wagTimer)
  if (statusTimer) clearTimeout(statusTimer)
})

// 暴露方法给父组件
defineExpose({
  showStatus,
  respondToSystemStatus
})

// 新增方法

/**
 * 处理主题切换
 */
const handleThemeChange = (theme: ThemeMode) => {
  // 支持所有主题类型，不仅限于dark/light
  switch (theme) {
    case 'light':
      startThemeTransitionAnimation()
      showMessage('☀️ 白猫模式!')
      setMood('excited')
      createThemeParticles('light')
      break
    case 'dark':
      startThemeTransitionAnimation()
      showMessage('🌙 夜狗模式!')
      setMood('alert')
      createThemeParticles('dark')
      break
    case 'ocean':
      startThemeTransitionAnimation()
      showMessage('🌊 深海探索!')
      setMood('curious')
      createThemeParticles('dark')
      break
    case 'forest':
      startThemeTransitionAnimation()
      showMessage('🌲 森林清新!')
      setMood('happy')
      createThemeParticles('light')
      break
    case 'sunset':
      startThemeTransitionAnimation()
      showMessage('🌅 温暖夕阳!')
      setMood('excited')
      createThemeParticles('light')
      break
    case 'aurora':
      startThemeTransitionAnimation()
      showMessage('🌌 极光梦幻!')
      setMood('celebrating')
      createThemeParticles('dark')
      break
    default:
      // 默认处理
      setMood('happy')
      break
  }
}

/**
 * 主题切换动画
 */
const startThemeTransitionAnimation = () => {
  if (!petRef.value) return
  
  currentAnimation.value = 'theme-switch'
  PixelAnimations.pixelCardFlip(petRef.value)
  
  // 创建能量环绕效果
  createEnergyOrbit()
  
  setTimeout(() => {
    currentAnimation.value = ''
  }, 600)
}

/**
 * 创建主题粒子效果
 */
const createThemeParticles = (theme: 'light' | 'dark') => {
  showParticles.value = true
  
  if (!particleContainer.value) return
  
  const colors = theme === 'light' 
    ? ['#1a365d', '#0891b2', '#047857'] // 白天主题色
    : ['#00ff41', '#00ffff', '#ff00ff'] // 夜晚主题色
  
  for (let i = 0; i < 12; i++) {
    const particle = document.createElement('div')
    particle.className = 'theme-particle'
    
    const color = colors[Math.floor(Math.random() * colors.length)]
    const size = 3 + Math.random() * 4
    const delay = i * 100
    
    Object.assign(particle.style, {
      position: 'absolute',
      width: size + 'px',
      height: size + 'px',
      background: color,
      borderRadius: '50%',
      pointerEvents: 'none',
      animation: `themeParticleFloat 3s ease-out ${delay}ms forwards`
    })
    
    particleContainer.value.appendChild(particle)
    
    // 清理粒子
    setTimeout(() => {
      if (particleContainer.value?.contains(particle)) {
        particleContainer.value.removeChild(particle)
      }
    }, 3000 + delay)
  }
  
  setTimeout(() => {
    showParticles.value = false
  }, 4000)
}

/**
 * 创建能量环绕效果
 */
const createEnergyOrbit = () => {
  if (!petRef.value) return
  
  const orbit = document.createElement('div')
  orbit.className = 'energy-orbit'
  
  Object.assign(orbit.style, {
    position: 'absolute',
    top: '-20px',
    left: '-20px',
    right: '-20px',
    bottom: '-20px',
    border: '2px solid var(--pixel-primary)',
    borderRadius: '50%',
    opacity: '0.6',
    animation: 'energyOrbit 2s ease-out forwards',
    pointerEvents: 'none'
  })
  
  petRef.value.style.position = 'relative'
  petRef.value.appendChild(orbit)
  
  // 添加CSS动画
  if (!document.querySelector('#energy-orbit-style')) {
    const style = document.createElement('style')
    style.id = 'energy-orbit-style'
    style.textContent = `
      @keyframes energyOrbit {
        0% { 
          transform: scale(0) rotate(0deg); 
          opacity: 0.8; 
        }
        50% { 
          transform: scale(1.2) rotate(180deg); 
          opacity: 0.4; 
        }
        100% { 
          transform: scale(2) rotate(360deg); 
          opacity: 0; 
        }
      }
    `
    document.head.appendChild(style)
  }
  
  // 清理轨道
  setTimeout(() => {
    if (petRef.value?.contains(orbit)) {
      petRef.value.removeChild(orbit)
    }
  }, 2000)
}

/**
 * 增强点击处理
 */
const handleEnhancedClick = () => {
  if (!petRef.value) return
  
  const now = Date.now()
  const timeDiff = now - lastInteractionTime.value
  
  // 连击检测
  if (timeDiff < 1000) {
    interactionCombo.value++
  } else {
    interactionCombo.value = 1
  }
  
  lastInteractionTime.value = now
  
  // Ming彩蛋触发检测
  if (interactionCombo.value === 5) {
    // 尝试触发Ming彩蛋
    tryTriggerMingEasterEgg()
  }
  
  // 根据连击数触发不同效果
  if (interactionCombo.value >= 5) {
    // 超级连击！
    triggerSuperCombo()
  } else if (interactionCombo.value >= 3) {
    // 连击效果
    triggerComboEffect()
  } else {
    // 普通点击
    handleClick()
  }
  
  // 添加游戏化反馈
  PixelAnimations.gamingClickFeedback(petRef.value)
  PixelAnimations.createParticleExplosion(petRef.value, interactionCombo.value + 3)
}

/**
 * 尝试触发Ming彩蛋
 */
const tryTriggerMingEasterEgg = async () => {
  try {
    // 动态导入Ming彩蛋引擎
    const { mingEasterEgg } = await import('../../utils/mingEasterEgg')
    
    // 尝试触发pixelPet彩蛋
    const triggered = await mingEasterEgg.attemptTrigger('pixelPet')
    
    if (triggered) {
      // 彩蛋触发成功，增强宠物反应
      setMood('excited')
      showMessage('🎁 哇！你发现了什么特别的东西！')
      
      // 特殊粒子效果
      createMingSpecialParticles()
    } else {
      // 彩蛋未触发，给出暗示
      if (Math.random() < 0.3) {
        showMessage('🤔 我感觉有什么特别的事情要发生了...')
      }
    }
  } catch (error) {
    console.warn('Ming彩蛋系统加载失败:', error)
  }
}

/**
 * 创建Ming特殊粒子效果
 */
const createMingSpecialParticles = () => {
  if (!particleContainer.value) return
  
  const specialColors = [
    'var(--primary-color)',
    '#FF1493', // 粉红色
    '#00FFFF', // 青色
    '#FFD700'  // 金色
  ]
  
  for (let i = 0; i < 15; i++) {
    const particle = document.createElement('div')
    particle.className = 'ming-special-particle'
    
    const color = specialColors[i % specialColors.length]
    const size = 6 + Math.random() * 8
    const delay = i * 100
    
    Object.assign(particle.style, {
      position: 'absolute',
      width: size + 'px',
      height: size + 'px',
      background: color,
      borderRadius: '50%',
      boxShadow: `0 0 15px ${color}, 0 0 30px ${color}`,
      pointerEvents: 'none',
      animation: `mingParticleFloat 3s ease-out ${delay}ms forwards`
    })
    
    particleContainer.value.appendChild(particle)
    
    setTimeout(() => {
      if (particleContainer.value?.contains(particle)) {
        particleContainer.value.removeChild(particle)
      }
    }, 3000 + delay)
  }
}

/**
 * 超级连击效果
 */
const triggerSuperCombo = () => {
  setMood('excited')
  isBouncing.value = true
  showMessage('🎉 SUPER COMBO!!! 你太厉害了!')
  
  // 特殊动画
  currentAnimation.value = 'super-combo'
  
  // 创建彩虹粒子
  createRainbowParticles()
  
  // 重置连击
  interactionCombo.value = 0
  
  setTimeout(() => {
    isBouncing.value = false
    currentAnimation.value = ''
    setMood('happy')
  }, 2000)
}

/**
 * 连击效果
 */
const triggerComboEffect = () => {
  setMood('excited')
  showMessage(`💫 ${interactionCombo.value}连击! 继续加油!`)
  
  // 连击动画
  if (petRef.value) {
    PixelAnimations.pixelButtonClick(petRef.value, { duration: 150 })
  }
}

/**
 * 创建彩虹粒子效果
 */
const createRainbowParticles = () => {
  if (!particleContainer.value) return
  
  const rainbowColors = [
    '#ff0000', '#ff8000', '#ffff00', '#80ff00', 
    '#00ff00', '#00ff80', '#00ffff', '#0080ff',
    '#0000ff', '#8000ff', '#ff00ff', '#ff0080'
  ]
  
  for (let i = 0; i < 20; i++) {
    const particle = document.createElement('div')
    particle.className = 'rainbow-particle'
    
    const color = rainbowColors[i % rainbowColors.length]
    const size = 4 + Math.random() * 6
    const delay = i * 50
    
    Object.assign(particle.style, {
      position: 'absolute',
      width: size + 'px',
      height: size + 'px',
      background: color,
      borderRadius: '50%',
      boxShadow: `0 0 10px ${color}`,
      pointerEvents: 'none',
      animation: `rainbowParticle 2s ease-out ${delay}ms forwards`
    })
    
    particleContainer.value.appendChild(particle)
    
    setTimeout(() => {
      if (particleContainer.value?.contains(particle)) {
        particleContainer.value.removeChild(particle)
      }
    }, 2000 + delay)
  }
}

/**
 * 工作模式切换
 */
const toggleWorkMode = () => {
  if (currentAnimation.value === 'working') {
    setMood('happy')
    showMessage('😊 工作完成！我们休息一下吧')
    isFloating.value = false
  } else {
    setMood('working')
    showMessage('💻 专注工作模式开启！')
    isFloating.value = true
    startWorkAnimation()
  }
}

/**
 * 开始工作动画
 */
const startWorkAnimation = () => {
  if (!petRef.value) return
  
  PixelAnimations.dataFlowEffect(petRef.value)
  PixelAnimations.neonGlowPulse(petRef.value, 'var(--neon-cyan)')
}

// 扩展现有的系统状态处理
const handleSystemStatus = (event: CustomEvent) => {
  const { status, theme } = event.detail
  
  switch (status) {
    case 'theme-switch':
      handleThemeChange(theme)
      break
    case 'scanning':
      setMood('working')
      showMessage('🔍 正在扫描...')
      if (petRef.value) {
        PixelAnimations.loadingAnimation(petRef.value, 'matrix')
      }
      break
    case 'scan-complete':
      setMood('excited')
      showMessage('✅ 扫描完成!')
      if (petRef.value) {
        PixelAnimations.stopLoadingAnimation(petRef.value)
        PixelAnimations.statusChangeAnimation(petRef.value, 'success')
      }
      break
    case 'error':
      setMood('sad')
      showMessage('❌ 出错了...')
      if (petRef.value) {
        PixelAnimations.statusChangeAnimation(petRef.value, 'error')
      }
      break
    case 'success':
      setMood('happy')
      showMessage('🎉 操作成功!')
      if (petRef.value) {
        PixelAnimations.statusChangeAnimation(petRef.value, 'success')
      }
      break
    case 'ready':
      setMood('alert')
      showMessage('🚀 系统就绪!')
      break
    default:
      // 保持现有逻辑
      break
  }
}

// 宠物状态类型
export type PetMood = 'happy' | 'excited' | 'sleepy' | 'working' | 'alert' | 'curious' | 'celebrating' | 'thinking'
export type PetActivity = 'idle' | 'walking' | 'jumping' | 'dancing' | 'scanning' | 'monitoring' | 'sleeping' | 'playing'

// 宠物数据接口
interface PetData {
  name: string
  mood: PetMood
  activity: PetActivity
  energy: number
  happiness: number
  experience: number
  level: number
  lastInteraction: Date
  preferences: {
    favoriteTheme: string
    favoriteTime: string
    personality: 'active' | 'calm' | 'playful' | 'serious'
  }
}

// 互动选项
interface InteractionOption {
  id: string
  name: string
  icon: string
  description: string
  energyCost: number
  happinessBonus: number
  unlockLevel: number
  cooldown: number // 冷却时间（毫秒）
}

// 宠物状态
const petData = ref<PetData>({
  name: '赛博小助手',
  mood: 'happy',
  activity: 'idle',
  energy: 100,
  happiness: 80,
  experience: 0,
  level: 1,
  lastInteraction: new Date(),
  preferences: {
    favoriteTheme: 'dark',
    favoriteTime: 'night',
    personality: 'playful'
  }
})

// 互动选项
const interactionOptions: InteractionOption[] = [
  {
    id: 'pet',
    name: '抚摸',
    icon: '🖐️',
    description: '轻抚宠物，增加亲密度',
    energyCost: 0,
    happinessBonus: 10,
    unlockLevel: 1,
    cooldown: 5000
  },
  {
    id: 'play',
    name: '游戏',
    icon: '🎮',
    description: '和宠物一起玩游戏',
    energyCost: 20,
    happinessBonus: 25,
    unlockLevel: 1,
    cooldown: 30000
  },
  {
    id: 'feed',
    name: '投食',
    icon: '🍪',
    description: '给宠物喂食，恢复能量',
    energyCost: -30,
    happinessBonus: 15,
    unlockLevel: 2,
    cooldown: 60000
  },
  {
    id: 'train',
    name: '训练',
    icon: '💪',
    description: '训练宠物技能，获得经验',
    energyCost: 30,
    happinessBonus: 5,
    unlockLevel: 3,
    cooldown: 120000
  },
  {
    id: 'dance',
    name: '跳舞',
    icon: '💃',
    description: '一起跳舞庆祝',
    energyCost: 15,
    happinessBonus: 20,
    unlockLevel: 5,
    cooldown: 45000
  }
]

// 互动冷却状态
const interactionCooldowns = ref<Record<string, number>>({})

// 宠物可见性和位置
const isVisible = ref(true)
const petPosition = ref({ x: 50, y: 50 })
const isDragging = ref(false)
const showInteractionMenu = ref(false)
const showStatsPanel = ref(false)

// 动画状态
const isAnimating = ref(false)

// 音效状态
const soundEnabled = ref(true)

// 获取当前宠物精灵图
const getCurrentSprite = computed(() => {
  const { mood, activity } = petData.value
  return `/sprites/pet_${mood}_${activity}.png`
})

// 获取宠物状态颜色
const getMoodColor = computed(() => {
  const colors = {
    happy: '#00ff41',
    excited: '#ff6600',
    sleepy: '#8a2be2',
    working: '#00d4ff',
    alert: '#ff4444',
    curious: '#ffff00',
    celebrating: '#ff00ff',
    thinking: '#39ff14'
  }
  return colors[petData.value.mood] || '#00ff41'
})

// 获取可用的互动选项
const availableInteractions = computed(() => {
  return interactionOptions.filter(option => 
    petData.value.level >= option.unlockLevel &&
    (!interactionCooldowns.value[option.id] || 
     Date.now() - interactionCooldowns.value[option.id] > option.cooldown)
  )
})

// 经验值到下一级的百分比
const experienceProgress = computed(() => {
  const requiredExp = petData.value.level * 100
  return Math.min((petData.value.experience / requiredExp) * 100, 100)
})

// 方法

/**
 * 执行互动
 */
const performInteraction = async (option: InteractionOption): Promise<void> => {
  if (interactionCooldowns.value[option.id] && 
      Date.now() - interactionCooldowns.value[option.id] < option.cooldown) {
    return
  }

  // 检查能量
  if (petData.value.energy + option.energyCost < 0) {
    showMessage('宠物太累了，需要休息!')
    return
  }

  // 执行互动
  petData.value.energy = Math.max(0, Math.min(100, petData.value.energy + option.energyCost))
  petData.value.happiness = Math.min(100, petData.value.happiness + option.happinessBonus)
  petData.value.experience += option.happinessBonus
  petData.value.lastInteraction = new Date()

  // 设置冷却
  interactionCooldowns.value[option.id] = Date.now()

  // 播放相应动画
  await playInteractionAnimation(option.id)

  // 播放音效 - 添加类型保护
  if (soundEnabled.value) {
    try {
      // 只播放已定义的音效类型
      const validSounds = ['click', 'success', 'error', 'notification', 'whoosh']
      const soundKey = `interaction_${option.id}`
      if (validSounds.includes(soundKey)) {
        playSound(soundKey as any)
      } else {
        // 使用默认成功音效
        audio.playSuccessSound()
      }
    } catch (error) {
      console.warn('音效播放失败:', error)
      audio.playSuccessSound()
    }
  }

  // 检查升级
  checkLevelUp()

  // 保存数据
  savePetData()

  // 隐藏菜单
  showInteractionMenu.value = false

  // 显示反馈消息
  showMessage(`${option.name}成功! 宠物很开心!`)
}

/**
 * 播放互动动画
 */
const playInteractionAnimation = async (interactionId: string): Promise<void> => {
  isAnimating.value = true
  
  switch (interactionId) {
    case 'pet':
      petData.value.activity = 'jumping'
      petData.value.mood = 'happy'
      break
    case 'play':
      petData.value.activity = 'dancing'
      petData.value.mood = 'excited'
      break
    case 'feed':
      petData.value.activity = 'idle'
      petData.value.mood = 'happy'
      break
    case 'train':
      petData.value.activity = 'walking'
      petData.value.mood = 'working'
      break
    case 'dance':
      petData.value.activity = 'dancing'
      petData.value.mood = 'celebrating'
      break
  }

  // 动画持续时间
  await new Promise(resolve => setTimeout(resolve, 3000))
  
  // 恢复默认状态
  petData.value.activity = 'idle'
  if (petData.value.happiness > 70) {
    petData.value.mood = 'happy'
  } else if (petData.value.energy < 30) {
    petData.value.mood = 'sleepy'
  } else {
    petData.value.mood = 'happy'
  }
  
  isAnimating.value = false
}

/**
 * 检查升级
 */
const checkLevelUp = (): void => {
  const requiredExp = petData.value.level * 100
  if (petData.value.experience >= requiredExp) {
    petData.value.level++
    petData.value.experience -= requiredExp
    petData.value.happiness = Math.min(100, petData.value.happiness + 20)
    
    // 升级庆祝动画
    celebrateLevelUp()
    
    showMessage(`🎉 恭喜! 宠物升级到 Lv.${petData.value.level}!`)
  }
}

/**
 * 升级庆祝动画
 */
const celebrateLevelUp = async (): Promise<void> => {
  petData.value.mood = 'celebrating'
  petData.value.activity = 'dancing'
  
  // 创建粒子效果
  createLevelUpParticles()
  
  // 播放升级音效 - 添加类型保护
  if (soundEnabled.value) {
    try {
      // 使用成功音效代替不存在的levelup音效
      audio.playSuccessSound()
    } catch (error) {
      console.warn('升级音效播放失败:', error)
    }
  }
  
  await new Promise(resolve => setTimeout(resolve, 5000))
  
  petData.value.mood = 'happy'
  petData.value.activity = 'idle'
}

/**
 * 创建升级粒子效果
 */
const createLevelUpParticles = (): void => {
  const pet = petRef.value
  if (!pet) return
  
  for (let i = 0; i < 10; i++) {
    setTimeout(() => {
      const particle = document.createElement('div')
      particle.className = 'levelup-particle'
      particle.style.cssText = `
        position: absolute;
        width: 8px;
        height: 8px;
        background: linear-gradient(45deg, #ffd700, #ffed4e);
        border-radius: 50%;
        pointer-events: none;
        left: ${Math.random() * 60 + 20}%;
        top: ${Math.random() * 60 + 20}%;
        animation: levelupParticle 2s ease-out forwards;
        z-index: 1000;
      `
      
      pet.appendChild(particle)
      
      setTimeout(() => {
        if (particle.parentNode) {
          particle.parentNode.removeChild(particle)
        }
      }, 2000)
    }, i * 100)
  }
}

/**
 * 自动行为系统
 */
const initAutoBehavior = (): void => {
  // 每10秒检查一次自动行为
  setInterval(() => {
    if (isAnimating.value || isDragging.value) return
    
    // 随机触发自动行为
    if (Math.random() < 0.3) {
      performAutoBehavior()
    }
    
    // 能量和快乐度自然衰减
    if (Math.random() < 0.1) {
      petData.value.energy = Math.max(0, petData.value.energy - 1)
      petData.value.happiness = Math.max(0, petData.value.happiness - 1)
    }
    
    // 根据状态调整心情
    updateMoodBasedOnStats()
    
  }, 10000)
}

/**
 * 执行自动行为
 */
const performAutoBehavior = async (): Promise<void> => {
  const behaviors = ['walking', 'jumping', 'idle']
  const randomBehavior = behaviors[Math.floor(Math.random() * behaviors.length)]
  
  petData.value.activity = randomBehavior as PetActivity
  
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  petData.value.activity = 'idle'
}

/**
 * 根据统计数据更新心情
 */
const updateMoodBasedOnStats = (): void => {
  if (petData.value.energy < 20) {
    petData.value.mood = 'sleepy'
  } else if (petData.value.happiness > 80) {
    petData.value.mood = 'happy'
  } else if (petData.value.happiness < 30) {
    petData.value.mood = 'alert'
  } else {
    petData.value.mood = 'happy'
  }
}

/**
 * 响应系统事件
 */
const initSystemEventListeners = (): void => {
  // 主题变化
  window.addEventListener('theme-change', (event: any) => {
    const { theme } = event.detail
    petData.value.preferences.favoriteTheme = theme
    
    if (theme === 'dark') {
      petData.value.mood = 'working'
      showMessage('宠物喜欢这个深色主题!')
    } else {
      petData.value.mood = 'happy'
      showMessage('宠物感觉很亮眼!')
    }
  })
  
  // 扫描开始
  window.addEventListener('scan-started', () => {
    petData.value.activity = 'scanning'
    petData.value.mood = 'working'
    showMessage('宠物正在帮你监控扫描进度...')
  })
  
  // 扫描完成
  window.addEventListener('scan-completed', () => {
    petData.value.activity = 'jumping'
    petData.value.mood = 'excited'
    performInteraction(interactionOptions[0]) // 自动奖励
    showMessage('扫描完成! 宠物很兴奋!')
  })
  
  // 语言切换
  window.addEventListener('language-changed', (event: any) => {
    const { language } = event.detail
    if (language === 'en') {
      petData.value.name = 'Cyber Assistant'
    } else {
      petData.value.name = '赛博小助手'
    }
    showMessage(`${petData.value.name} 说：语言切换成功!`)
  })
}

/**
 * 保存宠物数据到localStorage
 */
const savePetData = (): void => {
  try {
    const dataToSave = {
      ...petData.value,
      lastInteraction: petData.value.lastInteraction.toISOString()
    }
    localStorage.setItem('pixelPetData', JSON.stringify(dataToSave))
  } catch (error) {
    console.warn('Failed to save pet data:', error)
  }
}

/**
 * 从localStorage加载宠物数据
 */
const loadPetData = (): void => {
  try {
    const saved = localStorage.getItem('pixelPetData')
    if (saved) {
      const data = JSON.parse(saved)
      Object.assign(petData.value, {
        ...data,
        lastInteraction: new Date(data.lastInteraction)
      })
    }
  } catch (error) {
    console.warn('Failed to load pet data:', error)
  }
}

// 组件接口
interface Props {
  initialMood?: 'happy' | 'sleepy' | 'excited' | 'working'
  enableInteraction?: boolean
  showStatus?: boolean
  soundEnabled?: boolean
}
</script>

<style scoped>
.pixel-pet {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  user-select: none;
}

.pet-container {
  cursor: pointer;
  transition: transform 0.1s ease;
}

.pet-container:hover {
  transform: scale(1.1);
}

.pet-active .pet-container {
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 像素艺术基础 */
.pixel-art {
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
}

/* 猫咪样式 */
.cat-sprite {
  width: 64px;
  height: 64px;
  position: relative;
}

.cat-ear-left, .cat-ear-right {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--pixel-primary);
  top: 8px;
}

.cat-ear-left { left: 12px; }
.cat-ear-right { right: 12px; }

.cat-head {
  position: absolute;
  width: 32px;
  height: 24px;
  background: var(--pixel-primary);
  top: 12px;
  left: 16px;
  border-radius: 2px;
}

.cat-eye-left, .cat-eye-right {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--bg-dark);
  top: 6px;
  transition: height 0.1s ease;
}

.cat-eye-left { left: 6px; }
.cat-eye-right { right: 6px; }

.cat-eye-left.blink, .cat-eye-right.blink {
  height: 1px;
}

.cat-nose {
  position: absolute;
  width: 2px;
  height: 2px;
  background: var(--neon-pink);
  top: 12px;
  left: 15px;
}

.cat-body-main {
  position: absolute;
  width: 24px;
  height: 20px;
  background: var(--pixel-primary);
  top: 32px;
  left: 20px;
}

.cat-tail {
  position: absolute;
  width: 4px;
  height: 16px;
  background: var(--pixel-primary);
  top: 36px;
  right: 8px;
  transform-origin: top;
  transition: transform 0.3s ease;
}

.cat-tail.wag {
  animation: tail-wag 0.5s ease-in-out infinite alternate;
}

/* 狗狗样式 */
.dog-sprite {
  width: 64px;
  height: 64px;
  position: relative;
}

.dog-ear-left, .dog-ear-right {
  position: absolute;
  width: 12px;
  height: 16px;
  background: var(--pixel-accent);
  top: 8px;
  border-radius: 0 0 4px 4px;
}

.dog-ear-left { left: 8px; }
.dog-ear-right { right: 8px; }

.dog-head {
  position: absolute;
  width: 32px;
  height: 28px;
  background: var(--pixel-accent);
  top: 12px;
  left: 16px;
  border-radius: 4px;
}

.dog-eye-left, .dog-eye-right {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--bg-dark);
  top: 8px;
  transition: height 0.1s ease;
}

.dog-eye-left { left: 6px; }
.dog-eye-right { right: 6px; }

.dog-eye-left.blink, .dog-eye-right.blink {
  height: 1px;
}

.dog-nose {
  position: absolute;
  width: 4px;
  height: 3px;
  background: var(--bg-dark);
  top: 14px;
  left: 14px;
  border-radius: 2px;
}

.dog-tongue {
  position: absolute;
  width: 6px;
  height: 4px;
  background: var(--neon-pink);
  top: 18px;
  left: 13px;
  border-radius: 0 0 3px 3px;
}

.dog-body-main {
  position: absolute;
  width: 28px;
  height: 20px;
  background: var(--pixel-accent);
  top: 36px;
  left: 18px;
}

.dog-tail {
  position: absolute;
  width: 6px;
  height: 12px;
  background: var(--pixel-accent);
  top: 38px;
  right: 6px;
  transform-origin: bottom;
  border-radius: 3px 3px 0 0;
}

.dog-tail.wag {
  animation: tail-wag 0.3s ease-in-out infinite alternate;
}

@keyframes tail-wag {
  0% { transform: rotate(-15deg); }
  100% { transform: rotate(15deg); }
}

/* 状态气泡 */
.status-bubble {
  position: absolute;
  bottom: 70px;
  right: 0;
  background: var(--bg-dark);
  border: var(--pixel-border);
  padding: 8px 12px;
  border-radius: 4px;
  white-space: nowrap;
  font-size: 10px;
  box-shadow: var(--pixel-shadow);
}

.status-bubble::after {
  content: '';
  position: absolute;
  top: 100%;
  right: 20px;
  border: 6px solid transparent;
  border-top-color: var(--pixel-primary);
}

.status-bubble.success {
  border-color: var(--pixel-success);
  color: var(--pixel-success);
  box-shadow: 0 0 10px var(--pixel-success);
}

.status-bubble.warning {
  border-color: var(--pixel-warning);
  color: var(--pixel-warning);
  box-shadow: 0 0 10px var(--pixel-warning);
}

.status-bubble.error {
  border-color: var(--pixel-danger);
  color: var(--pixel-danger);
  box-shadow: 0 0 10px var(--pixel-danger);
}

.status-bubble.info {
  border-color: var(--pixel-accent);
  color: var(--pixel-accent);
  box-shadow: 0 0 10px var(--pixel-accent);
}

/* 切换按钮 */
.pet-switch {
  position: absolute;
  top: -40px;
  right: 0;
  width: 32px;
  height: 32px;
  padding: 4px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 动画状态 */
.alert {
  animation: alert-bounce 0.5s ease infinite alternate;
}

.happy {
  animation: happy-wiggle 0.3s ease infinite alternate;
}

.sad {
  animation: sad-droop 1s ease infinite alternate;
}

@keyframes alert-bounce {
  0% { transform: translateY(0); }
  100% { transform: translateY(-5px); }
}

@keyframes happy-wiggle {
  0% { transform: rotate(-2deg); }
  100% { transform: rotate(2deg); }
}

@keyframes sad-droop {
  0% { transform: translateY(0); }
  100% { transform: translateY(3px); }
}

/* 浮动动画 */
.floating {
  animation: pixelFloat 3s ease-in-out infinite;
}

@keyframes pixelFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

/* 粒子容器 */
.particle-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: visible;
}

/* 主题粒子动画 */
@keyframes themeParticleFloat {
  0% {
    opacity: 0;
    transform: translateY(0) scale(0);
  }
  10% {
    opacity: 1;
    transform: translateY(-5px) scale(1);
  }
  90% {
    opacity: 1;
    transform: translateY(-30px) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-40px) scale(0);
  }
}

/* 彩虹粒子动画 */
@keyframes rainbowParticle {
  0% {
    opacity: 0;
    transform: translateY(0) scale(0) rotate(0deg);
  }
  20% {
    opacity: 1;
    transform: translateY(-10px) scale(1) rotate(90deg);
  }
  80% {
    opacity: 1;
    transform: translateY(-50px) scale(1.2) rotate(270deg);
  }
  100% {
    opacity: 0;
    transform: translateY(-70px) scale(0) rotate(360deg);
  }
}

/* 连击指示器 */
.combo-indicator {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--neon-orange);
  color: var(--bg-dark);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 8px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  animation: comboPopup 0.5s ease-out;
  box-shadow: 0 0 10px var(--neon-orange);
}

@keyframes comboPopup {
  0% {
    opacity: 0;
    transform: translateX(-50%) scale(0.5);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) scale(1.2);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) scale(1);
  }
}

/* 工作模式切换按钮 */
.work-toggle {
  position: absolute;
  bottom: -15px;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 24px;
  padding: 4px;
  font-size: 10px;
  border: 1px solid var(--pixel-accent);
  background: var(--bg-darker);
  color: var(--pixel-accent);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.work-toggle:hover {
  background: var(--pixel-accent);
  color: var(--bg-dark);
  box-shadow: 0 0 10px var(--pixel-accent);
  transform: translateX(-50%) scale(1.1);
}

/* 超级连击动画 */
.animation-super-combo {
  animation: superCombo 2s ease-out;
}

@keyframes superCombo {
  0%, 100% { 
    transform: scale(1) rotate(0deg); 
    filter: hue-rotate(0deg);
  }
  25% { 
    transform: scale(1.2) rotate(90deg); 
    filter: hue-rotate(90deg);
  }
  50% { 
    transform: scale(1.3) rotate(180deg); 
    filter: hue-rotate(180deg);
  }
  75% { 
    transform: scale(1.2) rotate(270deg); 
    filter: hue-rotate(270deg);
  }
}

/* 主题切换动画 */
.animation-theme-switch {
  animation: themeSwitch 0.6s ease-in-out;
}

@keyframes themeSwitch {
  0% { 
    transform: rotateY(0deg); 
    filter: brightness(1);
  }
  50% { 
    transform: rotateY(90deg); 
    filter: brightness(1.5);
  }
  100% { 
    transform: rotateY(0deg); 
    filter: brightness(1);
  }
}

/* 工作模式动画增强 */
.animation-working {
  animation: workingMode 2s ease-in-out infinite;
  position: relative;
}

@keyframes workingMode {
  0%, 100% { 
    transform: scale(1);
    filter: brightness(1);
  }
  50% { 
    transform: scale(1.05);
    filter: brightness(1.2) hue-rotate(30deg);
  }
}

.animation-working::after {
  content: '💻';
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  animation: workIcon 1s ease-in-out infinite;
}

@keyframes workIcon {
  0%, 100% { opacity: 0.6; transform: translateX(-50%) translateY(0); }
  50% { opacity: 1; transform: translateX(-50%) translateY(-3px); }
}

/* 兴奋状态增强 */
.animation-excited {
  animation: excitedBounce 0.6s ease-in-out infinite;
}

@keyframes excitedBounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-8px) scale(1.1); }
}

/* 警戒状态 */
.animation-alert {
  animation: alertPulse 1s ease-in-out infinite;
}

@keyframes alertPulse {
  0%, 100% { 
    transform: scale(1);
    filter: brightness(1);
    box-shadow: 0 0 0 rgba(255, 255, 0, 0);
  }
  50% { 
    transform: scale(1.05);
    filter: brightness(1.3);
    box-shadow: 0 0 20px rgba(255, 255, 0, 0.5);
  }
}

/* 悲伤状态 */
.animation-sad {
  animation: sadSway 2s ease-in-out infinite;
  filter: saturate(0.5);
}

@keyframes sadSway {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-2deg); }
  75% { transform: rotate(2deg); }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .pixel-pet {
    width: 48px;
    height: 48px;
  }
  
  .work-toggle {
    width: 28px;
    height: 20px;
    font-size: 8px;
  }
  
  .combo-indicator {
    font-size: 7px;
    padding: 2px 6px;
  }
}

@media (max-width: 480px) {
  .pixel-pet {
    width: 40px;
    height: 40px;
  }
  
  .pet-switch {
    width: 20px;
    height: 16px;
    font-size: 8px;
  }
}

/* Ming彩蛋特殊动画 */
@keyframes mingParticleFloat {
  0% {
    opacity: 0;
    transform: translate(0, 0) scale(0);
  }
  10% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(var(--random-x, 20px), var(--random-y, -30px)) scale(1.2);
  }
  100% {
    opacity: 0;
    transform: translate(var(--random-x, 40px), var(--random-y, -60px)) scale(0.5);
  }
}

.ming-special-particle {
  --random-x: calc((var(--i, 0) % 3 - 1) * 40px);
  --random-y: calc(-50px - (var(--i, 0) % 2) * 20px);
}

/* Ming彩蛋触发状态动画 */
.ming-easter-egg-triggered {
  animation: mingEasterEggPulse 1s ease-in-out 3;
  filter: hue-rotate(180deg) brightness(1.3);
}

@keyframes mingEasterEggPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(255, 20, 147, 0);
  }
  50% {
    transform: scale(1.15);
    box-shadow: 0 0 30px rgba(255, 20, 147, 0.8), 0 0 60px rgba(0, 255, 150, 0.4);
  }
}

/* Ming彩蛋暗示效果 */
.ming-hint-glow {
  animation: mingHintGlow 2s ease-in-out infinite;
}

@keyframes mingHintGlow {
  0%, 100% {
    filter: brightness(1);
    box-shadow: 0 0 0 rgba(255, 215, 0, 0);
  }
  50% {
    filter: brightness(1.2);
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
  }
}
</style> 