<!--
---------------------------------------------------------------
File name:                  AchievementSystem.vue
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                成就系统组件，展示用户使用网络工具的成就和进度
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现成就系统功能;
----
-->

<template>
  <div class="achievement-system">
    <div class="achievement-header">
      <h3 class="achievement-title">
        <el-icon><Trophy /></el-icon>
        成就系统
      </h3>
      <div class="achievement-stats">
        <span class="stat-item">
          <el-icon><Check /></el-icon>
          已解锁: {{ unlockedCount }}/{{ totalCount }}
        </span>
        <span class="stat-item">
          <el-icon><Star /></el-icon>
          总积分: {{ totalPoints }}
        </span>
      </div>
    </div>

    <!-- 成就进度概览 -->
    <div class="achievement-progress">
      <el-progress
        :percentage="progressPercentage"
        :stroke-width="8"
        :status="progressStatus"
        class="progress-bar"
      >
        <template #default="{ percentage }">
          <span class="progress-text">{{ percentage }}% 完成</span>
        </template>
      </el-progress>
    </div>

    <!-- 成就分类 -->
    <div class="achievement-categories">
      <el-tabs v-model="activeCategory" class="achievement-tabs">
        <el-tab-pane 
          v-for="category in categories" 
          :key="category.id"
          :label="category.name"
          :name="category.id"
        >
          <div class="category-achievements">
            <div
              v-for="achievement in getAchievementsByCategory(category.id)"
              :key="achievement.id"
              class="achievement-card"
              :class="{
                'unlocked': achievement.unlocked,
                'in-progress': achievement.progress > 0 && !achievement.unlocked,
                'locked': achievement.progress === 0
              }"
              @click="showAchievementDetail(achievement)"
            >
              <!-- 成就图标 -->
              <div class="achievement-icon">
                <div class="icon-wrapper" :style="{ background: achievement.color }">
                  <el-icon :size="24">
                    <component :is="achievement.icon" />
                  </el-icon>
                  <div v-if="achievement.unlocked" class="unlock-badge">
                    <el-icon><Check /></el-icon>
                  </div>
                </div>
              </div>

              <!-- 成就信息 -->
              <div class="achievement-info">
                <h4 class="achievement-name">{{ achievement.name }}</h4>
                <p class="achievement-desc">{{ achievement.description }}</p>
                
                <!-- 进度条 -->
                <div v-if="!achievement.unlocked" class="achievement-progress-bar">
                  <div class="progress-wrapper">
                    <div
                      class="progress-fill"
                      :style="{
                        width: `${(achievement.progress / achievement.target) * 100}%`,
                        background: achievement.color
                      }"
                    />
                  </div>
                  <span class="progress-label">
                    {{ achievement.progress }}/{{ achievement.target }}
                  </span>
                </div>

                <!-- 奖励信息 -->
                <div class="achievement-rewards">
                  <span class="reward-points">+{{ achievement.points }} 积分</span>
                  <span v-if="achievement.unlocked" class="unlock-date">
                    {{ formatDate(achievement.unlockedAt) }}
                  </span>
                </div>
              </div>

              <!-- 稀有度标识 -->
              <div class="achievement-rarity" :class="`rarity-${achievement.rarity}`">
                {{ getRarityText(achievement.rarity) }}
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 最近解锁 -->
    <div v-if="recentAchievements.length > 0" class="recent-achievements">
      <h4 class="recent-title">最近解锁</h4>
      <div class="recent-list">
        <div
          v-for="achievement in recentAchievements"
          :key="`recent-${achievement.id}`"
          class="recent-item"
        >
          <div class="recent-icon" :style="{ background: achievement.color }">
            <el-icon>
              <component :is="achievement.icon" />
            </el-icon>
          </div>
          <div class="recent-info">
            <span class="recent-name">{{ achievement.name }}</span>
            <span class="recent-date">{{ formatDate(achievement.unlockedAt) }}</span>
          </div>
          <div class="recent-points">+{{ achievement.points }}</div>
        </div>
      </div>
    </div>

    <!-- 成就详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      :title="detailDialog.achievement?.name"
      width="400px"
      class="achievement-dialog"
    >
      <div v-if="detailDialog.achievement" class="achievement-detail">
        <div class="detail-icon">
          <div class="icon-large" :style="{ background: detailDialog.achievement.color }">
            <el-icon :size="48">
              <component :is="detailDialog.achievement.icon" />
            </el-icon>
          </div>
        </div>
        
        <div class="detail-info">
          <p class="detail-desc">{{ detailDialog.achievement.description }}</p>
          <div class="detail-meta">
            <div class="meta-item">
              <span class="meta-label">稀有度:</span>
              <span class="meta-value" :class="`rarity-${detailDialog.achievement.rarity}`">
                {{ getRarityText(detailDialog.achievement.rarity) }}
              </span>
            </div>
            <div class="meta-item">
              <span class="meta-label">积分奖励:</span>
              <span class="meta-value">{{ detailDialog.achievement.points }}</span>
            </div>
            <div v-if="detailDialog.achievement.unlocked" class="meta-item">
              <span class="meta-label">解锁时间:</span>
              <span class="meta-value">{{ formatDate(detailDialog.achievement.unlockedAt) }}</span>
            </div>
          </div>
          
          <div v-if="!detailDialog.achievement.unlocked" class="detail-progress">
            <h5>进度</h5>
            <el-progress
              :percentage="(detailDialog.achievement.progress / detailDialog.achievement.target) * 100"
              :stroke-width="6"
              :color="detailDialog.achievement.color"
            />
            <p class="progress-text">
              {{ detailDialog.achievement.progress }} / {{ detailDialog.achievement.target }}
            </p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, markRaw } from 'vue'
