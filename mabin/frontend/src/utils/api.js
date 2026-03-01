import axios from 'axios'
import { useUserStore } from '@/stores/user'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response,
  async error => {
    const userStore = useUserStore()
    
    if (error.response?.status === 401) {
      // Token过期，尝试刷新
      if (userStore.refreshToken) {
        try {
          const response = await axios.post(`${api.defaults.baseURL}/auth/refresh/`, {
            refresh: userStore.refreshToken
          })
          userStore.token = response.data.access
          localStorage.setItem('token', userStore.token)
          
          // 重试原请求
          error.config.headers.Authorization = `Bearer ${userStore.token}`
          return axios.request(error.config)
        } catch (refreshError) {
          // 刷新失败，跳转登录
          userStore.logout()
          router.push('/login')
          return Promise.reject(refreshError)
        }
      } else {
        userStore.logout()
        router.push('/login')
        return Promise.reject(new Error('No refresh token'))
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
