<!--
---------------------------------------------------------------
File name:                  FontSettings.vue
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                字体设置组件，提供字体类型、大小和舒适度控制
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现字体设置界面;
----
-->

<template>
  <div class="font-settings">
    <div class="font-settings-header">
      <h3 class="settings-title">
        <el-icon><Edit /></el-icon>
        字体设置
      </h3>
      <div class="readability-score">
        <el-progress
          :percentage="fontStore.getReadabilityScore"
          :status="getReadabilityStatus()"
          :stroke-width="6"
          text-inside
          class="readability-progress"
        />
        <span class="score-label">可读性评分</span>
      </div>
    </div>

    <div class="font-settings-content">
      <!-- 字体类型 -->
      <div class="setting-group">
        <label class="setting-label">字体类型</label>
        <el-radio-group 
          v-model="fontStore.fontConfig.type" 
          @change="handleFontTypeChange"
          class="font-type-group"
        >
          <el-radio value="pixel" class="font-radio pixel-radio">
            <span class="radio-content">
              <span class="radio-title pixel-font-demo">像素字体</span>
              <span class="radio-desc">游戏风格，适合沉浸体验</span>
            </span>
          </el-radio>
          <el-radio value="standard" class="font-radio standard-radio">
            <span class="radio-content">
              <span class="radio-title standard-font-demo">标准字体</span>
              <span class="radio-desc">清晰易读，适合长时间使用</span>
            </span>
          </el-radio>
          <el-radio value="hybrid" class="font-radio hybrid-radio">
            <span class="radio-content">
              <span class="radio-title hybrid-font-demo">混合字体</span>
              <span class="radio-desc">平衡体验，兼顾美观与实用</span>
            </span>
          </el-radio>
        </el-radio-group>
      </div>

      <!-- 字体大小 -->
      <div class="setting-group">
        <label class="setting-label">字体大小</label>
        <div class="size-controls">
          <el-slider
            v-model="fontSizeIndex"
            :min="0"
            :max="fontSizes.length - 1"
            :step="1"
            :marks="fontSizeMarks"
            @change="handleFontSizeChange"
            class="size-slider"
          />
          <div class="size-preview">
            <span class="size-demo" :style="{ fontSize: currentFontSize }">
              示例文字 Sample Text
            </span>
          </div>
        </div>
      </div>

      <!-- 舒适度级别 -->
      <div class="setting-group">
        <label class="setting-label">舒适度级别</label>
        <el-radio-group 
          v-model="fontStore.fontConfig.comfortLevel" 
          @change="handleComfortLevelChange"
          class="comfort-group"
        >
          <el-radio value="normal" class="comfort-radio">
            <span class="comfort-content">
              <span class="comfort-title">正常</span>
              <span class="comfort-desc">标准显示效果</span>
            </span>
          </el-radio>
          <el-radio value="soft" class="comfort-radio">
            <span class="comfort-content">
              <span class="comfort-title">柔和</span>
              <span class="comfort-desc">降低亮度和对比度</span>
            </span>
          </el-radio>
          <el-radio value="comfortable" class="comfort-radio">
            <span class="comfort-content">
              <span class="comfort-title">舒适</span>
              <span class="comfort-desc">最大化护眼效果</span>
            </span>
          </el-radio>
        </el-radio-group>
      </div>

      <!-- 高级设置 -->
      <div class="setting-group advanced-settings">
        <el-collapse v-model="advancedExpanded" class="advanced-collapse">
          <el-collapse-item name="advanced" title="高级设置">
            
            <!-- 行高调节 -->
            <div class="advanced-control">
              <label class="control-label">行高</label>
              <div class="control-wrapper">
                <el-slider
                  v-model="fontStore.fontConfig.lineHeight"
                  :min="1"
                  :max="3"
                  :step="0.1"
                  :format-tooltip="(val: number) => `${val.toFixed(1)}`"
                  @change="handleLineHeightChange"
                  class="advanced-slider"
                />
                <span class="control-value">{{ fontStore.fontConfig.lineHeight.toFixed(1) }}</span>
              </div>
            </div>

            <!-- 字符间距调节 -->
            <div class="advanced-control">
              <label class="control-label">字符间距</label>
              <div class="control-wrapper">
                <el-slider
                  v-model="fontStore.fontConfig.letterSpacing"
                  :min="-2"
                  :max="5"
                  :step="0.1"
                  :format-tooltip="(val: number) => `${val.toFixed(1)}px`"
                  @change="handleLetterSpacingChange"
                  class="advanced-slider"
                />
                <span class="control-value">{{ fontStore.fontConfig.letterSpacing.toFixed(1) }}px</span>
              </div>
            </div>

          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 预设配置 -->
      <div class="setting-group">
        <label class="setting-label">快速预设</label>
        <div class="preset-buttons">
          <el-button
            v-for="(preset, key) in fontStore.presets"
            :key="key"
            @click="handlePresetApply(key)"
            class="preset-btn pixel-btn"
            size="small"
          >
            <el-icon><Star /></el-icon>
            {{ getPresetName(key) }}
          </el-button>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="setting-actions">
        <el-button
          @click="handleReset"
          type="warning"
          class="action-btn pixel-btn"
        >
          <el-icon><RefreshLeft /></el-icon>
          重置默认
        </el-button>
        
        <el-button
          @click="handleExport"
          type="info"
          class="action-btn pixel-btn"
        >
          <el-icon><Download /></el-icon>
          导出设置
        </el-button>
        
        <el-button
          @click="handleImport"
          type="success"
          class="action-btn pixel-btn"
        >
          <el-icon><Upload /></el-icon>
          导入设置
        </el-button>
      </div>

      <!-- 实时预览 -->
      <div class="setting-preview">
        <div class="preview-header">
          <h4>实时预览</h4>
        </div>
        <div class="preview-content" :style="previewStyles">
          <p class="preview-text">
            这是字体设置的实时预览效果。您可以看到当前设置下文字的显示效果。
            This is a real-time preview of the font settings. You can see how text appears with current settings.
          </p>
          <div class="preview-stats">
            <span class="stat-item">类型: {{ getTypeDisplayName() }}</span>
            <span class="stat-item">大小: {{ currentFontSize }}</span>
            <span class="stat-item">舒适度: {{ getComfortDisplayName() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept=".json"
      @change="handleFileImport"
      style="display: none"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  Edit, 
  Star, 
  RefreshLeft, 
  Download, 
  Upload 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useFontStore, type FontSize, type FontType, type ComfortLevel } from '../../stores/font'

// Store
const fontStore = useFontStore()

// 状态
const advancedExpanded = ref([''])
const fileInput = ref<HTMLInputElement>()

// 字体大小配置
const fontSizes: FontSize[] = ['xs', 'sm', 'base', 'lg', 'xl', '2xl']
const fontSizeLabels = {
  'xs': '极小',
  'sm': '小',
  'base': '标准', 
  'lg': '大',
  'xl': '极大',
  '2xl': '超大'
}

// 计算属性
const fontSizeIndex = computed({
  get: () => fontSizes.indexOf(fontStore.fontConfig.size),
  set: (index: number) => {
    if (index >= 0 && index < fontSizes.length) {
      fontStore.setFontSize(fontSizes[index])
    }
  }
})

const fontSizeMarks = computed(() => {
  const marks: Record<number, string> = {}
  fontSizes.forEach((size, index) => {
    marks[index] = fontSizeLabels[size]
  })
  return marks
})

const currentFontSize = computed(() => {
  const sizeMap = {
    'xs': '10px',
    'sm': '12px', 
    'base': '14px',
    'lg': '16px',
    'xl': '18px',
    '2xl': '20px'
  }
  return sizeMap[fontStore.fontConfig.size]
})

const previewStyles = computed(() => ({
  fontFamily: fontStore.currentFontFamily,
  fontSize: currentFontSize.value,
  lineHeight: fontStore.fontConfig.lineHeight,
  letterSpacing: `${fontStore.fontConfig.letterSpacing}px`
}))

// 方法

/**
 * 处理字体类型变化
 */
const handleFontTypeChange = (type: FontType): void => {
  fontStore.setFontType(type)
  showChangeNotification('字体类型已更新')
}

/**
 * 处理字体大小变化
 */
const handleFontSizeChange = (index: number): void => {
  if (index >= 0 && index < fontSizes.length) {
    fontStore.setFontSize(fontSizes[index])
    showChangeNotification('字体大小已更新')
  }
}

/**
 * 处理舒适度级别变化
 */
const handleComfortLevelChange = (level: ComfortLevel): void => {
  fontStore.setComfortLevel(level)
  showChangeNotification('舒适度级别已更新')
}

/**
 * 处理行高变化
 */
const handleLineHeightChange = (height: number): void => {
  fontStore.setLineHeight(height)
}

/**
 * 处理字符间距变化
 */
const handleLetterSpacingChange = (spacing: number): void => {
  fontStore.setLetterSpacing(spacing)
}

/**
 * 应用预设配置
 */
const handlePresetApply = (presetKey: string): void => {
  fontStore.applyPreset(presetKey as keyof typeof fontStore.presets)
  showChangeNotification(`已应用${getPresetName(presetKey)}预设`)
}

/**
 * 重置到默认设置
 */
const handleReset = (): void => {
  fontStore.resetToDefault()
  ElMessage.success('已重置为默认设置')
}

/**
 * 导出设置
 */
const handleExport = (): void => {
  try {
    const settings = {
      fontConfig: fontStore.fontConfig,
      timestamp: new Date().toISOString(),
      version: '1.0'
    }
    
    const blob = new Blob([JSON.stringify(settings, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `font-settings-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    ElMessage.success('设置已导出')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('Export failed:', error)
  }
}

/**
 * 导入设置
 */
const handleImport = (): void => {
  fileInput.value?.click()
}

/**
 * 处理文件导入
 */
const handleFileImport = (event: Event): void => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string
      const settings = JSON.parse(content)
      
      if (settings.fontConfig && isValidFontConfig(settings.fontConfig)) {
        fontStore.fontConfig = settings.fontConfig
        fontStore.applyFontSettings()
        fontStore.applyComfortLevel()
        ElMessage.success('设置已导入')
      } else {
        ElMessage.error('无效的设置文件')
      }
    } catch (error) {
      ElMessage.error('导入失败：文件格式错误')
      console.error('Import failed:', error)
    }
  }
  
  reader.readAsText(file)
}

/**
 * 验证字体配置
 */
const isValidFontConfig = (config: any): boolean => {
  const validTypes: FontType[] = ['pixel', 'standard', 'hybrid']
  const validSizes: FontSize[] = ['xs', 'sm', 'base', 'lg', 'xl', '2xl']
  const validComfort: ComfortLevel[] = ['normal', 'soft', 'comfortable']

  return (
    config &&
    typeof config === 'object' &&
    validTypes.includes(config.type) &&
    validSizes.includes(config.size) &&
    validComfort.includes(config.comfortLevel) &&
    typeof config.lineHeight === 'number' &&
    typeof config.letterSpacing === 'number'
  )
}

/**
 * 显示变更通知
 */
const showChangeNotification = (message: string): void => {
  ElMessage({
    message,
    type: 'success',
    duration: 2000,
    showClose: false
  })
}

/**
 * 获取可读性状态
 */
const getReadabilityStatus = (): string => {
  const score = fontStore.getReadabilityScore
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'exception'
}

/**
 * 获取预设名称
 */
const getPresetName = (key: string): string => {
  const names: Record<string, string> = {
    gaming: '游戏风格',
    comfortable: '舒适阅读',
    accessibility: '无障碍'
  }
  return names[key] || key
}

/**
 * 获取类型显示名称
 */
const getTypeDisplayName = (): string => {
  const names: Record<FontType, string> = {
    pixel: '像素字体',
    standard: '标准字体',
    hybrid: '混合字体'
  }
  return names[fontStore.fontConfig.type]
}

/**
 * 获取舒适度显示名称
 */
const getComfortDisplayName = (): string => {
  const names: Record<ComfortLevel, string> = {
    normal: '正常',
    soft: '柔和',
    comfortable: '舒适'
  }
  return names[fontStore.fontConfig.comfortLevel]
}

// 监听字体配置变化
watch(
  () => fontStore.fontConfig,
  () => {
    // 可以在这里添加变化的副作用
  },
  { deep: true }
)
</script>

<style scoped>
.font-settings {
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  padding: 20px;
  color: var(--text-primary);
}

.font-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
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

.readability-score {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.readability-progress {
  width: 120px;
}

.score-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.setting-group {
  margin-bottom: 32px;
  padding: 24px;
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  box-shadow: var(--pixel-shadow);
  transition: all var(--animation-speed-fast) ease;
  min-height: 120px;
  display: flex;
  flex-direction: column;
}

.setting-group:hover {
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
}

.setting-label {
  display: block;
  font-size: var(--font-size-lg);
  color: var(--pixel-primary);
  margin-bottom: 20px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
  flex-shrink: 0;
}

/* 字体类型选择 */
.font-type-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  flex: 1;
  align-items: stretch;
}

.font-radio {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  border-radius: 8px;
  padding: 16px;
  transition: all var(--animation-speed-fast) ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  align-items: center;
}

.font-radio:hover {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.font-radio.is-checked {
  border-color: var(--neon-cyan);
  background: rgba(0, 212, 255, 0.1);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}

.radio-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.radio-title {
  font-size: var(--font-size-base);
  font-weight: 500;
}

.radio-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  opacity: 0.8;
}

.pixel-font-demo {
  font-family: var(--pixel-font) !important;
}

.standard-font-demo {
  font-family: var(--standard-font) !important;
}

.hybrid-font-demo {
  font-family: var(--standard-font) !important;
}

/* 字体大小控制 */
.size-controls {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
}

.size-slider {
  flex: 1;
}

.size-preview {
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 6px;
  padding: 16px;
  text-align: center;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.size-demo {
  font-family: var(--current-font-family);
  line-height: 1.5;
}

/* 舒适度选择 */
.comfort-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  flex: 1;
  align-items: stretch;
}

.comfort-radio {
  background: var(--bg-dark);
  border: 2px solid var(--pixel-primary);
  border-radius: 8px;
  padding: 16px;
  transition: all var(--animation-speed-fast) ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  align-items: center;
}

.comfort-radio:hover {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.comfort-radio.is-checked {
  border-color: var(--neon-cyan);
  background: rgba(0, 212, 255, 0.1);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}

.comfort-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comfort-title {
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.comfort-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  opacity: 0.8;
}

/* 高级设置 */
.advanced-settings {
  background: var(--bg-dark);
  border-radius: 6px;
  overflow: hidden;
}

.advanced-collapse {
  border: none;
  background: transparent;
}

.advanced-control {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.control-label {
  min-width: 80px;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.control-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.advanced-slider {
  flex: 1;
}

.control-value {
  min-width: 40px;
  text-align: right;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* 预设按钮 */
.preset-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  flex: 1;
}

.preset-btn {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 操作按钮 */
.setting-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
  margin-top: 24px;
  padding: 20px;
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
}

.action-btn {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 实时预览 */
.setting-preview {
  margin-top: 24px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 6px;
  overflow: hidden;
}

.preview-header {
  padding: 12px 16px;
  background: linear-gradient(135deg, var(--bg-darker), var(--bg-dark));
  border-bottom: 1px solid var(--pixel-primary);
}

.preview-header h4 {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.preview-content {
  padding: 16px;
}

.preview-text {
  margin: 0 0 12px 0;
  line-height: inherit;
  letter-spacing: inherit;
}

.preview-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  opacity: 0.8;
}

.stat-item {
  padding: 4px 8px;
  background: var(--bg-darker);
  border-radius: 4px;
  border: 1px solid rgba(0, 255, 65, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .font-settings-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .comfort-group {
    flex-direction: column;
  }
  
  .setting-actions {
    flex-direction: column;
  }
  
  .preset-buttons {
    flex-direction: column;
  }
  
  .preview-stats {
    flex-direction: column;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .font-settings {
    padding: 16px;
  }
  
  .advanced-control {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .control-wrapper {
    flex-direction: column;
    align-items: stretch;
  }
}
</style> 