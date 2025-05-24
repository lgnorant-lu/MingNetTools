<!--
---------------------------------------------------------------
File name:                  SettingsView.vue
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                系统设置页面，整合字体、音效、性能监控等设置
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，整合功能组件;
----
-->

<template>
  <div class="settings-container pixel-container">
    <!-- 页面标题 -->
    <div class="page-header pixel-header">
      <h1 class="page-title glitch-text" data-text="SYSTEM SETTINGS">
        SYSTEM SETTINGS
      </h1>
      <p class="page-subtitle">个性化设置和系统配置</p>
    </div>

    <!-- 设置标签页 -->
    <el-tabs v-model="activeTab" class="settings-tabs pixel-tabs" tab-position="left">
      <!-- 个人偏好 -->
      <el-tab-pane label="个人偏好" name="preferences">
        <template #label>
          <div class="tab-label">
            <el-icon><User /></el-icon>
            <span>个人偏好</span>
          </div>
        </template>
        <div class="preferences-section">
          <div class="section-header">
            <h3>个人偏好设置</h3>
            <p>自定义头像、快捷键、通知和数据管理</p>
          </div>
          <UserPreferences ref="userPreferencesRef" />
        </div>
      </el-tab-pane>

      <!-- 字体设置 -->
      <el-tab-pane label="字体设置" name="font">
        <template #label>
          <div class="tab-label">
            <el-icon><Edit /></el-icon>
            <span>字体设置</span>
          </div>
        </template>
        <FontSettings />
      </el-tab-pane>

      <!-- 音效设置 -->
      <el-tab-pane label="音效设置" name="audio">
        <template #label>
          <div class="tab-label">
            <el-icon><VideoPlay /></el-icon>
            <span>音效设置</span>
          </div>
        </template>
        <AudioSettings />
      </el-tab-pane>

      <!-- 动画设置 -->
      <el-tab-pane label="动画设置" name="animation">
        <template #label>
          <div class="tab-label">
            <el-icon><MagicStick /></el-icon>
            <span>动画设置</span>
          </div>
        </template>
        <div class="animation-section">
          <div class="section-header">
            <h3>动画性能控制</h3>
            <p>自定义动画效果、性能监控和舒适度设置</p>
          </div>
          <AnimationSettings />
        </div>
      </el-tab-pane>

      <!-- 网络监控 -->
      <el-tab-pane label="网络雷达" name="network">
        <template #label>
          <div class="tab-label">
            <el-icon><Monitor /></el-icon>
            <span>网络雷达</span>
          </div>
        </template>
        <div class="network-section">
          <div class="section-header">
            <h3>网络性能监控</h3>
            <p>实时监控网络状态和性能指标</p>
          </div>
          <NetworkRadar 
            :animated="true"
            :refresh-interval="5000"
            @refresh="handleNetworkRefresh"
          />
        </div>
      </el-tab-pane>

      <!-- 成就系统 -->
      <el-tab-pane label="成就系统" name="achievements">
        <template #label>
          <div class="tab-label">
            <el-icon><Trophy /></el-icon>
            <span>成就系统</span>
          </div>
        </template>
        <div class="achievements-section">
          <div class="section-header">
            <h3>用户成就</h3>
            <p>记录您的使用历程和解锁成就</p>
          </div>
          <AchievementSystem ref="achievementRef" />
        </div>
      </el-tab-pane>

      <!-- 主题设置 -->
      <el-tab-pane label="主题设置" name="theme">
        <template #label>
          <div class="tab-label">
            <el-icon><Brush /></el-icon>
            <span>主题设置</span>
          </div>
        </template>
        <div class="theme-section">
          <div class="section-header">
            <h3>外观主题</h3>
            <p>自定义界面外观和色彩主题</p>
          </div>
          
          <!-- 主题切换 -->
          <div class="theme-controls">
            <h4>主题模式</h4>
            <el-radio-group v-model="currentTheme" @change="handleThemeChange" class="theme-radio-group">
              <el-radio value="dark">
                <div class="theme-option">
                  <div class="theme-preview dark-preview"></div>
                  <span>暗黑模式</span>
                </div>
              </el-radio>
              <el-radio value="light">
                <div class="theme-option">
                  <div class="theme-preview light-preview"></div>
                  <span>明亮模式</span>
                </div>
              </el-radio>
            </el-radio-group>
          </div>

          <!-- 舒适度设置 -->
          <div class="comfort-controls">
            <h4>舒适度级别</h4>
            <el-radio-group v-model="currentComfort" @change="handleComfortChange" class="comfort-radio-group">
              <el-radio value="normal">正常模式</el-radio>
              <el-radio value="soft">柔和模式</el-radio>
              <el-radio value="comfortable">舒适模式</el-radio>
            </el-radio-group>
            <p class="comfort-description">
              舒适模式将降低亮度、减少动画效果，适合长时间使用
            </p>
          </div>
        </div>
      </el-tab-pane>

      <!-- 系统信息 -->
      <el-tab-pane label="系统信息" name="system">
        <template #label>
          <div class="tab-label">
            <el-icon><InfoFilled /></el-icon>
            <span>系统信息</span>
          </div>
        </template>
        <div class="system-section">
          <div class="section-header">
            <h3>系统信息</h3>
            <p>应用版本、环境信息和运行状态</p>
          </div>
          
          <div class="system-info-grid">
            <div class="info-card pixel-card">
              <h4>应用信息</h4>
              <div class="info-item">
                <span class="info-label">应用名称:</span>
                <span class="info-value">网络安全工具平台</span>
              </div>
              <div class="info-item">
                <span class="info-label">版本:</span>
                <span class="info-value">v1.0.0</span>
              </div>
              <div class="info-item">
                <span class="info-label">构建时间:</span>
                <span class="info-value">{{ buildTime }}</span>
              </div>
              
              <!-- Ming彩蛋触发点 - 隐藏的关于部分 -->
              <div class="info-item settings-about-section" @click="handleAboutClick">
                <span class="info-label">作者:</span>
                <span class="info-value ming-signature">Ming (鹿鸣) ✨</span>
              </div>
            </div>

            <div class="info-card pixel-card">
              <h4>运行环境</h4>
              <div class="info-item">
                <span class="info-label">浏览器:</span>
                <span class="info-value">{{ browserInfo }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">平台:</span>
                <span class="info-value">{{ platformInfo }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">屏幕分辨率:</span>
                <span class="info-value">{{ screenResolution }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Edit,
  VideoPlay,
  Monitor,
  Trophy,
  Brush,
  InfoFilled,
  User,
  MagicStick
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import FontSettings from '../components/common/FontSettings.vue'
import AudioSettings from '../components/common/AudioSettings.vue'
import NetworkRadar from '../components/charts/NetworkRadar.vue'
import AchievementSystem from '../components/features/AchievementSystem.vue'
import UserPreferences from '../components/common/UserPreferences.vue'
import AnimationSettings from '../components/common/AnimationSettings.vue'
import { useThemeStore } from '../stores/theme'
import { useFontStore } from '../stores/font'

// Stores
const themeStore = useThemeStore()
const fontStore = useFontStore()

// 状态
const activeTab = ref('font')
const achievementRef = ref()
const userPreferencesRef = ref()
const aboutClickCount = ref(0)
const lastAboutClickTime = ref(0)

// 主题设置
const currentTheme = ref(themeStore.currentMode)
const currentComfort = ref(fontStore.fontConfig.comfortLevel)

// 系统信息
const buildTime = ref(new Date().toLocaleDateString())
const browserInfo = computed(() => navigator.userAgent.split(' ')[0])
const platformInfo = computed(() => navigator.platform)
const screenResolution = computed(() => `${screen.width} x ${screen.height}`)

// 方法

/**
 * 处理主题变化
 */
const handleThemeChange = (theme: 'dark' | 'light'): void => {
  themeStore.setTheme(theme)
  ElMessage.success(`已切换到${theme === 'dark' ? '暗黑' : '明亮'}模式`)
}

/**
 * 处理舒适度变化
 */
const handleComfortChange = (comfort: string): void => {
  fontStore.setComfortLevel(comfort as any)
  ElMessage.success(`已切换到${comfort}模式`)
}

/**
 * 处理网络刷新
 */
const handleNetworkRefresh = (): void => {
  ElMessage.success('网络数据已刷新')
}

/**
 * 解锁测试成就
 */
const unlockTestAchievement = (): void => {
  if (achievementRef.value) {
    achievementRef.value.unlockAchievement('theme_explorer')
    ElMessage.success('解锁成就：主题探索者')
  }
}

/**
 * 处理关于点击
 */
const handleAboutClick = async (): Promise<void> => {
  const now = Date.now()
  const timeDiff = now - lastAboutClickTime.value
  
  // 重置连击计数器（如果间隔太长）
  if (timeDiff > 2000) {
    aboutClickCount.value = 0
  }
  
  aboutClickCount.value++
  lastAboutClickTime.value = now
  
  console.log(`🎯 关于部分点击次数: ${aboutClickCount.value}`)
  
  // 达到3次点击时尝试触发Ming彩蛋
  if (aboutClickCount.value === 3) {
    try {
      // 动态导入Ming彩蛋引擎
      const { mingEasterEgg } = await import('../utils/mingEasterEgg')
      
      // 尝试触发settingsAbout彩蛋
      const triggered = await mingEasterEgg.attemptTrigger('settingsAbout')
      
      if (triggered) {
        ElMessage({
          type: 'success',
          message: '🎁 哇！你发现了Ming的秘密！',
          duration: 3000
        })
        // 重置计数器
        aboutClickCount.value = 0
      } else {
        // 给出神秘暗示
        const hints = [
          '🤔 总感觉这里有什么特别的...',
          '✨ Ming似乎在这里留下了什么...',
          '🎭 继续探索，也许会有惊喜...'
        ]
        ElMessage({
          type: 'info',
          message: hints[Math.floor(Math.random() * hints.length)],
          duration: 2000
        })
      }
    } catch (error) {
      console.warn('Ming彩蛋系统加载失败:', error)
      ElMessage({
        type: 'info',
        message: '感谢你的关注！✨',
        duration: 2000
      })
    }
  } else {
    // 普通点击反馈
    const messages = [
      '👋 Hello!',
      '🎨 Created with love',
      '💫 Keep exploring...'
    ]
    ElMessage({
      type: 'info',
      message: messages[aboutClickCount.value % messages.length],
      duration: 1500
    })
  }
}

// 生命周期
onMounted(() => {
  // 检查是否应该解锁成就
  setTimeout(() => {
    unlockTestAchievement()
  }, 2000)
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: var(--font-size-2xl);
  margin: 0 0 8px 0;
  color: var(--pixel-primary);
}

.page-subtitle {
  color: var(--text-secondary);
  margin: 0;
  font-size: var(--font-size-sm);
}

/* 标签页样式 */
.settings-tabs {
  min-height: 600px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

/* 区块样式 */
.section-header {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--pixel-primary);
}

.section-header h3 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: var(--font-size-lg);
}

.section-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

/* 主题设置 */
.theme-controls {
  margin-bottom: 30px;
}

.theme-controls h4 {
  margin: 0 0 12px 0;
  color: var(--text-primary);
  font-size: var(--font-size-base);
}

.theme-radio-group {
  display: flex;
  gap: 20px;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.theme-preview {
  width: 40px;
  height: 30px;
  border: var(--pixel-border);
  border-radius: 4px;
}

.dark-preview {
  background: linear-gradient(135deg, #0a0a0a, #1a1a1a);
}

.light-preview {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
}

/* 舒适度设置 */
.comfort-controls h4 {
  margin: 0 0 12px 0;
  color: var(--text-primary);
  font-size: var(--font-size-base);
}

.comfort-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.comfort-description {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  opacity: 0.8;
  margin: 0;
}

/* 系统信息 */
.system-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-card {
  padding: 20px;
}

.info-card h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
  font-size: var(--font-size-base);
  border-bottom: 1px solid var(--pixel-primary);
  padding-bottom: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 255, 65, 0.1);
}

.info-label {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.info-value {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 16px;
  }
  
  .settings-tabs {
    min-height: auto;
  }
  
  .theme-radio-group {
    flex-direction: column;
    gap: 12px;
  }
  
  .theme-option {
    flex-direction: row;
    justify-content: flex-start;
  }
  
  .system-info-grid {
    grid-template-columns: 1fr;
  }
}

/* Element Plus 覆盖 */
.pixel-tabs .el-tabs__header {
  background: var(--bg-darker);
  border-right: var(--pixel-border);
}

.pixel-tabs .el-tabs__nav-wrap {
  background: var(--bg-darker);
}

.pixel-tabs .el-tabs__item {
  color: var(--text-secondary);
  border-bottom: 1px solid transparent;
  transition: all var(--animation-speed-fast) ease;
}

.pixel-tabs .el-tabs__item:hover {
  color: var(--pixel-primary);
  background: rgba(0, 255, 65, 0.1);
}

.pixel-tabs .el-tabs__item.is-active {
  color: var(--neon-cyan);
  background: rgba(0, 212, 255, 0.1);
  border-right: 2px solid var(--neon-cyan);
}

.pixel-tabs .el-tabs__content {
  padding: 20px;
  background: var(--bg-dark);
}

/* Ming彩蛋样式 */
.settings-about-section {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 4px;
  padding: 8px 4px !important;
}

.settings-about-section:hover {
  background: rgba(0, 255, 150, 0.1) !important;
  border-color: var(--primary-color) !important;
  transform: translateX(2px);
}

.ming-signature {
  position: relative;
  background: linear-gradient(45deg, var(--primary-color), #FF1493, #00FFFF);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: mingSignatureShine 3s ease-in-out infinite;
  font-weight: 600;
}

@keyframes mingSignatureShine {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.settings-about-section:hover .ming-signature {
  animation: mingSignatureGlow 0.8s ease-in-out infinite;
}

@keyframes mingSignatureGlow {
  0%, 100% {
    text-shadow: 0 0 5px var(--primary-color);
    transform: scale(1);
  }
  50% {
    text-shadow: 0 0 20px var(--primary-color), 0 0 30px #FF1493;
    transform: scale(1.05);
  }
}

/* Ming彩蛋激活状态 */
.settings-about-section.ming-active {
  background: linear-gradient(45deg, rgba(0, 255, 150, 0.2), rgba(255, 20, 147, 0.2)) !important;
  border-color: #FF1493 !important;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.5);
  animation: mingActivePulse 1s ease-in-out infinite;
}

@keyframes mingActivePulse {
  0%, 100% {
    transform: translateX(2px) scale(1);
  }
  50% {
    transform: translateX(2px) scale(1.02);
  }
}
</style> 