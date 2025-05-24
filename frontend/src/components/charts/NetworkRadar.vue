<!--
---------------------------------------------------------------
File name:                  NetworkRadar.vue
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                网络雷达图表组件，展示网络状态和性能指标
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现网络雷达可视化;
----
-->

<template>
  <div class="network-radar">
    <div class="radar-header">
      <h3 class="radar-title">
        <el-icon><Monitor /></el-icon>
        网络状态雷达
      </h3>
      <div class="radar-controls">
        <el-button
          @click="toggleAnimation"
          :type="isAnimated ? 'primary' : 'default'"
          size="small"
          class="control-btn pixel-btn"
        >
          {{ isAnimated ? '暂停动画' : '启动动画' }}
        </el-button>
        <el-button
          @click="refreshData"
          type="info"
          size="small"
          class="control-btn pixel-btn"
          :loading="isRefreshing"
        >
          刷新数据
        </el-button>
      </div>
    </div>

    <div class="radar-container" ref="radarContainer">
      <!-- SVG雷达图 -->
      <svg
        :width="radarSize"
        :height="radarSize"
        class="radar-svg"
        ref="radarSvg"
      >
        <!-- 背景网格 -->
        <g class="radar-grid">
          <!-- 同心圆 -->
          <circle
            v-for="level in 5"
            :key="`circle-${level}`"
            :cx="centerX"
            :cy="centerY"
            :r="(radarRadius / 5) * level"
            fill="none"
            :stroke="gridColor"
            :stroke-width="level === 5 ? 2 : 1"
            :opacity="level === 5 ? 0.8 : 0.3"
            class="grid-circle"
          />
          
          <!-- 辐射线 -->
          <line
            v-for="(metric, index) in metrics"
            :key="`line-${index}`"
            :x1="centerX"
            :y1="centerY"
            :x2="centerX + radarRadius * Math.cos(getAngle(index))"
            :y2="centerY + radarRadius * Math.sin(getAngle(index))"
            :stroke="gridColor"
            stroke-width="1"
            opacity="0.3"
            class="grid-line"
          />
        </g>

        <!-- 数据区域 -->
        <g class="radar-data">
          <!-- 数据多边形 -->
          <polygon
            :points="dataPolygonPoints"
            :fill="fillColor"
            :stroke="strokeColor"
            stroke-width="2"
            fill-opacity="0.3"
            class="data-polygon"
            :class="{ 'animated': isAnimated }"
          />
          
          <!-- 数据点 -->
          <circle
            v-for="(point, index) in dataPoints"
            :key="`point-${index}`"
            :cx="point.x"
            :cy="point.y"
            r="4"
            :fill="strokeColor"
            :stroke="backgroundColor"
            stroke-width="2"
            class="data-point"
            :class="{ 'animated': isAnimated }"
            @mouseenter="showTooltip(index, $event)"
            @mouseleave="hideTooltip"
          />
        </g>

        <!-- 标签 -->
        <g class="radar-labels">
          <text
            v-for="(metric, index) in metrics"
            :key="`label-${index}`"
            :x="centerX + (radarRadius + 20) * Math.cos(getAngle(index))"
            :y="centerY + (radarRadius + 20) * Math.sin(getAngle(index))"
            text-anchor="middle"
            dominant-baseline="central"
            :fill="textColor"
            class="metric-label pixel-text"
            :style="{ fontSize: '12px' }"
          >
            {{ metric.name }}
          </text>
        </g>

        <!-- 扫描线（仅动画模式） -->
        <g v-if="isAnimated" class="radar-scanner">
          <line
            :x1="centerX"
            :y1="centerY"
            :x2="scannerEndX"
            :y2="scannerEndY"
            :stroke="scannerColor"
            stroke-width="2"
            opacity="0.8"
            class="scanner-line"
          />
          <circle
            :cx="centerX"
            :cy="centerY"
            :r="radarRadius"
            fill="none"
            :stroke="scannerColor"
            stroke-width="1"
            opacity="0.2"
            class="scanner-circle"
          />
        </g>
      </svg>

      <!-- 数值显示 -->
      <div class="radar-values">
        <div
          v-for="(metric, index) in metrics"
          :key="`value-${index}`"
          class="value-item"
          :style="{ color: getMetricColor(metric.value) }"
        >
          <span class="value-name">{{ metric.name }}</span>
          <span class="value-number">{{ metric.value.toFixed(1) }}{{ metric.unit }}</span>
          <div class="value-bar">
            <div
              class="value-fill"
              :style="{
                width: `${(metric.value / metric.max) * 100}%`,
                backgroundColor: getMetricColor(metric.value)
              }"
            />
          </div>
        </div>
      </div>

      <!-- 工具提示 -->
      <div
        v-if="tooltip.visible"
        class="radar-tooltip"
        :style="{
          left: tooltip.x + 'px',
          top: tooltip.y + 'px'
        }"
      >
        <div class="tooltip-title">{{ tooltip.metric }}</div>
        <div class="tooltip-value">{{ tooltip.value }}{{ tooltip.unit }}</div>
        <div class="tooltip-status">{{ getStatusText(tooltip.normalizedValue) }}</div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="radar-stats">
      <div class="stat-grid">
        <div class="stat-item">
          <span class="stat-label">平均性能</span>
          <span class="stat-value" :style="{ color: getMetricColor(averagePerformance) }">
            {{ averagePerformance.toFixed(1) }}%
          </span>
        </div>
        <div class="stat-item">
          <span class="stat-label">最佳指标</span>
          <span class="stat-value" style="color: var(--neon-green)">
            {{ bestMetric.name }}
          </span>
        </div>
        <div class="stat-item">
          <span class="stat-label">需要关注</span>
          <span class="stat-value" style="color: var(--pixel-warning)">
            {{ worstMetric.name }}
          </span>
        </div>
        <div class="stat-item">
          <span class="stat-label">更新时间</span>
          <span class="stat-value">{{ lastUpdated }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Monitor } from '@element-plus/icons-vue'

