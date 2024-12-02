<template>
  <div class="recommendation-container">
    <div v-if="step === 1" class="recommendation-step">
      <h2>투자 목적을 선택해주세요</h2>
      <div class="options-grid">
        <div 
          v-for="option in purposeOptions" 
          :key="option.value"
          @click="selectPurpose(option.value)"
          :class="['option-card', { selected: preference.investment_purpose === option.value }]"
        >
          <div class="icon">{{ option.icon }}</div>
          <div class="label">{{ option.label }}</div>
        </div>
      </div>
    </div>

    <div v-else-if="step === 2" class="recommendation-step">
      <h2>투자 기간을 선택해주세요</h2>
      <div class="options-grid">
        <div 
          v-for="option in periodOptions" 
          :key="option.value"
          @click="selectPeriod(option.value)"
          :class="['option-card', { selected: preference.investment_period === option.value }]"
        >
          <div class="label">{{ option.label }}</div>
        </div>
      </div>
    </div>

    <div v-else-if="step === 3" class="recommendation-step">
      <h2>투자 금액을 입력해주세요</h2>
      <div class="amount-input">
        <input 
          type="number" 
          v-model="preference.investment_amount"
          placeholder="금액을 입력하세요"
        >
        <span>원</span>
      </div>
    </div>

    <div v-else-if="step >= 4 && !recommendationFinished" class="recommendation-step">
      <div class="progress-bar">
        <div class="progress" :style="{ width: `${(currentQuestionIndex + 1) / dynamicQuestions.length * 100}%` }"></div>
      </div>

      <div v-if="currentQuestion" class="dynamic-question">
        <h2>{{ currentQuestion.question_text }}</h2>
        <div class="options-grid">
          <div
            v-for="option in currentQuestion.options"
            :key="option.value"
            @click="selectDynamicOption(option)"
            :class="['option-card', { selected: selectedOption?.value === option.value }]"
          >
            <div class="label">{{ option.text }}</div>
          </div>
        </div>
        
        <div class="question-progress">
          <span>질문 {{ currentQuestionIndex + 1 }} / {{ dynamicQuestions.length }}</span>
          <div class="dots">
            <span 
              v-for="(_, index) in dynamicQuestions" 
              :key="index"
              :class="{ active: index === currentQuestionIndex }"
            ></span>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="$route.path === '/recommendation/result'" class="recommendation-results">
      <div class="results-header">
        <h2>맞춤 금융상품 추천</h2>
        <button class="restart-button" @click="restartRecommendation">
          <i class="fas fa-redo"></i> 다시 추천받기
        </button>
      </div>

      <div class="best-products-grid">
        <div v-for="(product, index) in recommendations.slice(0, 2)" 
             :key="product.fin_prdt_cd"
             class="best-product-card">
          <div class="best-badge">
            <span class="badge-text">BEST {{ index + 1 }}</span>
            <div class="badge-shine"></div>
          </div>
          
          <div class="bank-info">
            <div class="bank-logo-container">
              <img 
                v-if="productStore.bankLogos[formatBankName(product.kor_co_nm)]"
                :src="productStore.bankLogos[formatBankName(product.kor_co_nm)]" 
                :alt="product.kor_co_nm"
                class="bank-logo"
              >
            </div>
            <span class="bank-name">{{ product.kor_co_nm }}</span>
          </div>

          <h3 class="product-name">{{ product.fin_prdt_nm }}</h3>
          
          <div class="highlight-stats">
            <div class="stat-box rate">
              <div class="stat-value">{{ product.max_rate }}%</div>
              <div class="stat-label">최고금리</div>
            </div>
            <div class="stat-box score">
              <div class="stat-value">{{ Math.round(product.score * 100) }}</div>
              <div class="stat-label">추천점수</div>
            </div>
          </div>

          <button 
            class="wish-button"
            @click="toggleWish(product)"
            :class="{ 'wished': isWished(product.fin_prdt_cd) }"
          >
            {{ isWished(product.fin_prdt_cd) ? '찜 취소' : '찜하기' }}
          </button>
        </div>
      </div>

      <div class="other-products-container">
        <h3>추천 상품 리스트</h3>
        <div class="products-list">
          <div v-for="product in recommendations.slice(2)" 
               :key="product.fin_prdt_cd"
               class="product-list-item">
            <div class="product-main-info">
              <div class="bank-logo-container">
                <img 
                  v-if="productStore.bankLogos[formatBankName(product.kor_co_nm)]"
                  :src="productStore.bankLogos[formatBankName(product.kor_co_nm)]" 
                  :alt="product.kor_co_nm"
                  class="bank-logo-small"
                >
              </div>
              <div class="product-details">
                <span class="bank-name">{{ product.kor_co_nm }}</span>
                <h4>{{ product.fin_prdt_nm }}</h4>
              </div>
            </div>
            <div class="product-stats">
              <span class="stat">최고금리 {{ product.max_rate }}%</span>
              <span class="stat-divider">|</span>
              <span class="stat">추천점수 {{ Math.round(product.score * 100) }}</span>
            </div>
            <button 
              class="wish-button-small"
              @click="toggleWish(product)"
              :class="{ 'wished': isWished(product.fin_prdt_cd) }"
            >
              {{ isWished(product.fin_prdt_cd) ? '찜 취소' : '찜하기' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="navigation-buttons">
      <button 
        v-if="step > 1" 
        @click="prevStep"
        class="nav-button"
      >
        이전
      </button>
      <button 
        v-if="!recommendationFinished" 
        @click="nextStep"
        :disabled="!canProceed"
        class="nav-button primary"
      >
        {{ step >= 4 ? '다음 질문' : '다음' }}
      </button>
    </div>

    <div v-if="loading && !recommendationFinished && step === 3" class="loading-overlay">
      <div class="loading-content">
        <img 
          src="/public/오늘의_은행_로고-removebg-preview.png" 
          alt="오늘의 은행 로고" 
          class="loading-logo"
        >
        <h3>AI가 질문을 생성중입니다</h3>
        <div class="loading-bar">
          <div class="loading-progress"></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import Chart from 'chart.js/auto'
import api from "@/utils/axios"
import { formatBankName } from '@/utils/bankNameFormatter';
import { useProductStore } from '@/stores/productStore';

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const productStore = useProductStore();

const step = ref<number | 'result'>(1)
const loading = ref(false)
const recommendations = ref([])
const dynamicQuestions = ref([])
const currentQuestionIndex = ref(0)
const currentQuestion = computed(() => 
  dynamicQuestions.value[currentQuestionIndex.value] || null
)
const selectedOption = ref(null)
const preferenceId = ref(null)
const recommendationFinished = ref(false)

const preference = ref({
  investment_purpose: '',
  investment_period: null,
  investment_amount: null
})

// 옵션 정의
const purposeOptions = ref([
  { value: 'investment', label: '투자', icon: '💰' },
  { value: 'saving', label: '저축', icon: '🏦' },
  { value: 'other', label: '기타', icon: '📊' }
])

const periodOptions = [
  { value: 6, label: '6개월' },
  { value: 12, label: '12개월' },
  { value: 24, label: '24개월' },
  { value: 36, label: '36개월' }
]

// 다음 단계로 진행 가능한지 확인
const canProceed = computed(() => {
  if (step.value === 1) return !!preference.value.investment_purpose
  if (step.value === 2) return !!preference.value.investment_period
  if (step.value === 3) return !!preference.value.investment_amount
  if (step.value >= 4 && !recommendationFinished.value) return !!selectedOption.value
  return false
})

// 선택 함수들
const selectPurpose = (purpose: string) => {
  preference.value.investment_purpose = purpose
}

const selectPeriod = (period: number) => {
  preference.value.investment_period = period
}

const selectDynamicOption = (option: any) => {
  selectedOption.value = option
}

// 다음 단계로 이동
const nextStep = async () => {
  console.log('=== nextStep 시작 ===')
  console.log('현재 step:', step.value)
  console.log('canProceed:', canProceed.value)
  
  if (!canProceed.value) {
    console.log('진행 불가: canProceed가 false')
    return
  }
  
  // step 3 또는 마지막 질문(step 8)일 때 로딩 시작
  if (step.value === 3 || (typeof step.value === 'number' && step.value >= 8)) {
    loading.value = true
  }
  
  try {
    if (step.value === 3) {
      console.log('step 3 처리 시작')
      const response = await axios.post('/api/recommendations/save_preference/', {
        investment_purpose: preference.value.investment_purpose,
        investment_period: preference.value.investment_period,
        investment_amount: preference.value.investment_amount
      }, {
        headers: { 
          Authorization: `Token ${auth.token}`,
          'Content-Type': 'application/json'
        }
      })
      console.log('선호도 저장 응답:', response.data)

      if (response.data.status === 'success') {
        preferenceId.value = response.data.id
        console.log('선호도 ID 설정:', preferenceId.value)
        
        // 의도적인 지연 추가 (1.5초)
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        await loadQuestions()
        console.log('질문 로드 완료, 질문 수:', dynamicQuestions.value.length)
        
        loading.value = false // 질문 로드 완료 후 로딩 종료
        
        step.value = 4
        console.log('step 4로 변경')
        await router.push('/recommendation/4')
        console.log('라우터 이동 완료: /recommendation/4')
      }
    } else if (typeof step.value === 'number' && step.value >= 4 && !recommendationFinished.value) {
      console.log('step 4+ 처리 시작')
      await saveAnswer()
      
      if (currentQuestionIndex.value < dynamicQuestions.value.length - 1) {
        currentQuestionIndex.value++
        selectedOption.value = null
        step.value++
        await router.push(`/recommendation/${step.value}`)
      } else {
        // 마지막 질문 후 처리
        loading.value = true
        await new Promise(resolve => setTimeout(resolve, 1500)) // 의도적 지연
        
        recommendationFinished.value = true
        step.value = 'result'
        await router.push('/recommendation/result')
        await getRecommendations()
        loading.value = false
      }
    } else {
      if (typeof step.value === 'number') {
        step.value++
        await router.push(`/recommendation/${step.value}`)
      }
    }
  } catch (error) {
    console.error('오류 발생:', error)
    alert('처리 중 오류가 발생했습니다.')
    loading.value = false
  }
}

// 이전 단계로 이동
const prevStep = () => {
  if (step.value > 1) {
    step.value--
    router.push(`/recommendation/${step.value}`)
  }
}

// 라트 변경 감지
watch(() => route.path, (newPath) => {
  console.log('=== 라우트 변경 감지 ===')
  console.log('새 경로:', newPath)
  console.log('라우트 파라미터:', route.params)
  
  if (newPath === '/recommendation/result') {
    console.log('결과 페이지로 설정')
    step.value = 'result'
  } else if (route.params.step) {
    const newStep = parseInt(route.params.step as string)
    console.log('새로운 step으로 설정:', newStep)
    step.value = newStep
  }
  console.log('최종 step 값:', step.value)
}, { immediate: true })

// 추천 결과 가져오기
const getRecommendations = async () => {
  try {
    loading.value = true
    await new Promise(resolve => setTimeout(resolve, 1500)) // 의도적 지연
    
    const response = await axios.get('/api/recommendations/', {
      headers: { Authorization: `Token ${auth.token}` }
    })
    
    if (response.data.status === 'success') {
      recommendations.value = response.data.data
      router.push('/recommendation/result')
    } else {
      throw new Error(response.data.message || '추천 결과를 불러오는데 실패했습니다.')
    }
  } catch (error) {
    console.error('추천 결과 로드 중 오류:', error)
    alert('추천 결과를 불러오는데 실패했습니다.')
  } finally {
    loading.value = false
  }

}

// 추천 다시 시작
const restartRecommendation = () => {
  preference.value = {
    investment_purpose: '',
    investment_period: null,
    investment_amount: null
  }
  step.value = 1
  recommendationFinished.value = false
  selectedOption.value = null
  router.push('/recommendation/1')
}

const loadQuestions = async () => {
  try {
    const response = await axios.post('/api/recommendations/questions/next/', {
      preference_id: preferenceId.value
    }, {
      headers: { 
        'Authorization': `Token ${auth.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.data.status === 'success') {
      dynamicQuestions.value = response.data.data
      currentQuestionIndex.value = 0
      selectedOption.value = null
    }
  } catch (error) {
    console.error('질문 로드 중 오류:', error)
    alert('질문을 불러오는데 실패했습니다.')
  }
}

const saveAnswer = async () => {
  if (!selectedOption.value || !currentQuestion.value || !preferenceId.value) return;

  try {
    const response = await axios.post(
      '/api/recommendations/questions/answers/', 
      {
        question_id: currentQuestion.value.id,
        preference_id: preferenceId.value,
        answer: {
          selected_option: selectedOption.value.value
        }
      },
      {
        headers: { 
          Authorization: `Token ${auth.token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.data.status === 'success') {
      if (response.data.is_completed) {
        recommendationFinished.value = true;
        await getRecommendations();
      }
    }
  } catch (error) {
    console.error('답변 저장 실패:', error);
    alert('답변 저장에 실패했습니다.');
    throw error;
  }
};

const flippedCards = ref({});
const chartRefs = ref({});
const charts = ref({});

const flipCard = async (productId) => {
  flippedCards.value[productId] = !flippedCards.value[productId];
  
  if (flippedCards.value[productId]) {
    await nextTick();
    createChart(productId);
  } else {
    if (charts.value[productId]) {
      charts.value[productId].destroy();
      charts.value[productId] = null;
    }
  }
};

const createChart = (productId) => {
  const product = recommendations.value.find(p => p.fin_prdt_cd === productId);
  if (!product || !product.scores) return;

  const ctx = chartRefs.value[productId];
  if (!ctx) return;

  if (charts.value[productId]) {
    charts.value[productId].destroy();
  }

  charts.value[productId] = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['안정성', '수익성', '접근성', '유연성'],
      datasets: [{
        data: [
          product.scores.stability * 100,
          product.scores.profitability * 100,
          product.scores.accessibility * 100,
          product.scores.flexibility * 100
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2
      }]
    },
    options: {
      scales: {
        r: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
};

const saveToWishlist = async (product) => {
  try {
    console.log('[찜하기] 요청:', product);
    await api.post('/api/recommendations/wishlist/', {
      fin_prdt_cd: product.fin_prdt_cd,
      product_type: product.product_type
    });
    alert('찜 목록에 추가되었습니다.');
  } catch (error) {
    console.error('[찜하기] 실패:', error);
    if (error.response?.status === 400) {
      alert(error.response.data.message || '이미 찜한 상품입니다.');
    } else {
      alert('찜하기에 실패했습니다.');
    }
  }
};

const wishedProducts = ref([]);

// 찜한 상품 목록 가져오기
const fetchWishlist = async () => {
  try {
    const response = await fetch('/api/recommendations/wishlist/', {
      headers: {
        'Authorization': `Token ${auth.token}`
      }
    });
    const data = await response.json();
    wishedProducts.value = data.map(item => item.fin_prdt_cd);
  } catch (error) {
    console.error('찜 목록 조회 실패:', error);
  }
};

// 찜하기 상태 확인 함수
const isWished = computed(() => {
  return (productId) => wishedProducts.value.includes(productId);
});

// 찜하기 토글 함수
const toggleWish = async (product) => {
  try {
    if (isWished.value(product.fin_prdt_cd)) {
      await api.delete(`/api/recommendations/wishlist/`, {
        params: {
          fin_prdt_cd: product.fin_prdt_cd,
          product_type: product.product_type
        }
      });
      wishedProducts.value = wishedProducts.value.filter(id => id !== product.fin_prdt_cd);
    } else {
      await api.post('/api/recommendations/wishlist/', {
        fin_prdt_cd: product.fin_prdt_cd,
        product_type: product.product_type
      });
      wishedProducts.value.push(product.fin_prdt_cd);
    }
  } catch (error) {
    console.error('찜하기 처리 실패:', error);
  }
};

onMounted(() => {
  fetchWishlist();
  recommendations.value.slice(0, 2).forEach(product => {
    nextTick(() => {
      createChart(product.fin_prdt_cd);
    });
  });
});

// 이미지 에러 처리 함수 추가
const handleImageError = (e) => {
  e.target.src = '/bank.jpg'
}
</script>

<style lang="scss" scoped>
.recommendation-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
  padding-top: calc(30px + 1rem);
  min-height: 100vh;
  background-color: #f1f1f1;
  color: #333333;

  // 상단 진행 바
  .progress-container {
    width: 100%;
    max-width: 800px;
    margin: 0 auto 3rem;
    padding: 1rem;
    
    .progress-steps {
      display: flex;
      justify-content: space-between;
      margin-bottom: 1rem;
      
      .step {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #fff;
        position: relative;
        
        &.active {
          background: #34495e;
          box-shadow: 0 2px 8px rgba(88, 204, 2, 0.3);
        }
        
        &:not(:last-child)::after {
          content: '';
          position: absolute;
          width: calc(100% + 2rem);
          height: 4px;
          background: #e0e0e0;
          left: 100%;
          top: 50%;
          transform: translateY(-50%);
        }
      }
    }
  }

  // 질문 섹션
  .recommendation-step {
    max-width: 1200px;
    height: 600px;
    max-height: 1600px;
    margin: 0 auto;
    margin-top: 80px;
    background: #ffffff;
    padding: 3rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    animation: fadeIn 0.3s ease;

    display: flex;                /* 플렉스 컨테이너로 설정 */
    justify-content: center;      /* 수평 중앙 정렬 */
    align-items: center;          /* 수직 중앙 정렬 */
    flex-direction: column; 
    h2 {
      font-size: 2.4rem;
      color: #333333;
      margin-bottom: 4rem;
      text-align: center;
      font-weight: 600;
    }

    .options-grid {
      display: flex;
      justify-content: center;
      gap: 1.5rem;
      margin: 2rem auto 4rem auto;
      max-width: 1100px;
      border-radius: 8px;

      .option-card {
        flex: 1;
        min-width: 180px;
        max-width: 200px;
        background: #ffffff;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        &:hover {
          transform: translateY(-4px) scale(1.02);
          border-color: #34495e;
          box-shadow: 0 6px 15px rgba(77, 147, 117, 0.2);
        }

        &.selected {
          background: #2c3e50;
          color: white;
          animation: pulse 0.3s ease;

          .label {
            color: #ffffff;
          }
        }

        .icon {
          font-size: 2rem;
          margin-bottom: 0.8rem;
          color: #2c3e50;
        }

        .label {
          font-size: 1.1rem;
          font-weight: 600;
          color: #333333;
        }
      }
    }

    // 투자금액 입력 폼
    .amount-input {
      max-width: 500px;
      margin: 3rem auto;
      position: relative;
      
      input {
        width: 100%;
        padding: 1.2rem;
        font-size: 1.2rem;
        background: #ffffff;
        border: 2px solid #e5e5e5;
        border-radius: 12px;
        color: #333333;
        text-align: center;
        transition: all 0.3s ease;
        
        &:focus {
          outline: none;
          border-color: #34495e;
          box-shadow: 0 0 0 3px rgba(77, 147, 117, 0.1);
        }

        &::placeholder {
          color: #999999;
        }
      }
      
      span {
        position: absolute;
        right: 1.5rem;
        top: 50%;
        transform: translateY(-50%);
        color: #666666;
        font-weight: 500;
      }
    }
  }

  // 하단 네���게이션 버튼
  .navigation-buttons {
    position: fixed;
    bottom: 2rem;
    left: 0;
    right: 0;
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    padding: 1rem;
    z-index: 10;

    .nav-button {
      padding: 1rem 3.5rem;
      border-radius: 12px;
      font-size: 1.2rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border: none;

      &.primary {
        background: #2c3e50;
        color: white;
        box-shadow: 0 4px 12px rgba(77, 147, 117, 0.3);

        &:hover:not(:disabled) {
          background: #34495e;
          transform: translateY(-2px);
          box-shadow: 0 6px 15px rgba(77, 147, 117, 0.4);
        }

        &:disabled {
          background: #e5e5e5;
          cursor: not-allowed;
        }
      }

      &:not(.primary) {
        background: #f5f5f5;
        color: #333333;
        border: 2px solid #e5e5e5;

        &:hover {
          background: #eeeeee;
          transform: translateY(-2px);
        }
      }
    }
  }
}

.recommendation-results {
  padding: 2rem;

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;

    h2 {
      font-size: 2.2rem; // 헤더 글자 크기 조금 더 키움
      color: #2c3e50;
    }

    .restart-button {
      padding: 0.8rem 1.5rem;
      background: #2c3e50;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: #34495e;
        transform: translateY(-2px);
      }
    }
  }

  .product-card {
    position: relative;
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    
    &.best {
      background: white;
      border-radius: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      padding: 1.5rem;
      position: relative;
      margin-bottom: 2rem;

      .bank-logo {
        width: 40px;
        height: 40px;
        object-fit: contain;
      }

      .stats-container {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        
        .stat-item {
          text-align: center;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          
          &.rate {
            background: #e3f2fd;
            .value { color: #1976d2; }
          }
          
          &.score {
            background: #f3e5f5;
            .value { color: #7b1fa2; }
          }
        }
      }
    }
  }
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.restart-button {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;

  &:hover {
    background-color: #0056b3;
  }
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #eef2f7;
  border-radius: 3px;
  margin-bottom: 2rem;

  .progress {
    height: 100%;
    background: #2c3e50;
    border-radius: 3px;
    transition: width 0.3s ease;
  }
}

.question-progress {
  margin-top: 2rem;
  text-align: center;
  
  .dots {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 1rem;

    span {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #eef2f7;
      transition: background-color 0.3s;

      &.active {
        background: #2c3e50;
      }
    }
  }
}

// 애니메이션 추가
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(5px);

  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    
    .loading-logo {
      width: 200px;
      height: auto;
      animation: pulse 2s infinite ease-in-out;
    }

    h3 {
      color: #2c3e50;
      font-size: 1.5rem;
      font-weight: 600;
      margin: 0;
    }

    .loading-bar {
      width: 300px;
      height: 4px;
      background: #e0e0e0;
      border-radius: 2px;
      overflow: hidden;
      position: relative;

      .loading-progress {
        position: absolute;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, #34495e, transparent);
        animation: loading 1.5s infinite linear;
      }
    }
  }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes loading {
  0% { left: -100%; }
  100% { left: 100%; }
}

.results-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.top-products {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  
  .product-card.best {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 1.5rem;
    position: relative;
    margin-bottom: 2rem;

    .bank-logo {
      width: 40px;
      height: 40px;
      object-fit: contain;
    }

    .stats-container {
      display: flex;
      gap: 1rem;
      margin-top: 1rem;
      
      .stat-item {
        text-align: center;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        
        &.rate {
          background: #e3f2fd;
          .value { color: #1976d2; }
        }
        
        &.score {
          background: #f3e5f5;
          .value { color: #7b1fa2; }
        }
      }
    }
  }
}

.other-products-list {
  margin-top: 2rem;
  
  .product-list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    border-bottom: 1px solid #eee;
    
    .bank-logo-small {
      width: 24px;
      height: 24px;
      margin-right: 1rem;
    }
    
    .rate-info {
      display: flex;
      gap: 1rem;
      font-size: 0.9rem;
      color: #666;
    }
  }
}

.flip-card {
  perspective: 1000px;
  height: 300px;
  
  &.is-flipped .flip-card-inner {
    transform: rotateY(180deg);
  }
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 16px;
}

.flip-card-back {
  transform: rotateY(180deg);
  background: white;
  padding: 1rem;
}

.best-badge {
  position: absolute;
  top: -12px;
  right: 20px;
  background: #34495e;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  animation: badge-pulse 2s infinite;
}

.bank-info {
  display: flex;
  align-items: center;
  gap: 1rem;

  .bank-logo-container, .bank-logo-placeholder {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background-color: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .bank-logo {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 8px;
  }

  .bank-name {
    font-size: 1rem;
    color: #2c3e50;
    font-weight: 500;
  }
}

.wish-btn {
  position: absolute;
  right: 1rem;
  bottom: 1rem;
  background: none;
  border: none;
  color: #ff4757;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.2);
  }
}

@keyframes badge-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.other-products-container {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  margin-top: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.product-card.best {
  .card-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  .chart-container {
    width: 100%;
    height: 200px;
    margin: 1rem 0;
  }
}

.wish-button, .wish-button-small {
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  border: none;
  background: #34495e;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #2c3e50;
    transform: translateY(-2px);
  }
  
  &.wished {
    background: #e74c3c;
    
    &:hover {
      background: #c0392b;
    }
  }
}

.wish-button-small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.best-products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-bottom: 2rem;
}

.best-product-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .best-badge {
    position: absolute;
    top: -12px;
    right: 20px;
    background: linear-gradient(135deg, #2c3e50, #3498db);
    padding: 0.6rem 1.2rem;
    border-radius: 20px;
    color: white;
    font-weight: bold;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    overflow: hidden;

    .badge-shine {
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,0.3),
        transparent
      );
      animation: shine 2s infinite;
    }
  }

  .highlight-stats {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 1rem 0;

    .stat-box {
      text-align: center;
      padding: 1.5rem;
      border-radius: 12px;
      flex: 1;

      &.rate {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        .stat-value { color: #1976d2; }
      }
      
      &.score {
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        .stat-value { color: #7b1fa2; }
      }

      .stat-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
      }

      .stat-label {
        font-size: 0.9rem;
        color: #666;
      }
    }
  }
}

.other-products-container {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);

  .product-list-item {
    display: grid;
    grid-template-columns: 2fr 1.5fr auto;
    align-items: center;
    padding: 1.2rem;
    border-bottom: 1px solid #eee;
    gap: 1rem;

    &:last-child {
      border-bottom: none;
    }

    .product-main-info {
      display: flex;
      align-items: center;
      gap: 1rem;

      .bank-logo-container, .bank-logo-placeholder {
        width: 24px;
        height: 24px;
        border-radius: 4px;
      }
    }

    .product-stats {
      display: flex;
      align-items: center;
      gap: 1rem;
      color: #666;

      .stat-divider {
        color: #ddd;
      }
    }
  }
}

@keyframes shine {
  0% { left: -100%; }
  20% { left: 100%; }
  100% { left: 100%; }
}

.bank-logo-container {
  width: 40px;
  height: 40px;
  min-width: 40px;
  border-radius: 8px;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bank-logo-small {
  width: 24px;
  height: 24px;
  min-width: 24px;
  object-fit: contain;
}

.product-main-info .bank-logo-container {
  width: 24px;
  height: 24px;
  min-width: 24px;
}
</style>