import { 
  Trophy, 
  Check, 
  Star, 
  Location, 
  Timer, 
  Connection, 
  Search,
  Monitor,
  Cpu,
  Tools
} from '@element-plus/icons-vue'

// 成就稀有度
type AchievementRarity = 'common' | 'rare' | 'epic' | 'legendary'

// 成就类别
type AchievementCategory = 'network' | 'security' | 'performance' | 'exploration'

// 成就接口
interface Achievement {
  id: string
  name: string
  description: string
  category: AchievementCategory
  rarity: AchievementRarity
  icon: any
  color: string
  points: number
  target: number
  progress: number
  unlocked: boolean
  unlockedAt?: Date
}

// 成就分类
interface Category {
  id: AchievementCategory
  name: string
  icon: any
}

// 状态
const activeCategory = ref<AchievementCategory>('network')
const detailDialog = ref({
  visible: false,
  achievement: null as Achievement | null
})

// 成就分类定义 - 使用markRaw避免响应式警告
const categories: Category[] = [
  { id: 'network', name: '网络探索', icon: markRaw(Connection) },
  { id: 'security', name: '安全防护', icon: markRaw(Tools) },
  { id: 'performance', name: '性能优化', icon: markRaw(Cpu) },
  { id: 'exploration', name: '系统探索', icon: markRaw(Search) }
]

