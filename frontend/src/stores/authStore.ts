import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/axios'
import { AxiosError } from 'axios'

interface LoginForm {
  username: string
  password: string
}

interface SignupForm {
  username: string
  email: string
  password: string
  password_confirm: string
  nickname: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const nickname = ref(localStorage.getItem('nickname') || '')
  const userId = ref(localStorage.getItem('userId') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  const isAuthenticated = computed(() => !!token.value)

  const initializeUserData = async () => {
    if (token.value) {
      try {
        const response = await api.get('/api/accounts/profile/')
        user.value = response.data
        nickname.value = response.data.nickname
        username.value = response.data.username
        userId.value = response.data.id.toString()
        localStorage.setItem('user', JSON.stringify(response.data))
        localStorage.setItem('nickname', response.data.nickname)
        localStorage.setItem('username', response.data.username)
        localStorage.setItem('userId', response.data.id.toString())
      } catch (error) {
        console.error('사용자 정보 초기화 실패:', error)
        logout()
      }
    }
  }

  if (token.value && !user.value) {
    initializeUserData()
  }

  const login = async (loginForm: LoginForm) => {
    try {
      const response = await api.post('/api/accounts/login/', loginForm)
      if (response.data.token) {
        token.value = response.data.token
        user.value = response.data.user
        username.value = response.data.user.username
        nickname.value = response.data.user.nickname
        userId.value = response.data.user.id.toString()
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        localStorage.setItem('username', response.data.user.username)
        localStorage.setItem('nickname', response.data.user.nickname)
        localStorage.setItem('userId', response.data.user.id.toString())
      }
    } catch (error) {
      console.error('로그인 실패:', error)
      throw error
    }
  }

  const signup = async (signupForm: SignupForm) => {
    try {
      const response = await api.post('/api/accounts/signup/', signupForm)
      if (response.data.token) {
        token.value = response.data.token
        username.value = response.data.user.username
        nickname.value = response.data.user.nickname
        user.value = response.data.user
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('username', response.data.user.username)
        localStorage.setItem('nickname', response.data.user.nickname)
      } else {
        throw new Error('인증 토큰이 없습니다.')
      }
    } catch (error) {
      if (error instanceof AxiosError) {
        const errorData = error.response?.data
        if (typeof errorData === 'object') {
          const messages = Object.values(errorData).flat()
          throw new Error(messages.join('\n'))
        }
        throw new Error(errorData?.detail || '회원가입에 실패했습니다.')
      }
      throw error
    }
  }

  const logout = async () => {
    try {
      await api.post('/api/accounts/logout/')
    } finally {
      token.value = ''
      username.value = ''
      nickname.value = ''
      userId.value = ''
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('nickname')
      localStorage.removeItem('userId')
      localStorage.removeItem('user')
    }
  }

  const updateNickname = (newNickname: string) => {
    nickname.value = newNickname
    localStorage.setItem('nickname', newNickname)
  }

  return {
    token,
    username,
    nickname,
    userId,
    user,
    isAuthenticated,
    login,
    signup,
    logout,
    updateNickname
  }
})