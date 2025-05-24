import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Element Plus配置
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { initAudioManager } from './utils/audioManager'

const app = createApp(App)

// 注册Element Plus
app.use(ElementPlus)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)

// 初始化音效管理器
initAudioManager().then(() => {
  console.log('Audio Manager initialized')
}).catch(error => {
  console.warn('Audio Manager initialization failed:', error)
})

app.mount('#app')