// 成就数据 - 使用markRaw包装图标组件
const achievements = ref<Achievement[]>([
  // 网络探索类
  {
    id: 'first_ping',
    name: '初次探测',
    description: '完成你的第一次PING测试',
    category: 'network',
    rarity: 'common',
    icon: markRaw(Location),
    color: '#00ff41',
    points: 10,
    target: 1,
    progress: 1,
    unlocked: true,
    unlockedAt: new Date('2025-01-20T10:30:00')
  },
  {
    id: 'ping_master',
    name: 'PING大师',
    description: '累计完成100次PING测试',
    category: 'network',
    rarity: 'rare',
    icon: markRaw(Timer),
    color: '#00d4ff',
    points: 50,
    target: 100,
    progress: 67,
    unlocked: false
  },
  {
    id: 'port_scanner',
    name: '端口侦察员',
    description: '完成10次端口扫描',
    category: 'network',
    rarity: 'common',
    icon: markRaw(Search),
    color: '#ff0080',
    points: 25,
    target: 10,
    progress: 8,
    unlocked: false
  },

  // 安全防护类
  {
    id: 'security_aware',
    name: '安全意识',
    description: '检测到第一个开放端口',
    category: 'security',
    rarity: 'common',
    icon: markRaw(Tools),
    color: '#ffff00',
    points: 15,
    target: 1,
    progress: 1,
    unlocked: true,
    unlockedAt: new Date('2025-01-22T14:15:00')
  },
  {
    id: 'vulnerability_hunter',
    name: '漏洞猎手',
    description: '发现20个高风险端口',
    category: 'security',
    rarity: 'epic',
    icon: markRaw(Location),
    color: '#bf00ff',
    points: 100,
    target: 20,
    progress: 3,
    unlocked: false
  },

  // 性能优化类
  {
    id: 'speed_demon',
    name: '速度恶魔',
    description: '达到低于50ms的平均延迟',
    category: 'performance',
    rarity: 'rare',
    icon: markRaw(Timer),
    color: '#ff6600',
    points: 75,
    target: 1,
    progress: 0,
    unlocked: false
  },
  {
    id: 'uptime_champion',
    name: '在线冠军',
    description: '连续监控24小时无中断',
    category: 'performance',
    rarity: 'legendary',
    icon: markRaw(Monitor),
    color: '#39ff14',
    points: 200,
    target: 24,
    progress: 8,
    unlocked: false
  },

  // 系统探索类
  {
    id: 'theme_explorer',
    name: '主题探索者',
    description: '尝试所有主题模式',
    category: 'exploration',
    rarity: 'common',
    icon: markRaw(Star),
    color: '#00ffff',
    points: 20,
    target: 2,
    progress: 2,
    unlocked: true,
    unlockedAt: new Date('2025-01-24T09:45:00')
  },
  {
    id: 'customization_expert',
    name: '定制专家',
    description: '调整所有个人设置选项',
    category: 'exploration',
    rarity: 'epic',
    icon: markRaw(Cpu),
    color: '#ff00ff',
    points: 150,
    target: 10,
    progress: 5,
    unlocked: false
  }
])

// 计算属性
const unlockedCount = computed(() => {
  return achievements.value.filter(a => a.unlocked).length
})

const totalCount = computed(() => {
  return achievements.value.length
})

const totalPoints = computed(() => {
  return achievements.value
    .filter(a => a.unlocked)
    .reduce((sum, a) => sum + a.points, 0)
})

const progressPercentage = computed(() => {
  return Math.round((unlockedCount.value / totalCount.value) * 100)
})

const progressStatus = computed(() => {
  const percentage = progressPercentage.value
  if (percentage >= 90) return 'success'
  if (percentage >= 70) return ''
  if (percentage >= 50) return 'warning'
  return 'exception'
})

const recentAchievements = computed(() => {
  return achievements.value
    .filter(a => a.unlocked && a.unlockedAt)
    .sort((a, b) => (b.unlockedAt?.getTime() || 0) - (a.unlockedAt?.getTime() || 0))
    .slice(0, 3)
})

// 方法

/**
 * 根据分类获取成就
 */
const getAchievementsByCategory = (categoryId: AchievementCategory): Achievement[] => {
  return achievements.value.filter(a => a.category === categoryId)
}

/**
 * 获取稀有度文本
 */
const getRarityText = (rarity: AchievementRarity): string => {
  const rarityMap = {
    common: '普通',
    rare: '稀有',
    epic: '史诗',
    legendary: '传说'
  }
  return rarityMap[rarity]
}

/**
 * 格式化日期
 */
const formatDate = (date?: Date): string => {
  if (!date) return ''
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 显示成就详情
 */
const showAchievementDetail = (achievement: Achievement): void => {
  detailDialog.value = {
    visible: true,
    achievement
  }
}

/**
 * 解锁成就
 */
const unlockAchievement = (achievementId: string): void => {
  const achievement = achievements.value.find(a => a.id === achievementId)
  if (achievement && !achievement.unlocked) {
    achievement.unlocked = true
    achievement.unlockedAt = new Date()
    achievement.progress = achievement.target
    
    // 可以在这里添加解锁动画或通知
    console.log(`成就解锁: ${achievement.name}`)
  }
}

/**
 * 更新成就进度
 */
const updateProgress = (achievementId: string, progress: number): void => {
  const achievement = achievements.value.find(a => a.id === achievementId)
  if (achievement && !achievement.unlocked) {
    achievement.progress = Math.min(progress, achievement.target)
    
    // 如果达到目标，自动解锁
    if (achievement.progress >= achievement.target) {
      unlockAchievement(achievementId)
    }
  }
}

// 暴露方法给父组件
defineExpose({
  unlockAchievement,
  updateProgress,
  achievements
})
</script>

<style scoped>
.achievement-system {
  background: var(--bg-darker);
  border: var(--pixel-border);
  border-radius: 8px;
  padding: 20px;
  color: var(--text-primary);
}

.achievement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--pixel-primary);
}

