import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'

axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.withCredentials = true // 403 에러 해결 위해 추가

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
