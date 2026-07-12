import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { coreService } from './services/api.js'
import { loadBrandingFromApi, getCachedBranding, applyBranding } from './utils/branding.js'

applyBranding(getCachedBranding())
loadBrandingFromApi(coreService)

createApp(App).use(router).mount('#app')
