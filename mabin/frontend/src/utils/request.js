/**
 * 请求工具（增强版）
 */
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建axios实例
const service = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    
    // 添加token
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    
    // 添加请求时间戳（防止缓存）
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果返回的是文件流，直接返回
    if (response.config.responseType === 'blob') {
      return response
    }
    
    // 根据业务状态码处理
    if (res.code !== undefined && res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  async error => {
    const userStore = useUserStore()
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Token过期，尝试刷新
          if (userStore.refreshToken && !error.config._retry) {
            error.config._retry = true
            
            try {
              const response = await axios.post('http://localhost:8000/api/auth/refresh/', {
                refresh: userStore.refreshToken
              })
              
              userStore.token = response.data.access
              localStorage.setItem('token', userStore.token)
              
              // 重试原请求
              error.config.headers.Authorization = `Bearer ${userStore.token}`
              return service.request(error.config)
            } catch (refreshError) {
              // 刷新失败，跳转登录
              userStore.logout()
              router.push('/login')
              ElMessage.error('登录已过期，请重新登录')
              return Promise.reject(refreshError)
            }
          } else {
            userStore.logout()
            router.push('/login')
            ElMessage.error('请先登录')
          }
          break
          
        case 403:
          ElMessage.error('没有权限访问')
          break
          
        case 404:
          ElMessage.error('请求的资源不存在')
          break
          
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
          
        case 502:
        case 503:
        case 504:
          ElMessage.error('服务暂时不可用，请稍后重试')
          break
          
        default:
          ElMessage.error(data?.message || data?.error || `请求失败 (${status})`)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error(error.message || '请求失败')
    }
    
    return Promise.reject(error)
  }
)

export default service
