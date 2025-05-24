<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { 
  Fold, 
  Expand,
  Monitor,
  Search,
  Connection,
  Link,
  House,
  InfoFilled,
  User,
  ArrowDown,
  Setting,
  Document,
  SwitchButton,
  CircleCheckFilled,
  CircleCloseFilled,
  Close,
  Menu
} from '@element-plus/icons-vue'
import PixelPet from './components/common/PixelPet.vue'
import ThemeToggle from './components/common/ThemeToggle.vue'
import LanguageToggle from './components/common/LanguageToggle.vue'
import MingEasterEgg from './components/common/MingEasterEgg.vue'
import { useThemeStore } from './stores/theme'
import { useFontStore } from './stores/font'
import { useI18nStore } from './stores/i18n'

const route = useRoute()
const pixelPetRef = ref()
const themeStore = useThemeStore()
const fontStore = useFontStore()
const i18nStore = useI18nStore()

// 侧边栏状态
const sidebarCollapsed = ref(false)
const mobileDrawerVisible = ref(false)

// 系统状态
const apiStatus = ref(true)
const networkStatus = ref(true)

// 响应式状态
const isMobile = ref(false)

// 计算属性
const currentRoute = computed(() => route.path)
const currentRouteMeta = computed(() => route.meta)

// 页面标题映射
const pageTitle = computed(() => {
  const path = route.path
  switch (path) {
    case '/dashboard':
      return i18nStore.t('nav.dashboard')
    case '/scan':
      return i18nStore.t('nav.scan')
    case '/ping':
      return i18nStore.t('nav.ping')
    case '/tcp':
      return i18nStore.t('nav.tcp')
    case '/settings':
      return i18nStore.t('nav.settings')
    default:
      return 'NetTools'
  }
})

