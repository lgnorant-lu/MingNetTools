<!--
---------------------------------------------------------------
File name:                  UserPreferences.vue
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                用户个人偏好设置组件，提供个性化配置管理
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建，实现个人偏好设置界面;
----
-->

<template>
  <div class="user-preferences">
    <!-- 个人信息设置 -->
    <div class="preference-section">
      <h3 class="section-title">
        <el-icon><User /></el-icon>
        个人信息
      </h3>
      
      <div class="profile-settings">
        <!-- 头像设置 -->
        <div class="avatar-section">
          <div class="avatar-container">
            <el-avatar 
              :size="80" 
              :src="userProfile.avatar" 
              class="user-avatar pixel-avatar"
              @click="handleAvatarClick"
            >
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="avatar-overlay" @click="handleAvatarClick">
              <el-icon><Camera /></el-icon>
              <span>更换头像</span>
            </div>
          </div>
          
          <!-- 头像选择弹窗 -->
          <el-dialog 
            v-model="avatarDialogVisible" 
            title="选择头像" 
            width="500px"
            class="pixel-dialog"
          >
            <div class="avatar-grid">
              <div 
                v-for="(avatar, index) in avatarOptions" 
                :key="index"
                class="avatar-option"
                :class="{ active: userProfile.avatar === avatar }"
                @click="selectAvatar(avatar)"
              >
                <el-avatar :size="60" :src="avatar" />
              </div>
            </div>
            
            <div class="upload-section">
              <el-upload
                class="avatar-uploader"
                action="#"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                accept="image/*"
              >
                <el-button type="primary" class="pixel-btn">
                  <el-icon><Upload /></el-icon>
                  上传自定义头像
                </el-button>
              </el-upload>
            </div>
          </el-dialog>
        </div>
        
        <!-- 用户信息表单 -->
        <div class="profile-form">
          <el-form :model="userProfile" label-width="100px" class="pixel-form">
            <el-form-item label="昵称">
              <el-input 
                v-model="userProfile.nickname" 
                placeholder="请输入昵称"
                class="pixel-input"
                @change="saveUserProfile"
              />
            </el-form-item>
            
            <el-form-item label="邮箱">
              <el-input 
                v-model="userProfile.email" 
                placeholder="请输入邮箱"
                type="email"
                class="pixel-input"
                @change="saveUserProfile"
              />
            </el-form-item>
            
            <el-form-item label="个人简介">
              <el-input 
                v-model="userProfile.bio" 
                type="textarea"
                :rows="3"
                placeholder="介绍一下自己..."
                class="pixel-textarea"
                @change="saveUserProfile"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 快捷键设置 -->
    <div class="preference-section">
      <h3 class="section-title">
        <el-icon><Operation /></el-icon>
        快捷键配置
      </h3>
      
      <div class="hotkey-settings">
        <div 
          v-for="(hotkey, key) in shortcuts" 
          :key="key as string"
          class="hotkey-item"
        >
          <div class="hotkey-info">
            <span class="hotkey-label">{{ hotkey.name }}</span>
            <span class="hotkey-desc">{{ hotkey.description }}</span>
          </div>
          
          <div class="hotkey-input">
            <el-tag 
              v-if="hotkey.keys.length > 0"
              class="hotkey-tag pixel-tag"
              closable
              @close="clearHotkey(key as string)"
            >
              {{ formatHotkey(hotkey.keys) }}
            </el-tag>
            
            <el-button 
              size="small"
              class="pixel-btn"
              @click="recordHotkey(key as string)"
              :loading="recordingKey === key"
            >
              {{ recordingKey === key ? '按下新快捷键...' : '设置' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知设置 -->
    <div class="preference-section">
      <h3 class="section-title">
        <el-icon><Bell /></el-icon>
        通知设置
      </h3>
      
      <div class="notification-settings">
        <div class="notification-item">
          <div class="notification-info">
            <span class="notification-label">扫描完成通知</span>
            <span class="notification-desc">扫描任务完成时显示桌面通知</span>
          </div>
          <el-switch 
            v-model="notifications.scanComplete" 
            class="pixel-switch"
            @change="saveNotificationSettings"
          />
        </div>
        
        <div class="notification-item">
          <div class="notification-info">
            <span class="notification-label">PING异常通知</span>
            <span class="notification-desc">PING测试异常时显示警告通知</span>
          </div>
          <el-switch 
            v-model="notifications.pingAbnormal" 
            class="pixel-switch"
            @change="saveNotificationSettings"
          />
        </div>
        
        <div class="notification-item">
          <div class="notification-info">
            <span class="notification-label">系统状态通知</span>
            <span class="notification-desc">系统状态变化时显示通知</span>
          </div>
          <el-switch 
            v-model="notifications.systemStatus" 
            class="pixel-switch"
            @change="saveNotificationSettings"
          />
        </div>
        
        <div class="notification-item">
          <div class="notification-info">
            <span class="notification-label">成就解锁通知</span>
            <span class="notification-desc">解锁新成就时显示庆祝通知</span>
          </div>
          <el-switch 
            v-model="notifications.achievement" 
            class="pixel-switch"
            @change="saveNotificationSettings"
          />
        </div>
      </div>
    </div>

    <!-- 数据管理 -->
    <div class="preference-section">
      <h3 class="section-title">
        <el-icon><Files /></el-icon>
        数据管理
      </h3>
      
      <div class="data-management">
        <div class="data-actions">
          <el-button 
            type="primary" 
            class="pixel-btn"
            @click="exportSettings"
          >
            <el-icon><Download /></el-icon>
            导出设置
          </el-button>
          
          <el-button 
            type="info" 
            class="pixel-btn"
            @click="importSettings"
          >
            <el-icon><Upload /></el-icon>
            导入设置
          </el-button>
          
          <el-button 
            type="warning" 
            class="pixel-btn"
            @click="resetSettings"
          >
            <el-icon><RefreshRight /></el-icon>
            重置设置
          </el-button>
          
          <el-button 
            type="danger" 
            class="pixel-btn"
            @click="clearAllData"
          >
            <el-icon><Delete /></el-icon>
            清除所有数据
          </el-button>
        </div>
        
        <div class="data-info">
          <div class="info-item">
            <span class="info-label">数据大小:</span>
            <span class="info-value">{{ formatDataSize(getStorageSize()) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最后备份:</span>
            <span class="info-value">{{ lastBackupTime || '未备份' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input 
      ref="fileInput" 
      type="file" 
      accept=".json"
      style="display: none"
      @change="handleFileImport"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import {
  User,
  Camera,
  Upload,
  Operation,
  Bell,
  Files,
  Download,
  RefreshRight,
  Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 类型定义
interface UserProfile {
  avatar: string
  nickname: string
  email: string
  bio: string
}

interface Shortcut {
  name: string
  description: string
  keys: string[]
}

interface Shortcuts {
  [key: string]: Shortcut
}

interface Notifications {
  scanComplete: boolean
  pingAbnormal: boolean
  systemStatus: boolean
  achievement: boolean
}

// 状态
const avatarDialogVisible = ref(false)
const recordingKey = ref<string | null>(null)
const fileInput = ref<HTMLInputElement>()
const lastBackupTime = ref<string>('')

// 用户信息
const userProfile = reactive<UserProfile>({
  avatar: '',
  nickname: '网络管理员',
  email: '',
  bio: ''
})

// 头像选项
const avatarOptions = [
  '/avatars/avatar1.png',
  '/avatars/avatar2.png', 
  '/avatars/avatar3.png',
  '/avatars/avatar4.png',
  '/avatars/avatar5.png',
  '/avatars/avatar6.png'
]

// 快捷键设置
const shortcuts = reactive<Shortcuts>({
  refresh: {
    name: '刷新数据',
    description: '刷新当前页面数据',
    keys: ['F5']
  },
  scan: {
    name: '快速扫描',
    description: '启动快速端口扫描',
    keys: ['Ctrl', 'Shift', 'S']
  },
  ping: {
    name: '快速PING',
    description: '启动PING测试',
    keys: ['Ctrl', 'Shift', 'P']
  },
  settings: {
    name: '打开设置',
    description: '打开系统设置页面',
    keys: ['Ctrl', ',']
  },
  help: {
    name: '帮助文档',
    description: '显示帮助信息',
    keys: ['F1']
  }
})

// 通知设置
const notifications = reactive<Notifications>({
  scanComplete: true,
  pingAbnormal: true,
  systemStatus: false,
  achievement: true
})

// 方法

/**
 * 处理头像点击
 */
const handleAvatarClick = (): void => {
  avatarDialogVisible.value = true
}

/**
 * 选择头像
 */
const selectAvatar = (avatar: string): void => {
  userProfile.avatar = avatar
  avatarDialogVisible.value = false
  saveUserProfile()
  ElMessage.success('头像已更新')
}

/**
 * 头像上传前验证
 */
const beforeAvatarUpload = (file: File): boolean => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }

  // 这里可以添加图片上传逻辑
  const reader = new FileReader()
  reader.onload = (e) => {
    userProfile.avatar = e.target?.result as string
    avatarDialogVisible.value = false
    saveUserProfile()
    ElMessage.success('头像已上传')
  }
  reader.readAsDataURL(file)
  
  return false // 阻止自动上传
}

/**
 * 记录快捷键
 */
const recordHotkey = (key: string): void => {
  recordingKey.value = key
  const keys: string[] = []
  
  const handleKeyDown = (e: KeyboardEvent) => {
    e.preventDefault()
    
    if (e.key === 'Escape') {
      recordingKey.value = null
      document.removeEventListener('keydown', handleKeyDown)
      return
    }
    
    const keyName = getKeyName(e)
    if (keyName && !keys.includes(keyName)) {
      keys.push(keyName)
    }
  }
  
  const handleKeyUp = (e: KeyboardEvent) => {
    e.preventDefault()
    
    if (keys.length > 0) {
      shortcuts[key].keys = [...keys]
      saveShortcuts()
      ElMessage.success('快捷键已设置')
    }
    
    recordingKey.value = null
    document.removeEventListener('keydown', handleKeyDown)
    document.removeEventListener('keyup', handleKeyUp)
  }
  
  document.addEventListener('keydown', handleKeyDown)
  document.addEventListener('keyup', handleKeyUp)
}

/**
 * 获取按键名称
 */
const getKeyName = (e: KeyboardEvent): string => {
  const modifiers = []
  if (e.ctrlKey) modifiers.push('Ctrl')
  if (e.altKey) modifiers.push('Alt')
  if (e.shiftKey) modifiers.push('Shift')
  if (e.metaKey) modifiers.push('Meta')
  
  const key = e.key
  if (key.length === 1) {
    modifiers.push(key.toUpperCase())
  } else {
    modifiers.push(key)
  }
  
  return modifiers.join('+')
}

/**
 * 格式化快捷键显示
 */
const formatHotkey = (keys: string[]): string => {
  return keys.join('+')
}

/**
 * 清除快捷键
 */
const clearHotkey = (key: string): void => {
  shortcuts[key].keys = []
  saveShortcuts()
  ElMessage.info('快捷键已清除')
}

/**
 * 导出设置
 */
const exportSettings = (): void => {
  const settings = {
    userProfile,
    shortcuts,
    notifications,
    exportTime: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(settings, null, 2)], {
    type: 'application/json'
  })
  
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `nettools-settings-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('设置已导出')
}

/**
 * 导入设置
 */
const importSettings = (): void => {
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
      const settings = JSON.parse(e.target?.result as string)
      
      if (settings.userProfile) {
        Object.assign(userProfile, settings.userProfile)
      }
      if (settings.shortcuts) {
        Object.assign(shortcuts, settings.shortcuts)
      }
      if (settings.notifications) {
        Object.assign(notifications, settings.notifications)
      }
      
      saveAllSettings()
      ElMessage.success('设置已导入')
    } catch (error) {
      ElMessage.error('文件格式错误')
    }
  }
  reader.readAsText(file)
}

/**
 * 重置设置
 */
const resetSettings = async (): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置吗？此操作不可恢复。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 重置为默认值
    Object.assign(userProfile, {
      avatar: '',
      nickname: '网络管理员',
      email: '',
      bio: ''
    })
    
    Object.assign(notifications, {
      scanComplete: true,
      pingAbnormal: true,
      systemStatus: false,
      achievement: true
    })
    
    // 重置快捷键
    Object.keys(shortcuts).forEach(key => {
      shortcuts[key].keys = []
    })
    
    saveAllSettings()
    ElMessage.success('设置已重置')
  } catch {
    // 用户取消
  }
}

/**
 * 清除所有数据
 */
const clearAllData = async (): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有数据吗？包括设置、历史记录等，此操作不可恢复。',
      '确认清除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    localStorage.clear()
    ElMessage.success('所有数据已清除')
    
    // 刷新页面
    setTimeout(() => {
      window.location.reload()
    }, 1000)
  } catch {
    // 用户取消
  }
}

/**
 * 获取存储大小
 */
const getStorageSize = (): number => {
  let total = 0
  for (const key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length
    }
  }
  return total
}

/**
 * 格式化数据大小
 */
const formatDataSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 保存用户信息
 */
const saveUserProfile = (): void => {
  localStorage.setItem('user-profile', JSON.stringify(userProfile))
}

/**
 * 保存快捷键设置
 */
const saveShortcuts = (): void => {
  localStorage.setItem('shortcuts', JSON.stringify(shortcuts))
}

/**
 * 保存通知设置
 */
const saveNotificationSettings = (): void => {
  localStorage.setItem('notifications', JSON.stringify(notifications))
}

/**
 * 保存所有设置
 */
const saveAllSettings = (): void => {
  saveUserProfile()
  saveShortcuts()
  saveNotificationSettings()
}

/**
 * 加载设置
 */
const loadSettings = (): void => {
  // 加载用户信息
  const savedProfile = localStorage.getItem('user-profile')
  if (savedProfile) {
    Object.assign(userProfile, JSON.parse(savedProfile))
  }
  
  // 加载快捷键
  const savedShortcuts = localStorage.getItem('shortcuts')
  if (savedShortcuts) {
    Object.assign(shortcuts, JSON.parse(savedShortcuts))
  }
  
  // 加载通知设置
  const savedNotifications = localStorage.getItem('notifications')
  if (savedNotifications) {
    Object.assign(notifications, JSON.parse(savedNotifications))
  }
  
  // 加载最后备份时间
  lastBackupTime.value = localStorage.getItem('last-backup-time') || ''
}

// 生命周期
onMounted(() => {
  loadSettings()
})

// 暴露方法给父组件
defineExpose({
  exportSettings,
  importSettings,
  resetSettings
})
</script>

<style scoped>
.user-preferences {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 设置区块 */
.preference-section {
  background: var(--bg-dark);
  border: var(--pixel-border);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--pixel-shadow);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px 0;
  color: var(--pixel-primary);
  font-size: var(--font-size-lg);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 个人信息设置 */
.profile-settings {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.avatar-container {
  position: relative;
  cursor: pointer;
}

.user-avatar {
  border: 2px solid var(--pixel-primary);
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
  transition: all var(--animation-speed-fast) ease;
}

.user-avatar:hover {
  box-shadow: 0 0 25px rgba(0, 255, 65, 0.5);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--animation-speed-fast) ease;
  border-radius: 50%;
  color: var(--pixel-primary);
  font-size: var(--font-size-xs);
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.profile-form {
  flex: 1;
}

/* 头像选择 */
.avatar-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.avatar-option {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--animation-speed-fast) ease;
}

.avatar-option:hover {
  border-color: var(--pixel-primary);
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
}

.avatar-option.active {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}

.upload-section {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid var(--pixel-primary);
}

/* 快捷键设置 */
.hotkey-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hotkey-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-darker);
  border: 1px solid var(--pixel-primary);
  border-radius: 6px;
  transition: all var(--animation-speed-fast) ease;
}

.hotkey-item:hover {
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
}

.hotkey-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hotkey-label {
  color: var(--text-primary);
  font-weight: 500;
}

.hotkey-desc {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.hotkey-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hotkey-tag {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  border: none;
}

/* 通知设置 */
.notification-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-darker);
  border: 1px solid var(--pixel-primary);
  border-radius: 6px;
  transition: all var(--animation-speed-fast) ease;
}

.notification-item:hover {
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
}

.notification-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notification-label {
  color: var(--text-primary);
  font-weight: 500;
}

.notification-desc {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

/* 数据管理 */
.data-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.data-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.data-info {
  display: flex;
  gap: 24px;
  padding: 16px;
  background: var(--bg-darker);
  border: 1px solid var(--pixel-primary);
  border-radius: 6px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.info-value {
  color: var(--pixel-primary);
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-settings {
    flex-direction: column;
    align-items: center;
  }
  
  .avatar-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .hotkey-item,
  .notification-item {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .hotkey-input {
    justify-content: center;
  }
  
  .data-actions {
    flex-direction: column;
  }
  
  .data-info {
    flex-direction: column;
    gap: 12px;
  }
}

/* Element Plus覆盖 */
.pixel-dialog :deep(.el-dialog) {
  background: var(--bg-darker);
  border: var(--pixel-border);
}

.pixel-dialog :deep(.el-dialog__header) {
  background: var(--bg-dark);
  color: var(--text-primary);
  border-bottom: 1px solid var(--pixel-primary);
}

.pixel-form :deep(.el-form-item__label) {
  color: var(--text-primary);
}

.pixel-input :deep(.el-input__wrapper) {
  background: var(--bg-darker);
  border: 1px solid var(--pixel-primary);
  box-shadow: none;
}

.pixel-input :deep(.el-input__inner) {
  color: var(--text-primary);
  background: transparent;
}

.pixel-textarea :deep(.el-textarea__inner) {
  background: var(--bg-darker);
  border: 1px solid var(--pixel-primary);
  color: var(--text-primary);
}

.pixel-switch :deep(.el-switch__core) {
  border: 1px solid var(--pixel-primary);
  background: var(--bg-dark);
}

.pixel-switch.is-checked :deep(.el-switch__core) {
  background: var(--pixel-primary);
}

.pixel-tag {
  background: var(--pixel-primary);
  color: var(--bg-dark);
  border: none;
}
</style> 