.achievement-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--text-primary);
}

.achievement-stats {
  display: flex;
  gap: 16px;
  font-size: var(--font-size-sm);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
}

.achievement-progress {
  margin-bottom: 24px;
}

.progress-bar {
  background: var(--bg-dark);
  border-radius: 4px;
  overflow: hidden;
}

.progress-text {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

/* 成就分类标签 */
.achievement-tabs {
  --el-tabs-header-color: var(--text-primary);
}

.category-achievements {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

/* 成就卡片 */
.achievement-card {
  position: relative;
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--bg-dark);
  border: 1px solid var(--pixel-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--animation-speed-fast) ease;
  overflow: hidden;
}

.achievement-card:hover {
  box-shadow: var(--pixel-shadow);
  transform: translateY(-2px);
}

.achievement-card.unlocked {
  border-color: var(--neon-green);
  background: linear-gradient(135deg, var(--bg-dark), rgba(0, 255, 65, 0.05));
}

.achievement-card.in-progress {
  border-color: var(--pixel-warning);
  background: linear-gradient(135deg, var(--bg-dark), rgba(255, 255, 0, 0.03));
}

.achievement-card.locked {
  opacity: 0.6;
  filter: grayscale(50%);
}

/* 成就图标 */
.achievement-icon {
  flex-shrink: 0;
}

.icon-wrapper {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bg-dark);
  font-weight: bold;
}

.unlock-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  background: var(--neon-green);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--bg-dark);
}

/* 成就信息 */
.achievement-info {
  flex: 1;
  min-width: 0;
}

.achievement-name {
  margin: 0 0 4px 0;
  font-size: var(--font-size-base);
  color: var(--text-primary);
  font-weight: 500;
}

.achievement-desc {
  margin: 0 0 8px 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.4;
}

/* 进度条 */
.achievement-progress-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.progress-wrapper {
  flex: 1;
  height: 6px;
  background: var(--bg-darker);
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid rgba(0, 255, 65, 0.3);
}

.progress-fill {
  height: 100%;
  background: var(--pixel-primary);
  transition: width var(--animation-speed-normal) ease;
  border-radius: 3px;
}

.progress-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  min-width: 40px;
  text-align: right;
}

/* 奖励信息 */
.achievement-rewards {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reward-points {
  color: var(--neon-cyan);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.unlock-date {
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
}

/* 稀有度标识 */
.achievement-rarity {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.rarity-common {
  background: rgba(128, 128, 128, 0.8);
  color: white;
}

.rarity-rare {
  background: rgba(0, 123, 255, 0.8);
  color: white;
}

.rarity-epic {
  background: rgba(128, 0, 128, 0.8);
  color: white;
}

.rarity-legendary {
  background: rgba(255, 165, 0, 0.8);
  color: white;
}

/* 最近解锁 */
.recent-achievements {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--pixel-primary);
}

.recent-title {
  margin: 0 0 12px 0;
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: var(--bg-dark);
  border: 1px solid rgba(0, 255, 65, 0.3);
  border-radius: 6px;
}

.recent-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bg-dark);
}

.recent-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.recent-name {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: 500;
}

.recent-date {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.recent-points {
  color: var(--neon-cyan);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

/* 详情对话框 */
.achievement-detail {
  text-align: center;
}

.detail-icon {
  margin-bottom: 16px;
}

.icon-large {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--bg-dark);
  margin: 0 auto;
}

.detail-info {
  text-align: left;
}

.detail-desc {
  margin: 0 0 16px 0;
  font-size: var(--font-size-base);
  color: var(--text-primary);
  line-height: 1.5;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-label {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.meta-value {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.detail-progress h5 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.detail-progress .progress-text {
  margin: 8px 0 0 0;
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .achievement-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .achievement-stats {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .category-achievements {
    grid-template-columns: 1fr;
  }
  
  .achievement-card {
    flex-direction: column;
    text-align: center;
  }
  
  .achievement-info {
    order: 2;
  }
  
  .achievement-rewards {
    justify-content: center;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .achievement-system {
    padding: 16px;
  }
  
  .recent-item {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  
  .recent-info {
    align-items: center;
  }
}
</style> 