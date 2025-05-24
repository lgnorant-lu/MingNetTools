<!--
---------------------------------------------------------------
File name:                  MingEasterEgg.vue
Author:                     Ming (鹿鸣)
Date created:               2025/05/24
Description:                Ming的神秘彩蛋显示组件
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，彩蛋动画显示系统;
----
-->

<template>
  <Teleport to="body">
    <Transition 
      name="ming-easter-egg" 
      @enter="onEnter" 
      @leave="onLeave"
    >
      <div 
        v-if="isVisible" 
        class="ming-easter-egg-overlay"
        @click="handleOverlayClick"
      >
        <!-- 主要动画区域 -->
        <div class="ming-gift-container">
          <!-- 文字版本彩蛋 (当GIF不存在时) -->
          <div v-if="showTextVersion" class="ming-text-animation">
            <div class="ascii-art" :class="animationTypeText">
              <pre>{{ currentAsciiArt }}</pre>
            </div>
            <div class="animation-text">
              {{ animationDescription }}
            </div>
          </div>
          
          <!-- 原始GIF动画 -->
          <img 
            v-else
            :src="currentAnimationSrc"
            :alt="`Ming的${animationTypeText}动画`"
            class="ming-gift-animation"
            @load="handleAnimationLoad"
            @error="handleAnimationError"
          />
          
          <!-- 消息显示 -->
          <div 
            v-if="showMessage && currentMessage"
            class="ming-message"
            :class="messageClass"
          >
            {{ currentMessage }}
          </div>
          
          <!-- 开发者徽章 -->
          <div 
            v-if="showBadge"
            class="ming-badge-container"
          >
            <img 
              :src="badgeSrc"
              alt="Ming的开发者令牌"
              class="ming-developer-badge"
            />
            <div class="badge-text">
              ✨ Created with ❤️ by Ming (鹿鸣) ✨
            </div>
          </div>
          
          <!-- 统计信息 -->
          <div class="ming-stats" v-if="showStats">
            <div class="stat-item">
              <span class="stat-icon">🎁</span>
              <span class="stat-text">第 {{ triggerCount }} 次发现</span>
            </div>
            <div class="stat-item" v-if="achievementCount > 0">
              <span class="stat-icon">🏆</span>
              <span class="stat-text">{{ achievementCount }} 个成就</span>
            </div>
          </div>
          
          <!-- 关闭按钮 -->
          <button 
            class="ming-close-btn"
            @click="closeEasterEgg"
            :aria-label="'关闭Ming的彩蛋'"
          >
            <span class="close-icon">×</span>
          </button>
        </div>
        
        <!-- 粒子效果背景 -->
        <div class="ming-particles" ref="particleContainer">
          <div 
            v-for="(particle, index) in particles"
            :key="`particle-${index}`"
            class="particle"
            :style="particle.style"
          ></div>
        </div>
        
        <!-- 二次动画（连续播放） -->
        <div 
          v-if="shouldPlayDouble && doubleAnimationSrc"
          class="ming-double-animation"
        >
          <img 
            :src="doubleAnimationSrc"
            alt="Ming的连续动画"
            class="ming-gift-animation secondary"
          />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { MingAnimationType, type MingAchievement } from '../../utils/mingEasterEgg'

// Props
interface Props {
  visible?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: false
})

// Emits
const emit = defineEmits<{
  close: []
  animationComplete: []
}>()

// 状态管理
const isVisible = ref(false)
const currentAnimation = ref<MingAnimationType>(MingAnimationType.DIRECT)
const showMessage = ref(false)
const showBadge = ref(false)
const showStats = ref(true)
const shouldPlayDouble = ref(false)
const currentMessage = ref('')
const triggerCount = ref(0)
const achievementCount = ref(0)
const animationLoaded = ref(false)
const showTextVersion = ref(true) // 默认显示文字版本

// 文字版本相关状态
const currentAsciiArt = ref('')
const animationDescription = ref('')

