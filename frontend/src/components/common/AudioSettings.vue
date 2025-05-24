<!--
---------------------------------------------------------------
File name:                  AudioSettings.vue
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                音效设置组件，提供音效控制和音量调节
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现音效设置界面;
----
-->

<template>
  <div class="audio-settings">
    <div class="audio-header">
      <h3 class="settings-title">
        <el-icon><VideoPlay /></el-icon>
        音效设置
      </h3>
      <el-switch
        v-model="audioEnabled"
        @change="handleToggleAudio"
        active-text="启用"
        inactive-text="禁用"
        class="audio-toggle pixel-switch"
      />
    </div>

    <div class="audio-content" v-if="audioEnabled">
      <!-- 主音量控制 -->
      <div class="volume-control">
        <label class="control-label">主音量</label>
        <div class="volume-slider-container">
          <el-slider
            v-model="masterVolume"
            :min="0"
            :max="100"
            :step="5"
            :format-tooltip="(val: number) => `${val}%`"
            @change="handleVolumeChange"
            class="volume-slider"
          />
          <el-button
            @click="handleAudioTestClick"
            type="info"
            size="small"
            class="test-btn pixel-btn audio-test-button"
          >
            测试音效
          </el-button>
        </div>
      </div>

      <!-- 音效类型控制 -->
      <div class="sound-types">
        <h4>音效类型</h4>
        <div class="sound-grid">
          <div
            v-for="(sound, key) in soundTypes"
            :key="key"
            class="sound-item"
          >
            <div class="sound-info">
              <span class="sound-name">{{ sound.name }}</span>
              <span class="sound-desc">{{ sound.description }}</span>
            </div>
            <el-button
              @click="testSpecificSound(key)"
              size="small"
              class="sound-test-btn pixel-btn"
            >
              播放
            </el-button>
          </div>
        </div>
      </div>

      <!-- 快捷操作 */
      <div class="quick-actions">
        <el-button
          @click="playSuccessSequence"
          type="success"
          class="action-btn pixel-btn"
        >
          <el-icon><CircleCheckFilled /></el-icon>
          成功序列
        </el-button>
        
        <el-button
          @click="playScanSequence"
          type="primary"
          class="action-btn pixel-btn"
        >
          <el-icon><Search /></el-icon>
          扫描序列
        </el-button>
        
        <el-button
          @click="playNetworkSequence"
          type="info"
          class="action-btn pixel-btn"
        >
          <el-icon><Connection /></el-icon>
          网络序列
        </el-button>
      </div>

      <!-- 音效设置选项 -->
      <div class="audio-options">
        <h4>高级选项</h4>
        <el-checkbox v-model="enableUISound" @change="handleUIToggle">
          界面交互音效
        </el-checkbox>
        <el-checkbox v-model="enableNotifications" @change="handleNotificationToggle">
          通知音效
        </el-checkbox>
        <el-checkbox v-model="enableSystemSounds" @change="handleSystemToggle">
          系统状态音效
        </el-checkbox>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { 
  VideoPlay,
  CircleCheckFilled,
  Search,
  Connection
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { audioManager, playSound, type SoundType } from '../../utils/audioManager'

// 状态
const audioEnabled = ref(true)
const masterVolume = ref(50)
const enableUISound = ref(true)
const enableNotifications = ref(true)
const enableSystemSounds = ref(true)

// 音频测试点击状态
const audioTestClickCount = ref(0)
const lastAudioTestClickTime = ref(0)

// 音效类型定义
const soundTypes = ref({
  click: { name: '点击音效', description: '按钮点击时播放' },
  hover: { name: '悬停音效', description: '鼠标悬停时播放' },
  success: { name: '成功音效', description: '操作成功时播放' },
  error: { name: '错误音效', description: '操作失败时播放' },
  warning: { name: '警告音效', description: '警告提示时播放' },
  notification: { name: '通知音效', description: '系统通知时播放' },
  scan: { name: '扫描音效', description: '扫描进行时播放' },
  connect: { name: '连接音效', description: '建立连接时播放' },
  disconnect: { name: '断开音效', description: '断开连接时播放' },
  achievement: { name: '成就音效', description: '解锁成就时播放' },
  ping: { name: 'PING音效', description: 'PING测试时播放' }
})

// 方法

/**
 * 切换音效开关
 */
const handleToggleAudio = (enabled: boolean): void => {
  audioManager.setEnabled(enabled)
  
  if (enabled) {
    playSound('success')
    ElMessage.success('音效已启用')
  } else {
    ElMessage.info('音效已禁用')
  }
}

/**
 * 调整主音量
 */
const handleVolumeChange = (volume: number): void => {
  audioManager.setMasterVolume(volume / 100)
  playSound('beep')
}

/**
 * 处理音频测试按钮点击
 */
const handleAudioTestClick = async (): Promise<void> => {
  const now = Date.now()
  const timeDiff = now - lastAudioTestClickTime.value
  
  // 重置连击计数器（如果间隔太长）
  if (timeDiff > 1500) {
    audioTestClickCount.value = 0
  }
  
  audioTestClickCount.value++
  lastAudioTestClickTime.value = now
  
  // 播放测试音效
  playSound('notification')
  
  console.log(`🔊 音频测试按钮点击次数: ${audioTestClickCount.value}`)
  
  // 达到7次点击时尝试触发Ming彩蛋
  if (audioTestClickCount.value === 7) {
    try {
      // 动态导入Ming彩蛋引擎
      const { mingEasterEgg } = await import('../../utils/mingEasterEgg')
      
      // 尝试触发audioTest彩蛋
      const triggered = await mingEasterEgg.attemptTrigger('audioTest')
      
      if (triggered) {
        ElMessage({
          type: 'success',
          message: '🎵 音频系统检测到神秘频率！',
          duration: 3000
        })
        // 重置计数器
        audioTestClickCount.value = 0
      } else {
        // 给出音频相关的暗示
        const hints = [
          '🎧 音频系统正在校准...',
          '🔊 检测到高频信号...',
          '🎼 音频缓冲区优化完成',
          '🎵 发现隐藏的音频轨道...'
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
        message: '🔧 音频测试完成',
        duration: 1500
      })
    }
  } else if (audioTestClickCount.value > 3) {
    // 给出连击提示
    ElMessage({
      type: 'info',
      message: `🎯 连击 ${audioTestClickCount.value} 次！继续尝试...`,
      duration: 1000
    })
  }
}

/**
 * 测试特定音效
 */
const testSpecificSound = (soundType: string): void => {
  playSound(soundType as SoundType)
}

/**
 * 播放成功序列
 */
const playSuccessSequence = (): void => {
  audioManager.playSuccessSequence()
}

/**
 * 播放扫描序列
 */
const playScanSequence = (): void => {
  audioManager.playScanSound()
}

/**
 * 播放网络序列
 */
const playNetworkSequence = (): void => {
  audioManager.playNetworkActivity()
}

/**
 * 切换UI音效
 */
const handleUIToggle = (enabled: boolean): void => {
  // 这里可以添加UI音效的具体控制逻辑
  playSound(enabled ? 'success' : 'error')
}

/**
 * 切换通知音效
 */
const handleNotificationToggle = (enabled: boolean): void => {
  // 这里可以添加通知音效的具体控制逻辑
  playSound(enabled ? 'notification' : 'warning')
}

/**
 * 切换系统音效
 */
const handleSystemToggle = (enabled: boolean): void => {
  // 这里可以添加系统音效的具体控制逻辑
  playSound(enabled ? 'connect' : 'disconnect')
}

/**
 * 加载设置
 */
const loadSettings = (): void => {
  audioEnabled.value = audioManager.isEnabled()
  masterVolume.value = Math.round(audioManager.getMasterVolume() * 100)
}

// 生命周期
onMounted(() => {
  loadSettings()
})

// 监听音效状态变化
watch(audioEnabled, (enabled) => {
  if (enabled && !audioManager.isEnabled()) {
    audioManager.setEnabled(true)
  }
})

// 暴露方法给父组件
defineExpose({
  testSound: handleAudioTestClick,
  loadSettings
})
</script>

<style scoped>
.audio-settings {
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  padding: 20px;
  color: var(--text-primary);
}

.audio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--pixel-primary);
}

.settings-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--text-primary);
}

.audio-toggle {
  margin-left: 16px;
}

.audio-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 音量控制 */
.volume-control {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.control-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.volume-slider-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.volume-slider {
  flex: 1;
}

.test-btn {
  flex-shrink: 0;
}

/* 音效类型 */
.sound-types h4 {
  margin: 0 0 12px 0;
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

.sound-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.sound-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 4px;
  transition: all var(--animation-speed-fast) ease;
}

.sound-item:hover {
  box-shadow: var(--pixel-shadow);
  transform: translateY(-1px);
}

.sound-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sound-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.sound-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  opacity: 0.8;
}

.sound-test-btn {
  font-size: var(--font-size-xs);
  padding: 4px 8px;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 120px;
}

/* 音效选项 */
.audio-options h4 {
  margin: 0 0 12px 0;
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

.audio-options .el-checkbox {
  margin-bottom: 8px;
  color: var(--text-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .audio-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .volume-slider-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .action-btn {
    min-width: auto;
  }
}

/* 像素风格开关 */
.pixel-switch {
  border: var(--pixel-border);
  background: var(--bg-dark);
}

.pixel-switch.is-checked {
  border-color: var(--neon-cyan);
  background: var(--neon-cyan);
}
</style> 