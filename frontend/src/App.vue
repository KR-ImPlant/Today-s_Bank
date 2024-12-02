<template>
  <header class="nav-bar">
    <!-- 웹사이트 메인 로고와 환영 메시지 영역 -->
    <div class="logo-welcome">
      <div class="logo">
        <router-link to="/">
          <img src="/public/오늘의_은행_로고-removebg-preview.png" alt="오늘의 은행 로고">
        </router-link>
      </div>
      <div v-if="isAuthenticated" class="welcome-message">
        {{ nickname }}님 환영합니다
      </div>
    </div>

    <!-- 모바일 화면에서만 보이는 메뉴 토글 버튼 -->
    <button class="menu-toggle" @click="toggleMenu">
      <span v-if="!menuOpen">☰</span>
      <span v-else>✖</span>
    </button>

    <!-- 메인 네비게이션 영역 -->
    <nav :class="{ 'menu-open': menuOpen }">
      <ul class="nav-menu">
        <!-- 각 메뉴 항목들. 클릭 시 closeMenu 함수 실행 -->
        <li><router-link :to="{ name: 'home' }" @click="closeMenu">홈</router-link></li>
        <li><router-link :to="{ name: 'product' }" @click="closeMenu">예적금</router-link></li>
        <li><router-link :to="{ name: 'exchange-calculator' }" @click="closeMenu">환율</router-link></li>
        <li><router-link :to="{ name: 'bank-map' }" @click="closeMenu">지도</router-link></li>
        <li><router-link :to="{ name: 'community' }" @click="closeMenu">게시판</router-link></li>
        <li><router-link :to="{ name: 'recommendation' }" @click="closeMenu">상품 추천</router-link></li>
      </ul>
    </nav>

    <!-- 로그인/회원가입 버튼 영역 (모바일에서는 숨겨짐) -->
    <div class="user-actions">
      <Auth />
    </div>
  </header>
  <div class="main-content">
    <router-view />
  </div>
  <div class="floating-menu">
    <button class="floating-button" @click="toggleBanners">
      <i :class="['fas', bannerOpen ? 'fa-times' : 'fa-plus']"></i>
    </button>
    
    <div class="banner-container" :class="{ 'open': bannerOpen }">
      <router-link to="/product" class="banner" @click="closeBanners">
        <div class="banner-content">
          <i class="fas fa-store"></i>
          <span>상품</span>
        </div>
      </router-link>

      <router-link to="/map" class="banner" @click="closeBanners">
        <div class="banner-content">
          <i class="fas fa-map-marker-alt"></i>
          <span>지도</span>
        </div>
      </router-link>

      <router-link to="/community" class="banner" @click="closeBanners">
        <div class="banner-content">
          <i class="fas fa-comments"></i>
          <span>게시판</span>
        </div>
      </router-link>

      <router-link to="/recommendation" class="banner" @click="closeBanners">
        <div class="banner-content">
          <i class="fas fa-thumbs-up"></i>
          <span>추천</span>
        </div>
      </router-link>
    </div>
  </div>
  <!-- 스크롤 상단 이동 버튼 -->
  <button 
    v-show="showScrollTop" 
    @click="scrollToTop" 
    class="scroll-top-button"
    :class="{ 'show': showScrollTop }"
  >
    <i class="fas fa-arrow-up"></i>
  </button>
</template>

<script lang="ts">
import { RouterView } from 'vue-router'
import Auth from '@/components/common/Auth.vue'
import { defineComponent, ref, onMounted, onUnmounted, computed } from 'vue';
import { useAuthStore } from '@/stores/authStore'

