<!--
---------------------------------------------------------------
File name:                  AnimationSettings.vue
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                动画设置和性能控制组件
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，动画舒适度控制;
----
-->

<template>
  <div class="animation-settings">
    <!-- 动画强度设置 -->
    <el-card class="setting-card">
      <template #header>
        <div class="card-header">
          <el-icon><VideoPlay /></el-icon>
          <span>动画强度</span>
        </div>
      </template>
      
      <div class="intensity-section">
        <el-radio-group 
          v-model="animationStore.settings.intensity" 
          @change="handleIntensityChange"
          class="intensity-group"
        >
          <el-radio value="none" class="intensity-option">
            <div class="option-content">
              <div class="option-title">关闭动画</div>
              <div class="option-desc">完全禁用所有动画效果</div>
            </div>
          </el-radio>
          
          <el-radio value="reduced" class="intensity-option">
            <div class="option-content">
              <div class="option-title">减弱动画</div>
              <div class="option-desc">简化动画，适合敏感用户</div>
            </div>
          </el-radio>
          
          <el-radio value="normal" class="intensity-option">
            <div class="option-content">
              <div class="option-title">标准动画</div>
              <div class="option-desc">平衡的动画体验</div>
            </div>
          </el-radio>
          
          <el-radio value="enhanced" class="intensity-option">
            <div class="option-content">
              <div class="option-title">增强动画</div>
              <div class="option-desc">丰富的动画效果</div>
            </div>
          </el-radio>
        </el-radio-group>
        
        <div class="intensity-preview">
          <div 
            class="preview-box"
            :class="`intensity-${animationStore.effectiveIntensity}`"
            @click="triggerPreview"
          >
            <div class="preview-content">
              <el-icon><Star /></el-icon>
              <span>点击预览效果</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 动画类型控制 -->
    <el-card class="setting-card">
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>动画类型</span>
        </div>
      </template>
      
      <div class="animation-types">
        <div 
          v-for="(enabled, type) in animationStore.settings.enabledTypes" 
          :key="type"
          class="type-item"
        >
          <div class="type-info">
            <div class="type-name">{{ getTypeName(type) }}</div>
            <div class="type-duration">
              {{ animationStore.getAnimationDuration(type as any) }}ms
            </div>
          </div>
          
          <el-switch
            :model-value="enabled"
            @change="(value: boolean) => toggleAnimationType(type as any, value)"
            :disabled="animationStore.shouldDisableAnimations"
          />
        </div>
      </div>
    </el-card>

    <!-- 性能设置 -->
    <el-card class="setting-card">
      <template #header>
        <div class="card-header">
          <el-icon><Monitor /></el-icon>
          <span>性能控制</span>
        </div>
      </template>
      
      <div class="performance-settings">
        <div class="setting-item">
          <div class="setting-label">
            <span>GPU加速</span>
            <el-tooltip content="启用硬件加速提升动画性能">
              <el-icon><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-switch
            v-model="animationStore.settings.enableGPUAcceleration"
            @change="saveSettings"
          />
        </div>
        
        <div class="setting-item">
          <div class="setting-label">
            <span>性能模式</span>
            <el-tooltip content="自动优化动画以保持流畅性">
              <el-icon><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-switch
            v-model="animationStore.settings.performanceMode"
            @change="saveSettings"
          />
        </div>
        
        <div class="setting-item">
          <div class="setting-label">
            <span>遵循系统偏好</span>
            <el-tooltip content="自动检测系统的动画偏好设置">
              <el-icon><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-switch
            v-model="animationStore.settings.respectMotionPreference"
            @change="saveSettings"
          />
        </div>
        
        <div class="setting-item">
          <div class="setting-label">
            <span>最大并发动画</span>
          </div>
          <el-input-number
            v-model="animationStore.settings.maxConcurrentAnimations"
            :min="1"
            :max="20"
            @change="saveSettings"
            class="concurrent-input"
          />
        </div>
      </div>
    </el-card>

    <!-- 性能监控 -->
    <el-card class="setting-card">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>性能监控</span>
          <el-button 
            type="text" 
            size="small" 
            @click="resetStats"
            class="reset-btn"
          >
            重置统计
          </el-button>
        </div>
      </template>
      
      <div class="performance-stats">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ Math.round(animationStore.performanceStats.averageFPS) }}</div>
            <div class="stat-label">平均FPS</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ animationStore.performanceStats.totalAnimations }}</div>
            <div class="stat-label">总动画数</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ animationStore.activeAnimationCount }}</div>
            <div class="stat-label">活跃动画</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ animationStore.performanceStats.droppedFrames }}</div>
            <div class="stat-label">掉帧数</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ formatMemory(animationStore.performanceStats.memoryUsage) }}</div>
            <div class="stat-label">内存使用</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ animationStore.performanceStats.gpuAcceleratedCount }}</div>
            <div class="stat-label">GPU加速</div>
          </div>
        </div>
        
        <!-- 性能建议 -->
        <div v-if="performanceReport.recommendations.length > 0" class="recommendations">
          <div class="recommendations-title">
            <el-icon><Warning /></el-icon>
            <span>性能建议</span>
          </div>
          <ul class="recommendations-list">
            <li v-for="rec in performanceReport.recommendations" :key="rec">
              {{ rec }}
            </li>
          </ul>
        </div>
      </div>
    </el-card>

    <!-- 测试区域 -->
    <el-card class="setting-card">
      <template #header>
        <div class="card-header">
          <el-icon><Tools /></el-icon>
          <span>动画测试</span>
        </div>
      </template>
      
      <div class="test-section">
        <div class="test-buttons">
          <el-button @click="testAnimation('bounce')" type="primary">
            弹跳测试
          </el-button>
          <el-button @click="testAnimation('glow')" type="success">
            发光测试
          </el-button>
          <el-button @click="testAnimation('glitch')" type="warning">
            故障测试
          </el-button>
          <el-button @click="testAnimation('particle')" type="info">
            粒子测试
          </el-button>
        </div>
        
        <div class="test-area" ref="testArea">
          <div class="test-element" ref="testElement">
            <el-icon><Star /></el-icon>
            <span>测试元素</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  VideoPlay, 
  Setting, 
  Monitor, 
  DataAnalysis, 
  QuestionFilled, 
  Warning, 
  Tools,
  Star
} from '@element-plus/icons-vue'
import { useAnimationStore, type AnimationType } from '../../stores/animation'
import { AnimationOptimizer } from '../../utils/animationProfiler'

