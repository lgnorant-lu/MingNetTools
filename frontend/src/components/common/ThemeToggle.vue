<template>
  <div class="theme-toggle-container">
    <button
      @click="handleToggle"
      class="theme-toggle-btn pixel-btn"
      :class="{ 'light-mode': themeStore.currentMode === 'light' }"
      :title="themeStore.getToggleHint"
    >
      <div class="toggle-content">
        <div class="theme-icon" :class="{ 'rotating': isToggling }">
          {{ themeStore.getThemeIcon }}
        </div>
        <div class="theme-label">
          {{ themeStore.getThemeName }}
        </div>
      </div>
      
      <!-- 切换时的特效 -->
      <div v-if="isToggling" class="toggle-effect">
        <div class="particle" v-for="i in 8" :key="i" :style="getParticleStyle(i)"></div>
      </div>
    </button>
    
    <!-- 可选的详细主题选择器 -->
    <div v-if="showDetailedSelector" class="theme-selector pixel-card">
      <div class="selector-header">
        <span class="glitch-text" data-text="THEME SELECTOR">THEME SELECTOR</span>
      </div>
      
      <div class="theme-options">
        <div 
          class="theme-option"
          :class="{ active: themeStore.currentMode === 'dark' }"
          @click="setTheme('dark')"
        >
          <div class="option-preview dark-preview">
            <div class="preview-bg"></div>
            <div class="preview-elements">
              <div class="preview-dot green"></div>
              <div class="preview-dot cyan"></div>
              <div class="preview-dot pink"></div>
            </div>
          </div>
          <div class="option-info">
            <div class="option-title">🌙 赛博夜晚</div>
            <div class="option-desc">经典霓虹赛博朋克风格</div>
          </div>
        </div>
        
        <div 
          class="theme-option"
          :class="{ active: themeStore.currentMode === 'light' }"
          @click="setTheme('light')"
        >
          <div class="option-preview light-preview">
            <div class="preview-bg"></div>
            <div class="preview-elements">
              <div class="preview-dot blue"></div>
              <div class="preview-dot teal"></div>
              <div class="preview-dot emerald"></div>
            </div>
          </div>
          <div class="option-info">
            <div class="option-title">☀️ 马卡白</div>
            <div class="option-desc">优雅深色马卡龙配色</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useThemeStore, type ThemeMode } from '../../stores/theme'

// Props
interface Props {
  showDetailedSelector?: boolean
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
}

const props = withDefaults(defineProps<Props>(), {
  showDetailedSelector: false,
  position: 'top-right'
})

// Store
const themeStore = useThemeStore()

// 状态
const isToggling = ref(false)

// 处理主题切换
const handleToggle = async () => {
  if (isToggling.value) return
  
  isToggling.value = true
  
  // 添加切换动画
  themeStore.toggleTheme()
  
  // 发送系统状态变化事件给桌宠
  window.dispatchEvent(new CustomEvent('system-status-change', {
    detail: { 
      status: 'theme-switch',
      theme: themeStore.currentMode 
    }
  }))
  
  // 延迟重置动画状态
  setTimeout(() => {
    isToggling.value = false
  }, 800)
}

// 设置特定主题
const setTheme = (mode: ThemeMode) => {
  if (themeStore.currentMode === mode) return
  
  isToggling.value = true
  themeStore.setTheme(mode)
  
  window.dispatchEvent(new CustomEvent('system-status-change', {
    detail: { 
      status: 'theme-switch',
      theme: mode
    }
  }))
  
  setTimeout(() => {
    isToggling.value = false
  }, 800)
}

// 获取粒子样式
const getParticleStyle = (index: number) => {
  const angle = (index * 45) // 每个粒子相隔45度
  const distance = 30 + Math.random() * 20 // 随机距离
  const delay = index * 0.1 // 延迟时间
  
  return {
    '--angle': `${angle}deg`,
    '--distance': `${distance}px`,
    '--delay': `${delay}s`,
    animationDelay: `${delay}s`
  }
}

