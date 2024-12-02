<template>
  <div class="auth-container">
    <!-- 로그인/회원가입 버튼 -->
    <div class="auth-buttons" v-if="!isAuthenticated">
      <button @click="showLoginModal">로그인</button> |
      <button @click="showSignupModal">회원가입</button>
    </div>
    <div class="auth-buttons" v-else>
      <router-link to="/profile" class="profile-link">마이페이지</router-link> |
      <button @click="handleLogout">로그아웃</button>
    </div>

    <!-- 통합 인증 모달 -->
    <div v-if="isModalOpen" class="modal">
      <div class="modal-content">
        <!-- 탭 메뉴 -->
        <div class="auth-tabs">
          <button 
            :class="{ active: activeTab === 'login' }" 
            @click="activeTab = 'login'"
          >
            로그인
          </button>
          <button 
            :class="{ active: activeTab === 'signup' }" 
            @click="activeTab = 'signup'"
          >
            회원가입
          </button>
        </div>

        <!-- 로그인 폼 -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin">
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          <div class="input-group">
            <input 
              type="text" 
              v-model="loginForm.username" 
              placeholder="아이디" 
              required
            >
          </div>
          <div class="input-group password-group">
            <input 
              :type="showLoginPassword ? 'text' : 'password'" 
              v-model="loginForm.password" 
              placeholder="비밀번호" 
              required
            >
            <button 
              type="button" 
              class="toggle-password"
              @click="showLoginPassword = !showLoginPassword"
            >
              <i :class="showLoginPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <button type="submit">로그인</button>
        </form>

        <!-- 회원가입 폼 -->
        <form v-else @submit.prevent="handleSignup">
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          <div class="input-group">
            <input 
              type="text" 
              v-model="signupForm.username" 
              placeholder="아이디" 
              required
            >
          </div>
          <div class="input-group">
            <input 
              type="email" 
              v-model="signupForm.email" 
              placeholder="이메일" 
              required
            >
          </div>
          <div class="input-group">
            <input 
              type="text" 
              v-model="signupForm.nickname" 
              placeholder="닉네임" 
              required
            >
          </div>
          <div class="input-group password-group">
            <input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="signupForm.password" 
              placeholder="비밀번호" 
              required
            >
            <button 
              type="button" 
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <div class="input-group password-group">
            <input 
              :type="showConfirmPassword ? 'text' : 'password'" 
              v-model="signupForm.password_confirm" 
              placeholder="비밀번호 확인" 
              required
            >
            <button 
              type="button" 
              class="toggle-password"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <button type="submit" class="submit-button">가입하기</button>
        </form>

        <button class="close-button" @click="closeModal">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue' 
import { useAuthStore } from '@/stores/authStore' 

const authStore = useAuthStore()
const isModalOpen = ref(false)
const activeTab = ref('login')

const loginForm = ref({
  username: '',
  password: ''
})

const signupForm = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  nickname: ''
})

const isAuthenticated = computed(() => {
  return !!authStore.token && !!authStore.username
})

const errorMessage = ref('')

const showLoginModal = () => {
  isModalOpen.value = true
  activeTab.value = 'login'
}

const showSignupModal = () => {
  isModalOpen.value = true
  activeTab.value = 'signup'
}

const closeModal = () => {
  isModalOpen.value = false
  activeTab.value = 'login'
  loginForm.value = { username: '', password: '' }
  signupForm.value = { username: '', email: '', password: '', password_confirm: '', nickname: '' }
}

const handleLogin = async () => {
  try {
    errorMessage.value = ''
    await authStore.login(loginForm.value)
    closeModal()
    window.location.reload()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '로그인에 실패했습니다.'
    loginForm.value = { username: '', password: '' }
  }
}

const handleSignup = async () => {
  try {
    errorMessage.value = ''
    await authStore.signup(signupForm.value)
    closeModal()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '회원가입에 실패했습니다.'
    signupForm.value = { username: '', email: '', password: '', password_confirm: '', nickname: '' }
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    window.location.reload()
  } catch (error) {
    console.error('로그아웃 실패:', error)
  }
}

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const showLoginPassword = ref(false)
</script>

<style lang="scss" scoped>
.auth-container {
  .auth-buttons {
    display: flex;
    gap: 0.5rem;
    align-items: center;

    button, .profile-link {
      background: none;
      border: none;
      color: #2c3e50;
      font-size: 0.9rem;
      padding: 0.5rem 1rem;
      cursor: pointer;
      transition: all 0.3s ease;
      border-radius: 8px;

      &:hover {
        background: #f8f9fa;
        color: #34495e;
      }
    }

    .profile-link {
      text-decoration: none;
      
      &:hover {
        text-decoration: none;
      }
    }
  }
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.auth-tabs {
  display: flex;
  margin-bottom: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 0.3rem;
  gap: 0.3rem;

  button {
    flex: 1;
    padding: 0.8rem;
    border: none;
    background: none;
    cursor: pointer;
    border-radius: 6px;
    color: #666;
    transition: all 0.3s ease;
    
    &.active {
      background: white;
      color: #2c3e50;
      font-weight: 600;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    &:hover:not(.active) {
      background: rgba(255, 255, 255, 0.5);
    }
  }
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 100%;

  input {
    width: 100%;
    box-sizing: border-box;
    padding: 0.8rem 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    transition: all 0.3s ease;
    font-size: 0.95rem;

    &:focus {
      outline: none;
      border-color: #2c3e50;
      box-shadow: 0 0 0 2px rgba(44, 62, 80, 0.1);
    }
  }

  button {
    padding: 0.8rem;
    background: #2c3e50;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;

    &:hover {
      background: #34495e;
      transform: translateY(-1px);
    }
  }
}

.close-button {
  width: 100%;
  margin-top: 1.5rem;
  padding: 0.8rem;
  border: none;
  background: #f8f9fa;
  color: #2c3e50;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #e9ecef;
  }
}

.error-message {
  background: #fff5f5;
  color: #e53e3e;
  padding: 0.8rem;
  border-radius: 8px;
  text-align: center;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.input-group {
  position: relative;
  width: 100%;

  input {
    width: 100%;
    box-sizing: border-box;
  }

  &.password-group {
    position: relative;
    width: 100%;

    input {
      padding-right: 40px;
      width: 100%;
    }

    .toggle-password {
      position: absolute;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: #666;
      cursor: pointer;
      padding: 5px;
      transition: color 0.3s ease;
      z-index: 2;

      &:hover {
        color: #2c3e50;
      }

      i {
        font-size: 1.1rem;
      }
    }
  }
}

.submit-button {
  background: #2c3e50 !important; // KB 스타일 노란색
  color: white !important;
  font-weight: bold !important;
  margin-top: 1rem;

  &:hover {
    background: #34495e !important;
    transform: translateY(-1px);
  }
}

// Font Awesome 아이콘을 위한 CDN 추가 필요
// index.html에 추가:
// <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
</style>