// Props
interface Props {
  data?: NetworkMetric[]
  size?: number
  animated?: boolean
  refreshInterval?: number
}

interface NetworkMetric {
  name: string
  value: number
  max: number
  unit: string
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  size: 300,
  animated: true,
  refreshInterval: 5000
})

// Emit
const emit = defineEmits<{
  refresh: []
  metricClick: [metric: NetworkMetric]
}>()

// 状态
const radarContainer = ref<HTMLElement>()
const radarSvg = ref<SVGElement>()
const isAnimated = ref(props.animated)
const isRefreshing = ref(false)
const scannerAngle = ref(0)
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  metric: '',
  value: '',
  unit: '',
  normalizedValue: 0
})

let scannerAnimationFrame: number | null = null
let refreshTimer: number | null = null

// 默认网络指标数据
const defaultMetrics: NetworkMetric[] = [
  { name: '延迟', value: 45, max: 200, unit: 'ms', color: '#00ff41' },
  { name: '带宽', value: 85, max: 100, unit: '%', color: '#00d4ff' },
  { name: '丢包率', value: 2, max: 10, unit: '%', color: '#ff0080' },
  { name: 'CPU使用', value: 35, max: 100, unit: '%', color: '#ffff00' },
  { name: '内存使用', value: 68, max: 100, unit: '%', color: '#ff6600' },
  { name: '连接数', value: 156, max: 500, unit: '', color: '#bf00ff' }
]

// 计算属性
const metrics = computed(() => props.data.length > 0 ? props.data : defaultMetrics)
const radarSize = computed(() => props.size)
const centerX = computed(() => radarSize.value / 2)
const centerY = computed(() => radarSize.value / 2)
const radarRadius = computed(() => (radarSize.value - 80) / 2)

const gridColor = computed(() => 'var(--pixel-primary)')
const fillColor = computed(() => 'rgba(0, 212, 255, 0.2)')
const strokeColor = computed(() => 'var(--neon-cyan)')
const backgroundColor = computed(() => 'var(--bg-dark)')
const textColor = computed(() => 'var(--text-primary)')
const scannerColor = computed(() => 'var(--pixel-primary)')

// 数据点计算
const dataPoints = computed(() => {
  return metrics.value.map((metric, index) => {
    const normalizedValue = metric.value / metric.max
    const angle = getAngle(index)
    const radius = radarRadius.value * normalizedValue
    
    return {
      x: centerX.value + radius * Math.cos(angle),
      y: centerY.value + radius * Math.sin(angle),
      value: metric.value,
      metric: metric.name
    }
  })
})