// Store
const animationStore = useAnimationStore()

// 引用
const testArea = ref<HTMLElement>()
const testElement = ref<HTMLElement>()

// 计算属性
const performanceReport = computed(() => animationStore.getPerformanceReport())

// 动画类型名称映射
const typeNames: Record<AnimationType, string> = {
  transition: '过渡动画',
  transform: '变换动画',
  opacity: '透明度',
  scale: '缩放动画',
  rotate: '旋转动画',
  translate: '位移动画',
  particle: '粒子效果',
  glow: '发光效果',
  glitch: '故障效果'
}

// 方法

/**
 * 获取动画类型名称
 */
const getTypeName = (type: string): string => {
  return typeNames[type as AnimationType] || type
}

/**
 * 处理强度变化
 */
const handleIntensityChange = (intensity: string): void => {
  animationStore.setIntensity(intensity as any)
  
  // 播放音效反馈
  if ((window as any).audioManager) {
    (window as any).audioManager.playSound('click')
  }
}

/**
 * 切换动画类型
 */
const toggleAnimationType = (type: AnimationType, enabled: boolean): void => {
  animationStore.toggleAnimationType(type, enabled)
  
  // 播放音效反馈
  if ((window as any).audioManager) {
    (window as any).audioManager.playSound(enabled ? 'success' : 'click')
  }
}

/**
 * 保存设置
 */
const saveSettings = (): void => {
  // 设置会自动保存，这里只需要播放反馈音效
  if ((window as any).audioManager) {
    (window as any).audioManager.playSound('click')
  }
}

