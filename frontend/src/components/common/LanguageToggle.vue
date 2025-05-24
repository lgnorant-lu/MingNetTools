<!--
---------------------------------------------------------------
File name:                  LanguageToggle.vue
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                语言切换组件，支持中英文切换功能
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现语言切换界面;
----
-->

<template>
  <div class="language-toggle">
    <el-dropdown 
      @command="handleLanguageChange"
      trigger="click"
      class="language-dropdown"
    >
      <el-button type="text" class="language-btn pixel-btn">
        <span class="language-flag">{{ currentLanguageConfig.flag }}</span>
        <span class="language-name">{{ currentLanguageConfig.nativeName }}</span>
        <el-icon class="language-arrow">
          <ArrowDown />
        </el-icon>
      </el-button>
      
      <template #dropdown>
        <el-dropdown-menu class="language-menu pixel-dropdown">
          <el-dropdown-item
            v-for="language in supportedLanguages"
            :key="language.code"
            :command="language.code"
            :class="{
              'active': language.code === currentLanguage,
              'language-item': true,
              'pixel-dropdown-item': true
            }"
          >
            <div class="language-option">
              <span class="language-option-flag">{{ language.flag }}</span>
              <div class="language-option-text">
                <div class="language-option-native">{{ language.nativeName }}</div>
                <div class="language-option-english">{{ language.name }}</div>
              </div>
              <el-icon v-if="language.code === currentLanguage" class="language-check">
                <Check />
              </el-icon>
            </div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
    
    <!-- 快捷切换按钮（可选） -->
    <div class="language-quick-switch" v-if="showQuickSwitch">
      <el-button
        v-for="language in supportedLanguages"
        :key="`quick-${language.code}`"
        @click="handleLanguageChange(language.code)"
        :type="language.code === currentLanguage ? 'primary' : 'default'"
        size="small"
        class="quick-switch-btn pixel-btn"
        :class="{ 'active': language.code === currentLanguage }"
      >
        {{ language.flag }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowDown, Check } from '@element-plus/icons-vue'
import { useI18nStore, type Language } from '../../stores/i18n'
import { PixelAnimations } from '../../utils/animations'

// Props
interface Props {
  showQuickSwitch?: boolean
  showNames?: boolean
  size?: 'small' | 'default' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  showQuickSwitch: false,
  showNames: true,
  size: 'default'
})

// Store
const i18nStore = useI18nStore()

// 状态
const isLoading = ref(false)

// 计算属性
const currentLanguage = computed(() => i18nStore.currentLanguage)
const currentLanguageConfig = computed(() => i18nStore.currentLanguageConfig)
const supportedLanguages = computed(() => i18nStore.getSupportedLanguages())
const isDropdownOpen = ref(false)

// 方法

/**
 * 处理语言切换
 */
const handleLanguageChange = async (languageCode: Language): Promise<void> => {
  if (languageCode === currentLanguage.value || isLoading.value) {
    return
  }

  try {
    isLoading.value = true
    
    // 添加切换动画效果
    const button = document.querySelector('.language-btn') as HTMLElement
    if (button) {
      PixelAnimations.pixelButtonClick(button)
      PixelAnimations.createParticleExplosion(button, 4)
    }
    
    // 执行语言切换
    await i18nStore.setLanguage(languageCode)
    
    // 成功提示
    showLanguageChangeNotification(languageCode)
    
  } catch (error) {
    console.error('Language change failed:', error)
    // 可以在这里添加错误处理
  } finally {
    isLoading.value = false
  }
}

/**
 * 显示语言切换通知
 */
const showLanguageChangeNotification = (languageCode: Language): void => {
  const config = supportedLanguages.value.find(lang => lang.code === languageCode)
  if (!config) return

  // 发送语言切换事件给其他组件
  window.dispatchEvent(new CustomEvent('language-switch-notification', {
    detail: {
      language: languageCode,
      config,
      message: languageCode === 'zh' ? '语言已切换为中文' : 'Language switched to English'
    }
  }))
}

/**
 * 获取当前语言的问候语
 */
const getGreeting = computed((): string => {
  return currentLanguage.value === 'zh' ? '你好！' : 'Hello!'
})

/**
 * 键盘快捷键支持
 */
const handleKeyboardShortcut = (event: KeyboardEvent): void => {
  // Ctrl/Cmd + Shift + L 切换语言
  if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.code === 'KeyL') {
    event.preventDefault()
    
    const currentIndex = supportedLanguages.value.findIndex(
      lang => lang.code === currentLanguage.value
    )
    const nextIndex = (currentIndex + 1) % supportedLanguages.value.length
    const nextLanguage = supportedLanguages.value[nextIndex]
    
    handleLanguageChange(nextLanguage.code)
  }
}