export default defineComponent({
  components: {
    Auth
  },
  setup() {
    const menuOpen = ref(false);
    const isMobile = ref(window.innerWidth < 768);
    const authStore = useAuthStore();
    
    // authStore 디버깅을 위한 console.log 추가
    console.log('전체 authStore:', authStore);
    console.log('인증 상태:', authStore.isAuthenticated);
    console.log('닉네임:', authStore.nickname);
    console.log('사용자 정보:', authStore.user);

    const isAuthenticated = computed(() => {
        console.log('computed isAuthenticated 실행:', authStore.isAuthenticated);
        return authStore.isAuthenticated;
    });
    
    const nickname = computed(() => {
        console.log('computed nickname 실행:', authStore.nickname);
        return authStore.nickname;
    });

    // 메뉴 토글 함수: 열림/닫힘 상태 전환
    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value;
    };

    // 메뉴 닫기 함수: 메뉴 항목 클릭 시 호출
    const closeMenu = () => {
      menuOpen.value = false;
    };

    // 화면 크기 변경 감지 함수
    const handleResize = () => {
      const nowMobile = window.innerWidth < 855;
      // 데스크톱 모드로 전환 시 메뉴 자동 닫기
      if (!nowMobile) {
        menuOpen.value = false;
      }
      isMobile.value = nowMobile;
    };

    // 컴포넌트 마운트 시 리사이즈 이벤트 리스너 등록
    onMounted(() => {
      window.addEventListener('resize', handleResize);
    });

    // 컴포넌트 언마운트 시 이벤트 리스너 제거 (메모리 누수 방지)
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize);
    });

    const bannerOpen = ref(false);

    const toggleBanners = () => {
      bannerOpen.value = !bannerOpen.value;
    };

    const closeBanners = () => {
      bannerOpen.value = false;
    };

    const showScrollTop = ref(false);

    // 스크롤 위치 감지
    const handleScroll = () => {
      showScrollTop.value = window.scrollY > 200;
    };

    // 최상단으로 스크롤
    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    };

    // 이벤트 리스너 등록/해제
    onMounted(() => {
      window.addEventListener('scroll', handleScroll);
    });

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll);
    });

    // 페이지 새로고침 감지를 위한 변수
    let isRefreshing = false;

    // 새로고침 감지
    window.onkeydown = (e) => {
      if ((e.key === 'F5') || ((e.ctrlKey || e.metaKey) && e.key === 'r')) {
        isRefreshing = true;
      }
    };

    // 마우스 클릭 새로고침 감지
    window.addEventListener('click', (e) => {
      // @ts-ignore - 타입스크립트에서 path 프로퍼티를 인식하지 못하는 경우를 위한 처리
      const path = e.path || (e.composedPath && e.composedPath());
      // 새로고침 버튼이 클릭되었는지 확인
      if (path.some((element: any) => 
        element.className && 
        typeof element.className === 'string' && 
        element.className.includes('reload'))) {
        isRefreshing = true;
      }
    });

    // beforeunload 이벤트만 사용하여 브라우저/탭 종료 시에만 로그아웃
    const handleBeforeUnload = async (e: BeforeUnloadEvent) => {
      const isRefresh = performance.navigation.type === 1;
      
      if (!isRefresh && authStore.isAuthenticated) {
        e.preventDefault()
        await authStore.logout()
      }
    }

    onMounted(() => {
      window.addEventListener('beforeunload', handleBeforeUnload)
    })

    onUnmounted(() => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    })

    return { 
      menuOpen, 
      toggleMenu, 
      closeMenu, 
      isMobile,
      isAuthenticated,
      nickname,
      bannerOpen,
      toggleBanners,
      closeBanners,
      showScrollTop,
      scrollToTop
    };
  },
});
</script>

<style lang="scss" scoped>
/* 전체 네비게이션 바 컨테이너 */
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  z-index: 1000;
  display: grid;
  grid-template-columns: 300px 1fr 200px;  // 로고+환영 메시지 영역 확장
  align-items: center;
  padding: 0 2rem;
  box-sizing: border-box;

  .logo-welcome {
    display: flex;
    align-items: center;
    gap: 1rem;
    min-width: 300px;  // 최소 너비 설정
    
    .logo {
      img {
        height: 40px;
        width: auto;
      }
    }

    .welcome-message {
      font-size: 0.9rem;
      color: #666;
      white-space: nowrap;
      margin-left: 1rem;
    }
  }

  nav {
    justify-self: center;
    width: 600px;
    margin: 0 auto;
    
    .nav-menu {
      display: flex;
      justify-content: space-between;
      list-style: none;
      margin: 0;
      padding: 0;
      white-space: nowrap;

      li a {
        color: #8A8A8A;
        text-decoration: none;
        font-size: 1.1rem;
        font-weight: bold;
        transition: color 0.2s;
        padding: 0 1rem;

        &.router-link-active {
          color: #000;
        }

        &:hover {
          color: #007bff;
        }
      }
    }
  }

  .user-actions {
    justify-self: end;
    white-space: nowrap;
  }

  .menu-toggle {
    display: none;
    background: none;
    border: none;
    font-size: 1.8rem;
    cursor: pointer;
    padding: 0.5rem;
    color: #333;
    z-index: 1001;
  }

  @media (max-width: 854px) {
    grid-template-columns: auto auto;
    justify-content: space-between;
    padding: 0 1rem;

    .menu-toggle {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .logo-welcome {
      min-width: auto;
      
      .welcome-message {
        display: none;
      }
    }

    nav {
      display: none;
      
      &.menu-open {
        display: block;
        position: fixed;
        top: 60px;
        left: 0;
        width: 100%;
        background: #fff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1rem 0;
        
        .nav-menu {
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }
      }
    }

    .user-actions {
      display: none;
    }
  }
}

.main-content {
  padding-top: 60px;
  min-height: calc(100vh - 60px);
  background-color: #f1f1f1;
}

.floating-menu {
  position: fixed;
  right: 2rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;

  .floating-button {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #8b8b8b;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    z-index: 1001;
    position: relative;

    &:hover {
      transform: scale(1.1);
      background: #000000;
    }
  }

  .banner-container {
    position: absolute;
    right: 60px;
    top: 50%;
    transform: translateY(-50%) scale(0);
    display: flex;
    flex-direction: column;
    gap: 1rem;
    opacity: 0;
    transition: all 0.3s ease;
    pointer-events: none;

    &.open {
      transform: translateY(-50%) scale(1);
      opacity: 1;
      pointer-events: all;
    }

    .banner {
      background: white;
      border-radius: 12px;
      padding: 1rem;
      text-decoration: none;
      color: #333;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s ease;

      &:hover {
        transform: translateX(-5px);
      }

      .banner-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        i {
          font-size: 1.2rem;
        }

        span {
          font-weight: 500;
        }
      }
    }
  }
}

.scroll-top-button {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #919191;
  color: white;
  border: none;
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;

  &.show {
    opacity: 1;
    visibility: visible;
  }

  &:hover {
    background: #000000;
    transform: translateY(-3px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  }

  i {
    font-size: 1.5rem;
  }
}

@media (max-width: 768px) {
  .scroll-top-button {
    bottom: 1rem;
    right: 1rem;
  }
}
</style>