// 快捷键支持
const handleKeydown = (event: KeyboardEvent) => {
  // Ctrl/Cmd + Shift + T 切换主题
  if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'T') {
    event.preventDefault()
    handleToggle()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.theme-toggle-container {
  position: relative;
  z-index: 1000;
}

/* 主题切换按钮 */
.theme-toggle-btn {
  position: relative;
  padding: 12px 16px;
  background: var(--bg-darker);
  border: 2px solid var(--pixel-primary);
  color: var(--pixel-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  min-width: 160px;
}

.theme-toggle-btn:hover {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  box-shadow: 0 0 20px var(--pixel-primary);
  transform: translateY(-2px);
}

.theme-toggle-btn.light-mode {
  border-color: var(--pixel-accent);
  box-shadow: 0 0 15px rgba(8, 145, 178, 0.3);
}

.theme-toggle-btn.light-mode:hover {
  background: var(--pixel-accent);
  box-shadow: 0 0 25px var(--pixel-accent);
}

.toggle-content {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 2;
}

.theme-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.theme-icon.rotating {
  animation: themeRotate 0.8s ease-in-out;
}

.theme-label {
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 切换特效 */
.toggle-effect {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--pixel-primary);
  border-radius: 50%;
  animation: particleExplosion 0.8s ease-out forwards;
}

@keyframes themeRotate {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.2); }
  100% { transform: rotate(360deg) scale(1); }
}

@keyframes particleExplosion {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  100% {
    transform: 
      translateX(calc(cos(var(--angle)) * var(--distance)))
      translateY(calc(sin(var(--angle)) * var(--distance)))
      scale(0);
    opacity: 0;
  }
}

/* 详细主题选择器 */
.theme-selector {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  min-width: 300px;
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--pixel-shadow);
  animation: selectorSlideIn 0.3s ease;
}

.selector-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--pixel-primary);
  font-size: 14px;
  text-align: center;
  color: var(--pixel-primary);
}

.theme-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-dark);
}

.theme-option:hover {
  border-color: var(--pixel-primary);
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
  transform: translateX(4px);
}

.theme-option.active {
  border-color: var(--pixel-accent);
  background: rgba(0, 212, 255, 0.1);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

/* 主题预览 */
.option-preview {
  width: 48px;
  height: 32px;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--pixel-primary);
}

.preview-bg {
  width: 100%;
  height: 100%;
  transition: background 0.3s ease;
}

.dark-preview .preview-bg {
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
}

.light-preview .preview-bg {
  background: linear-gradient(135deg, #f0fdfa 0%, #e6fffa 100%);
}

.preview-elements {
  position: absolute;
  top: 4px;
  left: 4px;
  display: flex;
  gap: 3px;
}

.preview-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: previewPulse 2s infinite;
}

.preview-dot.green { background: #00ff41; }
.preview-dot.cyan { background: #00ffff; }
.preview-dot.pink { background: #ff00ff; }
.preview-dot.blue { background: #1a365d; }
.preview-dot.teal { background: #0891b2; }
.preview-dot.emerald { background: #047857; }

.option-info {
  flex: 1;
}

.option-title {
  font-size: 12px;
  font-weight: bold;
  color: var(--pixel-primary);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.option-desc {
  font-size: 10px;
  color: var(--pixel-accent);
  opacity: 0.8;
}

@keyframes selectorSlideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes previewPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.8); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-toggle-btn {
    min-width: 120px;
    padding: 10px 12px;
  }
  
  .theme-label {
    font-size: 10px;
  }
  
  .theme-icon {
    font-size: 16px;
  }
  
  .theme-selector {
    min-width: 250px;
    right: auto;
    left: 0;
  }
  
  .theme-option {
    padding: 10px;
    gap: 12px;
  }
  
  .option-preview {
    width: 40px;
    height: 28px;
  }
}

/* 位置变体 */
.theme-toggle-container.position-top-left .theme-selector {
  top: calc(100% + 12px);
  left: 0;
  right: auto;
}

.theme-toggle-container.position-bottom-right .theme-selector {
  bottom: calc(100% + 12px);
  top: auto;
  right: 0;
}

.theme-toggle-container.position-bottom-left .theme-selector {
  bottom: calc(100% + 12px);
  top: auto;
  left: 0;
  right: auto;
}

/* 高级动画效果 */
.theme-toggle-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s ease;
  z-index: 1;
}

.theme-toggle-btn:hover::before {
  left: 100%;
}

/* 故障效果增强 */
.theme-toggle-btn.light-mode .theme-label {
  text-shadow: 
    1px 1px var(--neon-pink),
    -1px -1px var(--neon-cyan);
}

.theme-toggle-btn:not(.light-mode) .theme-label {
  text-shadow: 
    1px 1px var(--neon-pink),
    -1px -1px var(--neon-cyan);
}
</style> 