/**
 * 重置统计
 */
const resetStats = (): void => {
  animationStore.resetPerformanceStats()
  
  if ((window as any).audioManager) {
    (window as any).audioManager.playSound('notification')
  }
}

/**
 * 格式化内存显示
 */
const formatMemory = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

/**
 * 触发预览效果
 */
const triggerPreview = (): void => {
  const element = document.querySelector('.preview-box') as HTMLElement
  if (!element) return
  
  const animationName = `preview-${Date.now()}`
  animationStore.startAnimationMonitoring(animationName, element)
  
  // 添加预览动画类
  element.classList.add('preview-active')
  
  setTimeout(() => {
    element.classList.remove('preview-active')
    animationStore.stopAnimationMonitoring(animationName)
  }, 1000)
  
  if ((window as any).audioManager) {
    (window as any).audioManager.playSound('hover')
  }
}

/**
 * 测试动画
 */
const testAnimation = (type: string): void => {
  if (!testElement.value) return
  
  const element = testElement.value
  const animationName = `test-${type}-${Date.now()}`
  
  // 开始监控
  animationStore.startAnimationMonitoring(animationName, element)
  
  // 启用GPU加速
  AnimationOptimizer.enableGPUAcceleration(element)
  
  // 添加测试动画类
  element.classList.add(`test-${type}`)
  
  // 创建动画
  let animation: Animation
  
  switch (type) {
    case 'bounce':
      animation = element.animate([
        { transform: 'translateY(0) scale(1)' },
        { transform: 'translateY(-20px) scale(1.1)' },
        { transform: 'translateY(0) scale(1)' }
      ], {
        duration: animationStore.getAnimationDuration('transform'),
        easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
      })
      break
      
    case 'glow':
      animation = element.animate([
        { boxShadow: '0 0 5px var(--primary-color)' },
        { boxShadow: '0 0 20px var(--primary-color), 0 0 30px var(--primary-color)' },
        { boxShadow: '0 0 5px var(--primary-color)' }
      ], {
        duration: animationStore.getAnimationDuration('glow'),
        easing: 'ease-in-out'
      })
      break
      
    case 'glitch':
      animation = element.animate([
        { transform: 'translateX(0)', filter: 'hue-rotate(0deg)' },
        { transform: 'translateX(-2px)', filter: 'hue-rotate(90deg)' },
        { transform: 'translateX(2px)', filter: 'hue-rotate(180deg)' },
        { transform: 'translateX(-1px)', filter: 'hue-rotate(270deg)' },
        { transform: 'translateX(0)', filter: 'hue-rotate(360deg)' }
      ], {
        duration: animationStore.getAnimationDuration('glitch'),
        easing: 'steps(5, end)'
      })
      break
      
    case 'particle':
      // 创建粒子效果
      createParticleEffect(element)
      animation = element.animate([
        { transform: 'scale(1) rotate(0deg)' },
        { transform: 'scale(1.2) rotate(180deg)' },
        { transform: 'scale(1) rotate(360deg)' }
      ], {
        duration: animationStore.getAnimationDuration('particle'),
        easing: 'ease-in-out'
      })
      break
      
    default:
      animation = element.animate([
        { opacity: 1 },
        { opacity: 0.5 },
        { opacity: 1 }
      ], {
        duration: animationStore.getAnimationDuration('opacity'),
        easing: 'ease-in-out'
      })
  }
  
  // 动画完成后清理
  animation.addEventListener('finish', () => {
    element.classList.remove(`test-${type}`)
    animationStore.stopAnimationMonitoring(animationName)
  })
  
  if ((window as any).audioManager) {
    (window as any).audioManager.playSound('notification')
  }
}

/**
 * 创建粒子效果
 */