const dataPolygonPoints = computed(() => {
  return dataPoints.value.map(point => `${point.x},${point.y}`).join(' ')
})

// 扫描器位置
const scannerEndX = computed(() => {
  return centerX.value + radarRadius.value * Math.cos(scannerAngle.value)
})

const scannerEndY = computed(() => {
  return centerY.value + radarRadius.value * Math.sin(scannerAngle.value)
})

// 统计数据
const averagePerformance = computed(() => {
  const total = metrics.value.reduce((sum, metric) => {
    return sum + (metric.value / metric.max) * 100
  }, 0)
  return total / metrics.value.length
})

const bestMetric = computed(() => {
  return metrics.value.reduce((best, current) => {
    const currentPerf = current.value / current.max
    const bestPerf = best.value / best.max
    return currentPerf > bestPerf ? current : best
  })
})

const worstMetric = computed(() => {
  return metrics.value.reduce((worst, current) => {
    const currentPerf = current.value / current.max
    const worstPerf = worst.value / worst.max
    return currentPerf < worstPerf ? current : worst
  })
})

const lastUpdated = computed(() => {
  return new Date().toLocaleTimeString()
})

// 方法

/**
 * 获取指标角度
 */
const getAngle = (index: number): number => {
  const totalMetrics = metrics.value.length
  const angleStep = (2 * Math.PI) / totalMetrics
  // 从顶部开始，顺时针旋转
  return angleStep * index - Math.PI / 2
}

/**
 * 获取指标颜色
 */
const getMetricColor = (value: number): string => {
  if (value >= 80) return 'var(--neon-green)'
  if (value >= 60) return 'var(--pixel-warning)'
  if (value >= 40) return 'var(--neon-orange)'
  return 'var(--pixel-danger)'
}

/**
 * 获取状态文本
 */
const getStatusText = (normalizedValue: number): string => {
  if (normalizedValue >= 0.8) return '优秀'
  if (normalizedValue >= 0.6) return '良好'
  if (normalizedValue >= 0.4) return '一般'
  return '需要优化'
}

/**
 * 切换动画
 */
const toggleAnimation = (): void => {
  isAnimated.value = !isAnimated.value
  
  if (isAnimated.value) {
    startScannerAnimation()
  } else {
    stopScannerAnimation()
  }
}

/**
 * 刷新数据
 */
const refreshData = async (): Promise<void> => {
  isRefreshing.value = true
  
  try {
    // 模拟网络请求延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 发送刷新事件
    emit('refresh')
    
    // 如果没有外部数据，模拟数据更新
    if (props.data.length === 0) {
      defaultMetrics.forEach(metric => {
        metric.value = Math.random() * metric.max
      })
    }
    
  } finally {
    isRefreshing.value = false
  }
}

/**
 * 显示工具提示
 */
const showTooltip = (index: number, event: MouseEvent): void => {
  const metric = metrics.value[index]
  const normalizedValue = metric.value / metric.max
  
  tooltip.value = {
    visible: true,
    x: event.offsetX + 10,
    y: event.offsetY - 10,
    metric: metric.name,
    value: metric.value.toFixed(1),
    unit: metric.unit,
    normalizedValue
  }
}

/**
 * 隐藏工具提示
 */
const hideTooltip = (): void => {
  tooltip.value.visible = false
}

/**
 * 启动扫描器动画
 */
const startScannerAnimation = (): void => {
  const animate = (): void => {
    scannerAngle.value += 0.02
    if (scannerAngle.value > 2 * Math.PI) {
      scannerAngle.value = 0
    }
    
    if (isAnimated.value) {
      scannerAnimationFrame = requestAnimationFrame(animate)
    }
  }
  
  animate()
}

/**
 * 停止扫描器动画
 */
const stopScannerAnimation = (): void => {
  if (scannerAnimationFrame) {
    cancelAnimationFrame(scannerAnimationFrame)
    scannerAnimationFrame = null
  }
}

/**
 * 启动自动刷新
 */
const startAutoRefresh = (): void => {
  if (props.refreshInterval > 0) {
    refreshTimer = window.setInterval(() => {
      refreshData()
    }, props.refreshInterval)
  }
}

