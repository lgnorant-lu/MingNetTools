import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: {
        title: '控制台',
        icon: 'Monitor'
      }
    },
    {
      path: '/scan',
      name: 'scan',
      component: () => import('../views/ScanToolsView.vue'),
      meta: {
        title: '端口扫描',
        icon: 'Search'
      }
    },
    {
      path: '/ping',
      name: 'ping',
      component: () => import('../views/PingMonitorView.vue'),
      meta: {
        title: 'PING监控',
        icon: 'Connection'
      }
    },
    {
      path: '/tcp',
      name: 'tcp',
      component: () => import('../views/ConnectionLabView.vue'),
      meta: {
        title: 'TCP通信',
        icon: 'Link'
      }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: {
        title: '系统设置',
        icon: 'Setting'
      }
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: {
        title: '首页',
        icon: 'House'
      }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: {
        title: '关于',
        icon: 'InfoFilled'
      }
    },
    // 重定向处理
    {
      path: '/dashboard',
      redirect: '/'
    }
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 网络安全平台`
  } else {
    document.title = '网络安全平台'
  }
  next()
})

export default router