// ASCII艺术库 (优化版)
const asciiArts = {
  escape: `
      嗖 ε=ε=┌( >ヮ<)┘ ✨
     ↗        ↖
    🧱       🧱  ← "冲啊！自由就在前方！"
     ↘        ↙
      💨💨💨💨
  `, // 小猫咪快速奔跑，背景是象征障碍或出口的砖块/通道
  return: `
    🏠🐾 ~~~~~~
    │ ^_^ │ z Z
    │( >ω< )│  ← "还是家里最舒服啦～喵"
    └───💖──┘
  `, // 小猫咪在舒适的家里，满足地打着小呼噜
  direct: `
    ┌───────┐
    │  ^ ^  │  ← "是谁在呼唤我？"
    │ (๑• . •๑)│  (小猫咪好奇探头)
    │  ╲   ╱  │
    └─═──═─┘
  `  // 小猫咪从某个边缘或洞口小心翼翼探出脑袋
}

// 动画描述库 (优化版)
const animationDescriptions = {
  escape: "💨💨💨 小猫咪像一道闪电，开启了它的越狱大冒险，目标是远方的自由！",
  return: "🏡 兜兜转转，小猫咪终于回到了它温馨的小窝，蹭了蹭熟悉的毯子，发出了满足的呼噜声。",
  direct: "👀 喵？ 一只好奇的小猫咪从它的神秘角落悄悄探出了毛茸茸的小脑袋，想看看发生了什么趣事。"
}

// 粒子效果
const particleContainer = ref<HTMLElement>()
const particles = ref<Array<{ style: string }>>([])

// 计算属性
const currentAnimationSrc = computed(() => {
  const baseUrl = '/assets/ming/secrets/'
  switch (currentAnimation.value) {
    case MingAnimationType.ESCAPE:
      return `${baseUrl}box-escape-adventure.gif`
    case MingAnimationType.RETURN:
      return `${baseUrl}box-return-home.gif`
    case MingAnimationType.DIRECT:
      return `${baseUrl}box-shy-drop.gif`
    default:
      return `${baseUrl}box-shy-drop.gif`
  }
})

const doubleAnimationSrc = computed(() => {
  // 连续播放时选择不同的动画
  const animations = [MingAnimationType.ESCAPE, MingAnimationType.RETURN, MingAnimationType.DIRECT]
  const differentAnimation = animations.find(type => type !== currentAnimation.value) || MingAnimationType.ESCAPE
  
  const baseUrl = '/assets/ming/secrets/'
  switch (differentAnimation) {
    case MingAnimationType.ESCAPE:
      return `${baseUrl}box-escape-adventure.gif`
    case MingAnimationType.RETURN:
      return `${baseUrl}box-return-home.gif`
    case MingAnimationType.DIRECT:
      return `${baseUrl}box-shy-drop.gif`
    default:
      return `${baseUrl}box-escape-adventure.gif`
  }
})

const badgeSrc = computed(() => '/assets/ming/secrets/developer-token.png')

const animationTypeText = computed(() => {
  switch (currentAnimation.value) {
    case MingAnimationType.ESCAPE:
      return '逃脱冒险'
    case MingAnimationType.RETURN:
      return '温馨回家'
    case MingAnimationType.DIRECT:
      return '害羞直降'
    default:
      return '神秘'
  }
})

const messageClass = computed(() => {
  return {
    'special-time': isSpecialTime(),
    'achievement-unlock': showBadge.value
  }
})

// 方法

/**
 * 显示彩蛋
 */
const showEasterEgg = (eventDetail: any) => {
  currentAnimation.value = eventDetail.animationType
  shouldPlayDouble.value = eventDetail.shouldDouble
  showBadge.value = eventDetail.showBadge
  showMessage.value = eventDetail.showMessage
  triggerCount.value = eventDetail.triggerCount
  
  // 设置文字版本内容
  const animType = eventDetail.animationType as MingAnimationType
  currentAsciiArt.value = asciiArts[animType] || asciiArts.direct
  animationDescription.value = animationDescriptions[animType] || animationDescriptions.direct
  
  // 设置消息
  if (eventDetail.showMessage) {
    currentMessage.value = generateMessage()
  }
  
  // 创建粒子效果
  createParticles()
  
  // 显示彩蛋
  isVisible.value = true
  
  // 设置自动关闭（如果没有特殊事件）
  if (!shouldPlayDouble.value && !showBadge.value) {
    setTimeout(() => {
      closeEasterEgg()
    }, 5000)
  }
}