/**
 * 停止自动刷新
 */
const stopAutoRefresh = (): void => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  if (isAnimated.value) {
    startScannerAnimation()
  }
  startAutoRefresh()
})

onUnmounted(() => {
  stopScannerAnimation()
  stopAutoRefresh()
})

// 监听动画状态变化
watch(isAnimated, (newValue) => {
  if (newValue) {
    startScannerAnimation()
  } else {
    stopScannerAnimation()
  }
})

// 暴露方法给父组件
defineExpose({
  refreshData,
  toggleAnimation,
  metrics: metrics
})
</script>

<style scoped>
.network-radar {
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  padding: 16px;
  color: var(--text-primary);
}

.radar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--pixel-primary);
}

.radar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

.radar-controls {
  display: flex;
  gap: 8px;
}

.control-btn {
  font-size: var(--font-size-xs);
  padding: 4px 8px;
}

.radar-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.radar-svg {
  background: radial-gradient(circle, var(--bg-dark) 0%, var(--bg-darker) 100%);
  border: 1px solid var(--pixel-primary);
  border-radius: 50%;
  overflow: visible;
}

/* SVG动画 */
.data-polygon.animated {
  animation: radarPulse 2s ease-in-out infinite;
}

.data-point.animated {
  animation: pointPulse 1.5s ease-in-out infinite;
}

.scanner-line {
  animation: scannerRotate 3s linear infinite;
  transform-origin: 50% 50%;
}

.scanner-circle {
  animation: scannerPulse 2s ease-in-out infinite;
}

@keyframes radarPulse {
  0%, 100% { fill-opacity: 0.3; }
  50% { fill-opacity: 0.5; }
}

@keyframes pointPulse {
  0%, 100% { r: 4; opacity: 1; }
  50% { r: 6; opacity: 0.8; }
}

@keyframes scannerRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes scannerPulse {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.4; }
}

/* 数值显示 */
.radar-values {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
  width: 100%;
  max-width: 400px;
}

.value-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 4px;
  transition: all var(--animation-speed-fast) ease;
}

.value-item:hover {
  box-shadow: var(--pixel-shadow);
  transform: translateY(-1px);
}

.value-name {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  text-align: center;
}

.value-number {
  font-size: var(--font-size-sm);
  font-weight: 500;
  text-align: center;
}

.value-bar {
  height: 4px;
  background: var(--bg-darker);
  border-radius: 2px;
  overflow: hidden;
  border: 1px solid rgba(0, 255, 65, 0.3);
}

.value-fill {
  height: 100%;
  background: var(--pixel-primary);
  transition: width var(--animation-speed-normal) ease;
  border-radius: 2px;
}

/* 工具提示 */
.radar-tooltip {
  position: absolute;
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 4px;
  padding: 8px;
  pointer-events: none;
  z-index: 1000;
  box-shadow: var(--pixel-shadow);
  min-width: 80px;
}

.tooltip-title {
  font-size: var(--font-size-xs);
  color: var(--text-primary);
  font-weight: 500;
}

.tooltip-value {
  font-size: var(--font-size-sm);
  color: var(--neon-cyan);
  margin: 2px 0;
}

.tooltip-status {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  opacity: 0.8;
}

/* 统计信息 */
.radar-stats {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--pixel-primary);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px;
  background: var(--bg-dark);
  border: 1px solid rgba(0, 255, 65, 0.3);
  border-radius: 4px;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  text-align: center;
}

.stat-value {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .radar-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .radar-controls {
    justify-content: center;
  }
  
  .radar-values {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .network-radar {
    padding: 12px;
  }
  
  .radar-values {
    grid-template-columns: 1fr;
  }
  
  .stat-grid {
    grid-template-columns: 1fr;
  }
}

/* 像素文本 */
.pixel-text {
  font-family: var(--standard-font);
  text-shadow: 1px 1px 0 var(--bg-dark);
}

/* 主题适配 */
[data-theme="light"] .radar-svg {
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
}

/* 舒适模式 */
[data-comfort="comfortable"] .data-polygon.animated,
[data-comfort="comfortable"] .data-point.animated,
[data-comfort="comfortable"] .scanner-line,
[data-comfort="comfortable"] .scanner-circle {
  animation: none !important;
}
</style> 