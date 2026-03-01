import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const user = ref(null)

  const isAuthenticated = ref(!!token.value)

  const login = async (username, password) => {
    try {
      const response = await api.post('/users/login/', { username, password })
      token.value = response.data.access
      refreshToken.value = response.data.refresh
      user.value = response.data.user
      isAuthenticated.value = true
      
      localStorage.setItem('token', token.value)
      localStorage.setItem('refreshToken', refreshToken.value)
      
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || '登录失败' }
    }
  }

  const logout = () => {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/users/me/')
      user.value = response.data
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || '获取用户信息失败' }
    }
  }

  return {
    token,
    refreshToken,
    user,
    isAuthenticated,
    login,
    logout,
    fetchUserInfo
  }
})