/**
 * 关闭彩蛋
 */
const closeEasterEgg = () => {
  isVisible.value = false
  resetState()
  emit('close')
}

/**
 * 重置状态
 */
const resetState = () => {
  showMessage.value = false
  showBadge.value = false
  shouldPlayDouble.value = false
  currentMessage.value = ''
  animationLoaded.value = false
  particles.value = []
}

/**
 * 生成消息文本
 */
const generateMessage = (): string => {
  const now = new Date()
  const hour = now.getHours()
  const timeString = `${hour.toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  // 时间特殊消息
  const timeMessages: { [key: string]: string } = {
    '12:34': '🕐 时间魔法！Ming在12:34向你问好！',
    '23:33': '🌙 深夜惊喜！小猫咪在月光下向你招手～',
    '00:00': '🌟 新的一天开始了！Ming的祝福伴随着你！'
  }
  
  if (timeMessages[timeString]) {
    return timeMessages[timeString]
  }
  
  // 时间段消息
  if (hour >= 22 || hour <= 6) {
    return `🌃 深夜冒险时光！小猫咪要开始${animationTypeText.value}的表演了～`
  } else if (hour >= 18) {
    return `🏠 温馨黄昏！小猫咪想要回到温暖的家～`
  } else if (hour >= 12) {
    return `☀️ 午后时光！害羞的小猫咪悄悄探出头来～`
  } else {
    return `🌅 美好的早晨！跟着小猫咪一起开始新的一天吧！`
  }
}

/**
 * 检查是否为特殊时间
 */
const isSpecialTime = (): boolean => {
  const now = new Date()
  const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  return ['12:34', '23:33', '00:00'].includes(timeString)
}

/**
 * 创建粒子效果
 */
const createParticles = () => {
  particles.value = []
  
  for (let i = 0; i < 30; i++) {
    const particle = {
      style: `
        left: ${Math.random() * 100}vw;
        top: ${Math.random() * 100}vh;
        animation-delay: ${Math.random() * 3}s;
        animation-duration: ${2 + Math.random() * 4}s;
      `
    }
    particles.value.push(particle)
  }
}

/**
 * 处理覆盖层点击
 */
const handleOverlayClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    closeEasterEgg()
  }
}

/**
 * 处理动画加载完成
 */
const handleAnimationLoad = () => {
  animationLoaded.value = true
  
  // 如果需要连续播放，延迟显示第二个动画
  if (shouldPlayDouble.value) {
    setTimeout(() => {
      // 触发第二个动画的显示逻辑
      console.log('🎭 连续表演开始！')
    }, 3000)
  }
}

/**
 * 处理动画加载错误
 */
const handleAnimationError = () => {
  console.warn('Ming彩蛋GIF文件加载失败，切换到文字版本')
  
  // 切换到文字版本
  showTextVersion.value = true
  
  // 设置ASCII艺术内容
  const animType = currentAnimation.value
  currentAsciiArt.value = asciiArts[animType] || asciiArts.direct
  animationDescription.value = animationDescriptions[animType] || animationDescriptions.direct
  
  // 显示提示消息
  currentMessage.value = '🎁 Ming的神秘文字彩蛋（图片版本开发中...）'
  showMessage.value = true
}

/**
 * 处理成就解锁
 */
const handleAchievementUnlock = (event: CustomEvent<MingAchievement>) => {
  const achievement = event.detail
  achievementCount.value++
  
  // 显示成就解锁消息
  currentMessage.value = `🏆 成就解锁：${achievement.name}\n${achievement.description}`
  showMessage.value = true
  
  // 播放特殊音效
  if ((window as any).audioManager) {
    (window as any).audioManager.playSound('notification')
  }
}

/**
 * 动画进入效果
 */
const onEnter = (el: Element) => {
  const element = el as HTMLElement
  element.style.opacity = '0'
  element.style.transform = 'scale(0.8)'
  
  nextTick(() => {
    element.style.transition = 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)'
    element.style.opacity = '1'
    element.style.transform = 'scale(1)'
  })
}

/**
 * 动画离开效果
 */
const onLeave = (el: Element) => {
  const element = el as HTMLElement
  element.style.transition = 'all 0.3s ease-out'
  element.style.opacity = '0'
  element.style.transform = 'scale(0.9)'
}

// 生命周期
onMounted(() => {
  // 监听彩蛋触发事件
  window.addEventListener('ming-easter-egg', showEasterEgg as EventListener)
  
  // 监听成就解锁事件
  window.addEventListener('ming-achievement-unlocked', handleAchievementUnlock as EventListener)
  
  // 添加欢迎消息
  console.log(`
🎯 Ming的彩蛋系统已启动！
🎁 尝试多次点击页面上的元素来发现惊喜
🏆 解锁成就获得特殊奖励
✨ Created with love by Ming (鹿鸣)
  `)
})

onUnmounted(() => {
  window.removeEventListener('ming-easter-egg', showEasterEgg as EventListener)
  window.removeEventListener('ming-achievement-unlocked', handleAchievementUnlock as EventListener)
})
</script>

<style scoped>
.ming-easter-egg-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.ming-gift-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  max-width: 90vw;
  max-height: 90vh;
  z-index: 10;
}

.ming-gift-animation {
  max-width: 400px;
  max-height: 400px;
  width: auto;
  height: auto;
  border-radius: 16px;
  box-shadow: 
    0 0 30px rgba(0, 255, 150, 0.3),
    0 0 60px rgba(0, 255, 150, 0.1);
  filter: drop-shadow(0 0 20px rgba(0, 255, 150, 0.2));
}

.ming-gift-animation.secondary {
  position: absolute;
  top: -50px;
  right: -50px;
  max-width: 200px;
  max-height: 200px;
  opacity: 0.8;
  animation: float 3s ease-in-out infinite;
}

.ming-message {
  background: linear-gradient(135deg, rgba(0, 255, 150, 0.1), rgba(255, 20, 147, 0.1));
  border: 2px solid var(--primary-color);
  border-radius: 12px;
  padding: 16px 24px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
  text-align: center;
  white-space: pre-line;
  max-width: 500px;
  box-shadow: 0 0 20px var(--primary-color-alpha);
  animation: glow 2s ease-in-out infinite alternate;
}

.ming-message.special-time {
  border-color: #FFD700;
  color: #FFD700;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
  animation: special-glow 1s ease-in-out infinite alternate;
}

.ming-message.achievement-unlock {
  border-color: #FF1493;
  background: linear-gradient(135deg, rgba(255, 20, 147, 0.2), rgba(0, 255, 150, 0.1));
  animation: achievement-pulse 0.5s ease-in-out infinite alternate;
}

.ming-badge-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
}

.ming-developer-badge {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 3px solid var(--primary-color);
  box-shadow: 0 0 25px var(--primary-color-alpha);
  animation: badge-spin 4s linear infinite;
}

.badge-text {
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  animation: text-shine 2s ease-in-out infinite;
}

.ming-stats {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 255, 150, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: 20px;
  color: var(--text-primary);
  font-size: 14px;
}

.stat-icon {
  font-size: 16px;
}

.ming-close-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 40px;
  height: 40px;
  border: 2px solid var(--primary-color);
  border-radius: 50%;
  background: var(--bg-dark);
  color: var(--primary-color);
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.ming-close-btn:hover {
  background: var(--primary-color);
  color: var(--bg-dark);
  transform: scale(1.1);
  box-shadow: 0 0 15px var(--primary-color-alpha);
}

.close-icon {
  line-height: 1;
}

/* 粒子效果 */
.ming-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--primary-color);
  border-radius: 50%;
  animation: particle-float 4s linear infinite;
  opacity: 0.6;
}

.particle:nth-child(odd) {
  background: #FF1493;
}

.particle:nth-child(3n) {
  background: #00FFFF;
}

/* 动画效果 */
@keyframes glow {
  from {
    box-shadow: 0 0 20px var(--primary-color-alpha);
  }
  to {
    box-shadow: 0 0 30px var(--primary-color), 0 0 40px var(--primary-color-alpha);
  }
}

@keyframes special-glow {
  from {
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
    transform: scale(1);
  }
  to {
    box-shadow: 0 0 30px rgba(255, 215, 0, 0.5), 0 0 40px rgba(255, 215, 0, 0.2);
    transform: scale(1.02);
  }
}

@keyframes achievement-pulse {
  from {
    transform: scale(1);
    box-shadow: 0 0 20px rgba(255, 20, 147, 0.3);
  }
  to {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(255, 20, 147, 0.5);
  }
}

@keyframes badge-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes text-shine {
  from {
    text-shadow: 0 0 5px var(--primary-color);
  }
  to {
    text-shadow: 0 0 15px var(--primary-color), 0 0 25px var(--primary-color-alpha);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes particle-float {
  0% {
    opacity: 0;
    transform: translateY(100vh) scale(0);
  }
  10% {
    opacity: 0.6;
    transform: translateY(90vh) scale(1);
  }
  90% {
    opacity: 0.6;
    transform: translateY(10vh) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(0vh) scale(0);
  }
}

/* 进入/离开动画 */
.ming-easter-egg-enter-active,
.ming-easter-egg-leave-active {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.ming-easter-egg-enter-from,
.ming-easter-egg-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ming-gift-animation {
    max-width: 300px;
    max-height: 300px;
  }
  
  .ming-message {
    font-size: 14px;
    padding: 12px 18px;
    max-width: 350px;
  }
  
  .ming-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .stat-item {
    font-size: 12px;
    padding: 6px 12px;
  }
}

@media (max-width: 480px) {
  .ming-gift-animation {
    max-width: 250px;
    max-height: 250px;
  }
  
  .ming-message {
    font-size: 12px;
    padding: 10px 15px;
    max-width: 280px;
  }
  
  .ming-developer-badge {
    width: 60px;
    height: 60px;
  }
  
  .badge-text {
    font-size: 12px;
  }
}

/* 文字版本彩蛋动画 */
.ming-text-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  max-width: 400px;
  padding: 30px;
  background: linear-gradient(135deg, rgba(0, 255, 150, 0.1), rgba(255, 20, 147, 0.1));
  border: 2px solid var(--primary-color);
  border-radius: 16px;
  box-shadow: 
    0 0 30px rgba(0, 255, 150, 0.3),
    0 0 60px rgba(0, 255, 150, 0.1);
}

.ascii-art {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.2;
  color: var(--primary-color);
  text-align: center;
  white-space: pre;
  text-shadow: 0 0 10px var(--primary-color);
  animation: asciiGlow 2s ease-in-out infinite alternate;
}

.ascii-art.逃脱冒险 {
  color: #FF6600;
  text-shadow: 0 0 10px #FF6600;
  animation: escapeAnimation 1.5s ease-in-out infinite;
}

.ascii-art.温馨回家 {
  color: #FFD700;
  text-shadow: 0 0 10px #FFD700;
  animation: returnAnimation 2s ease-in-out infinite;
}

.ascii-art.害羞直降 {
  color: #FF1493;
  text-shadow: 0 0 10px #FF1493;
  animation: directAnimation 1.8s ease-in-out infinite;
}

.animation-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
  background: linear-gradient(45deg, var(--primary-color), #FF1493, #00FFFF);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: textShine 3s ease-in-out infinite;
}

/* ASCII艺术动画 */
@keyframes asciiGlow {
  from {
    filter: brightness(1);
    transform: scale(1);
  }
  to {
    filter: brightness(1.3);
    transform: scale(1.02);
  }
}

@keyframes escapeAnimation {
  0%, 100% {
    transform: translateX(0) rotate(0deg);
  }
  25% {
    transform: translateX(-3px) rotate(-1deg);
  }
  75% {
    transform: translateX(3px) rotate(1deg);
  }
}

@keyframes returnAnimation {
  0%, 100% {
    transform: scale(1);
    filter: brightness(1);
  }
  50% {
    transform: scale(1.05);
    filter: brightness(1.2);
  }
}

@keyframes directAnimation {
  0%, 100% {
    transform: translateY(0);
    opacity: 0.9;
  }
  50% {
    transform: translateY(-5px);
    opacity: 1;
  }
}

@keyframes textShine {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}
</style> 