// 生命周期
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  // 注册键盘快捷键
  document.addEventListener('keydown', handleKeyboardShortcut)
})

onUnmounted(() => {
  // 清理事件监听器
  document.removeEventListener('keydown', handleKeyboardShortcut)
})

// 暴露方法给父组件
defineExpose({
  handleLanguageChange,
  currentLanguage,
  supportedLanguages
})
</script>

<style scoped>
.language-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.language-dropdown {
  position: relative;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-dark);
  border: var(--pixel-border);
  color: var(--text-primary);
  font-family: var(--standard-font);
  font-size: var(--font-size-sm);
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--animation-speed-fast) ease;
  min-width: 80px;
}

.language-btn:hover {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  box-shadow: var(--pixel-shadow);
  transform: translateY(-1px);
}

.language-flag {
  font-size: 16px;
  line-height: 1;
}

.language-name {
  font-size: var(--font-size-xs);
  white-space: nowrap;
}

.language-arrow {
  font-size: 12px;
  transition: transform var(--animation-speed-fast) ease;
}

.language-dropdown.is-opened .language-arrow {
  transform: rotate(180deg);
}

/* 下拉菜单样式 */
.language-menu {
  background: var(--bg-darker) !important;
  border: var(--pixel-border) !important;
  border-radius: 4px !important;
  box-shadow: var(--pixel-shadow) !important;
  padding: 4px !important;
  min-width: 160px;
}

.language-item {
  margin: 2px 0 !important;
  border-radius: 4px !important;
  transition: all var(--animation-speed-fast) ease !important;
}

.language-item:hover {
  background: rgba(0, 255, 65, 0.1) !important;
  border-color: var(--pixel-primary) !important;
}

.language-item.active {
  background: rgba(0, 212, 255, 0.2) !important;
  border-color: var(--neon-cyan) !important;
}

.language-option {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  gap: 8px;
  width: 100%;
}

.language-option-flag {
  font-size: 18px;
  line-height: 1;
  flex-shrink: 0;
}

.language-option-text {
  flex: 1;
  min-width: 0;
}

.language-option-native {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: 500;
  line-height: 1.2;
}

.language-option-english {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  opacity: 0.8;
  line-height: 1.2;
}

.language-check {
  font-size: 14px;
  color: var(--neon-cyan);
  flex-shrink: 0;
}

/* 快捷切换按钮 */
.language-quick-switch {
  display: flex;
  gap: 4px;
  align-items: center;
}

.quick-switch-btn {
  width: 36px;
  height: 28px;
  padding: 4px;
  font-size: 14px;
  border: 1px solid var(--pixel-primary);
  background: var(--bg-darker);
  color: var(--pixel-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--animation-speed-fast) ease;
}

.quick-switch-btn:hover {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  box-shadow: var(--pixel-shadow);
  transform: translateY(-1px);
}

.quick-switch-btn.active {
  background: var(--neon-cyan);
  border-color: var(--neon-cyan);
  color: var(--bg-dark);
  box-shadow: 0 0 10px var(--neon-cyan);
}

/* 加载状态 */
.language-btn.loading {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.language-btn.loading .language-arrow {
  animation: languageLoading 1s linear infinite;
}

@keyframes languageLoading {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 语言切换动画 */
.language-switch-animation {
  animation: languageSwitchPulse 0.6s ease-out;
}

@keyframes languageSwitchPulse {
  0% { 
    transform: scale(1); 
    box-shadow: var(--pixel-shadow); 
  }
  50% { 
    transform: scale(1.05); 
    box-shadow: 0 0 20px var(--pixel-primary); 
  }
  100% { 
    transform: scale(1); 
    box-shadow: var(--pixel-shadow); 
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .language-btn {
    min-width: 60px;
    padding: 4px 8px;
  }
  
  .language-name {
    display: none;
  }
  
  .language-option-english {
    display: none;
  }
}

@media (max-width: 480px) {
  .language-toggle {
    gap: 4px;
  }
  
  .quick-switch-btn {
    width: 32px;
    height: 24px;
    font-size: 12px;
  }
}

/* 无障碍支持 */
.language-btn:focus {
  outline: 2px solid var(--neon-cyan);
  outline-offset: 2px;
}

.language-item:focus {
  background: rgba(0, 255, 65, 0.2) !important;
  outline: 1px solid var(--pixel-primary) !important;
}

/* 暗色主题特殊优化 */
[data-theme="dark"] .language-menu {
  background: var(--bg-darker) !important;
  border-color: var(--pixel-primary) !important;
}

/* 舒适模式适配 */
[data-comfort="comfortable"] .language-btn {
  font-family: var(--standard-font) !important;
  border-radius: 6px !important;
}

[data-comfort="comfortable"] .language-option-native,
[data-comfort="comfortable"] .language-option-english {
  font-family: var(--standard-font) !important;
}
</style> 