// 方法
const toggleSidebar = () => {
  if (isMobile.value) {
    mobileDrawerVisible.value = !mobileDrawerVisible.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

const closeMobileDrawer = () => {
  mobileDrawerVisible.value = false
}

// 检查是否为移动端
const checkIfMobile = () => {
  isMobile.value = window.innerWidth <= 768
  if (isMobile.value) {
    sidebarCollapsed.value = false
  }
}

// 模拟系统状态检查
const checkSystemStatus = () => {
  // 这里将来会调用真实的API检查
  apiStatus.value = Math.random() > 0.1 // 90% 正常
  networkStatus.value = navigator.onLine
}

// 检测屏幕尺寸
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

// 组件挂载
onMounted(() => {
  // 初始化主题系统
  themeStore.initTheme()
  
  // 初始化字体系统
  fontStore.initFontSystem()
  
  // 初始化语言系统
  i18nStore.initI18n()
  
  // 初始化动画系统
  import('./stores/animation').then(({ useAnimationStore }) => {
    const animationStore = useAnimationStore()
    animationStore.initAnimationSystem()
  })
  
  checkSystemStatus()
  checkIfMobile()
  
  // 定期检查系统状态
  setInterval(checkSystemStatus, 30000) // 每30秒检查一次
  
  // 监听窗口大小变化
  window.addEventListener('resize', checkIfMobile)
  
  // 监听网络状态变化
  window.addEventListener('online', () => {
    networkStatus.value = true
  })
  
  window.addEventListener('offline', () => {
    networkStatus.value = false
  })

  checkMobile()
  window.addEventListener('resize', checkMobile)
  
  // 发送系统状态给宠物
  const emitSystemStatus = (status: string) => {
    window.dispatchEvent(new CustomEvent('system-status-change', {
      detail: { status }
    }))
  }
  
  // 示例：监听路由变化，让宠物响应
  route.path && emitSystemStatus('ready')
})
</script>

<template>
  <div id="app" class="scanlines">
    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside width="250px" class="sidebar pixel-sidebar">
        <div class="logo-section">
          <div class="logo glitch-text" data-text="NETTOOLS">
            NETTOOLS
          </div>
          <div class="subtitle">网络安全工具平台</div>
        </div>
        
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu pixel-menu"
          router
          background-color="transparent"
          text-color="var(--pixel-primary)"
          active-text-color="var(--neon-cyan)"
        >
          <el-menu-item index="/dashboard" class="pixel-menu-item">
            <el-icon><Monitor /></el-icon>
            <span>{{ i18nStore.t('nav.dashboard') }}</span>
          </el-menu-item>
          <el-menu-item index="/scan" class="pixel-menu-item">
            <el-icon><Search /></el-icon>
            <span>{{ i18nStore.t('nav.scan') }}</span>
          </el-menu-item>
          <el-menu-item index="/ping" class="pixel-menu-item">
            <el-icon><Connection /></el-icon>
            <span>{{ i18nStore.t('nav.ping') }}</span>
          </el-menu-item>
          <el-menu-item index="/tcp" class="pixel-menu-item">
            <el-icon><Link /></el-icon>
            <span>{{ i18nStore.t('nav.tcp') }}</span>
          </el-menu-item>
          <el-menu-item index="/settings" class="pixel-menu-item">
            <el-icon><Setting /></el-icon>
            <span>{{ i18nStore.t('nav.settings') }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header pixel-header">
          <div class="header-left">
            <h1 class="page-title glitch-text" :data-text="pageTitle">
              {{ pageTitle }}
            </h1>
          </div>
          
          <div class="header-right">
            <!-- 语言切换组件 -->
            <LanguageToggle />
            
            <!-- 主题切换组件 -->
            <ThemeToggle />
            
            <el-dropdown>
              <el-button type="text" class="user-btn pixel-btn">
                <el-icon><User /></el-icon>
                <span v-if="!isMobile">管理员</span>
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu class="pixel-dropdown">
                  <el-dropdown-item>个人设置</el-dropdown-item>
                  <el-dropdown-item>系统设置</el-dropdown-item>
                  <el-dropdown-item divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 页面内容 -->
        <el-main class="main-content pixel-main">
          <Transition name="fade" mode="out-in">
            <router-view />
          </Transition>
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 像素宠物 -->
    <PixelPet ref="pixelPetRef" />
    
    <!-- Ming的神秘彩蛋系统 -->
    <MingEasterEgg />
  </div>
</template>

<style scoped>
.main-container {
  height: 100vh;
  background: var(--bg-dark);
}

/* 像素风格侧边栏 */
.pixel-sidebar {
  background: linear-gradient(180deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
  border-right: var(--pixel-border);
  box-shadow: 2px 0 10px rgba(0, 255, 65, 0.1);
}

.logo-section {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid var(--pixel-primary);
  margin-bottom: 20px;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: var(--pixel-primary);
  margin-bottom: 8px;
  text-shadow: 0 0 10px var(--pixel-primary);
}

.subtitle {
  font-size: 8px;
  color: var(--pixel-accent);
  opacity: 0.8;
}

/* 像素风格菜单 */
.pixel-menu {
  border: none !important;
  background: transparent !important;
}

.pixel-menu-item {
  margin: 8px 16px;
  border-radius: 4px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  font-size: 12px;
}

.pixel-menu-item:hover {
  background: rgba(0, 255, 65, 0.1) !important;
  border-color: var(--pixel-primary);
  box-shadow: inset 0 0 10px rgba(0, 255, 65, 0.2);
}

.pixel-menu-item.is-active {
  background: rgba(0, 212, 255, 0.2) !important;
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

/* 像素风格头部 */
.pixel-header {
  background: var(--bg-darker);
  border-bottom: var(--pixel-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 10px rgba(0, 255, 65, 0.1);
}

.page-title {
  font-size: 16px;
  margin: 0;
  color: var(--pixel-primary);
  text-shadow: 0 0 10px var(--pixel-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-btn {
  color: var(--pixel-accent) !important;
  border: 1px solid var(--pixel-accent);
  padding: 8px 12px;
  font-size: 10px;
}

.user-btn:hover {
  background: var(--pixel-accent) !important;
  color: var(--bg-dark) !important;
  box-shadow: 0 0 10px var(--pixel-accent);
}

/* 像素风格主内容 */
.pixel-main {
  background: var(--bg-dark);
  padding: 24px;
  overflow-y: auto;
}

/* 下拉菜单像素风格 */
.pixel-dropdown {
  background: var(--bg-dark) !important;
  border: var(--pixel-border) !important;
  box-shadow: 0 4px 20px rgba(0, 255, 65, 0.2) !important;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pixel-sidebar {
    width: 200px !important;
  }
  
  .logo {
    font-size: 14px;
  }
  
  .subtitle {
    font-size: 7px;
  }
  
  .pixel-menu-item {
    margin: 6px 12px;
    font-size: 10px;
  }
  
  .page-title {
    font-size: 14px;
  }
  
  .pixel-main {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .pixel-sidebar {
    width: 180px !important;
  }
  
  .header-right span {
    display: none;
  }
}
</style>

    display: none;