const createParticleEffect = (element: HTMLElement): void => {
  const rect = element.getBoundingClientRect()
  const container = testArea.value
  if (!container) return
  
  for (let i = 0; i < 10; i++) {
    const particle = document.createElement('div')
    particle.className = 'particle'
    particle.style.cssText = `
      position: absolute;
      width: 4px;
      height: 4px;
      background: var(--primary-color);
      border-radius: 50%;
      pointer-events: none;
      left: ${rect.left + rect.width / 2}px;
      top: ${rect.top + rect.height / 2}px;
    `
    
    container.appendChild(particle)
    
    // 粒子动画
    const angle = (i / 10) * Math.PI * 2
    const distance = 50 + Math.random() * 30
    const x = Math.cos(angle) * distance
    const y = Math.sin(angle) * distance
    
    const particleAnimation = particle.animate([
      { 
        transform: 'translate(0, 0) scale(1)',
        opacity: 1
      },
      { 
        transform: `translate(${x}px, ${y}px) scale(0)`,
        opacity: 0
      }
    ], {
      duration: 800 + Math.random() * 400,
      easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    })
    
    particleAnimation.addEventListener('finish', () => {
      particle.remove()
    })
  }
}

// 生命周期
onMounted(() => {
  // 初始化动画系统
  animationStore.initAnimationSystem()
})

onUnmounted(() => {
  // 清理资源
  if ((window as any).animationProfiler) {
    (window as any).animationProfiler.cleanup()
  }
})
</script>

<style scoped>
.animation-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-card {
  background: var(--bg-dark);
  border: 2px solid var(--primary-color);
  box-shadow: 0 0 10px var(--primary-color-alpha);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-weight: bold;
}

.reset-btn {
  margin-left: auto;
  color: var(--warning-color);
}

/* 强度设置 */
.intensity-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.intensity-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.intensity-option {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  transition: all var(--animation-duration-transition);
}

.intensity-option:hover {
  border-color: var(--primary-color);
  box-shadow: 0 0 5px var(--primary-color-alpha);
}

.option-content {
  margin-left: 25px;
}

.option-title {
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.option-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.intensity-preview {
  display: flex;
  justify-content: center;
}

.preview-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  cursor: pointer;
  transition: all var(--animation-duration-transform);
}

.preview-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px var(--primary-color-alpha);
}

.preview-box.preview-active {
  animation: preview-pulse 1s ease-in-out;
}

@keyframes preview-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* 动画类型 */
.animation-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.type-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
}

.type-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.type-name {
  font-weight: 500;
  color: var(--text-primary);
}

.type-duration {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 性能设置 */
.performance-settings {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
}

.concurrent-input {
  width: 120px;
}

/* 性能统计 */
.performance-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.recommendations {
  padding: 15px;
  border: 1px solid var(--warning-color);
  border-radius: 6px;
  background: var(--warning-color-alpha);
}

.recommendations-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--warning-color);
  font-weight: bold;
  margin-bottom: 10px;
}

.recommendations-list {
  margin: 0;
  padding-left: 20px;
  color: var(--text-primary);
}

.recommendations-list li {
  margin-bottom: 5px;
}

/* 测试区域 */
.test-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.test-area {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  overflow: hidden;
}

.test-element {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 15px 20px;
  border: 2px solid var(--primary-color);
  border-radius: 6px;
  background: var(--bg-dark);
  color: var(--primary-color);
  font-weight: bold;
  cursor: pointer;
}

.particle {
  z-index: 10;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .intensity-group {
    grid-template-columns: 1fr;
  }
  
  .animation-types {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .test-buttons {
    justify-content: center;
  }
}

/* GPU加速优化 */
.gpu-acceleration-enabled .preview-box,
.gpu-acceleration-enabled .test-element {
  will-change: transform;
  backface-visibility: hidden;
}

/* 性能模式优化 */
.performance-mode .preview-box,
.performance-mode .test-element {
  transition-duration: 0.1s;
}

/* 动画强度适配 */
.animation-none * {
  animation-duration: 0s !important;
  transition-duration: 0s !important;
}

.animation-reduced * {
  animation-duration: 0.5s;
  transition-duration: 0.15s;
}

.animation-enhanced * {
  animation-duration: 1.5s;
  transition-duration: 0.45s;
}
</style> 