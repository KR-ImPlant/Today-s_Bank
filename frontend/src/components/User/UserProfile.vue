<template>
  <div class="profile-container">
    <div class="profile-section">
      <h2>회원 정보</h2>
      <div class="profile-info">
        <div class="info-row">
          <span class="label">사용자명</span>
          <span class="value">{{ username }}</span>
        </div>
        <div class="info-row">
          <span class="label">닉네임</span>
          <span class="value">{{ nickname }}</span>
        </div>
        <div class="info-row">
          <span class="label">이메일</span>
          <span class="value">{{ email }}</span>
        </div>
        <button @click="showEditModal" class="edit-button">정보 수정</button>
      </div>
    </div>

    <div class="financial-products-section">
      <div class="section-header">
        <div class="tabs">
          <button 
            :class="['tab-button', { active: activeTab === 'subscribed' }]"
            @click="activeTab = 'subscribed'"
          >
            가입한 상품
          </button>
          <button 
            :class="['tab-button', { active: activeTab === 'wishlist' }]"
            @click="activeTab = 'wishlist'"
          >
            찜한 상품
          </button>
        </div>
      </div>
      
      <!-- 가입 상품 섹션 -->
      <div v-if="activeTab === 'subscribed'" class="products-section">
        <div class="products-list">
          <h3>가입 상품 목록</h3>
          <div class="products-container">
            <div class="products-list-view">
              <div v-for="product in displayedProducts" 
                   :key="product.id" 
                   class="product-list-item">
                <div class="product-info">
                  <div class="bank-logo-name">
                    <img 
                      :src="productStore.bankLogos[getBankName(product)]" 
                      :alt="getBankName(product)"
                      class="bank-logo"
                    >
                    <span class="bank-name">{{ getBankName(product) }}</span>
                  </div>
                  <button class="product-name" @click="showProductDetail(product)">
                    {{ getProductName(product) }}
                  </button>
                  <div class="product-rate">
                    <span class="rate-label">최고금리</span>
                    <span class="rate-value">
                      {{ product.selected_option?.intr_rate2 || product.intr_rate2 || '0' }}%
                    </span>
                  </div>
                </div>
                <button class="unsubscribe-button" @click.stop="handleUnsubscribe(product)">
                  <i class="fas fa-minus"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-section">
          <h3>금리 비교</h3>
          <div class="chart-container">
            <canvas ref="subscribedRateChart"></canvas>
          </div>
        </div>
      </div>

      <!-- 찜한 상품 섹션 -->
      <div v-else class="products-section">
        <div class="products-list">
          <h3>찜한 상품 목록</h3>
          <div class="products-container">
            <div class="products-list-view">
              <div v-for="product in wishlistProducts" 
                   :key="product.fin_prdt_cd" 
                   class="product-list-item">
                <div class="product-info">
                  <div class="bank-logo-name">
                    <img 
                      :src="productStore.bankLogos[product.kor_co_nm]" 
                      :alt="product.kor_co_nm"
                      class="bank-logo"
                    >
                    <span class="bank-name">{{ product.kor_co_nm }}</span>
                  </div>
                  <button class="product-name" @click="showProductDetail(product)">
                    {{ product.fin_prdt_nm }}
                  </button>
                  <div class="product-rate">
                    <span class="rate-label">최고금리</span>
                    <span class="rate-value">{{ product.intr_rate2 }}%</span>
                  </div>
                </div>
                <button class="unsubscribe-button" @click.stop="removeFromWishlist(product)">
                  <i class="fas fa-minus"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-section">
          <h3>금리 비교</h3>
          <div class="chart-container">
            <canvas ref="rateChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 모달 수정 -->
    <div v-if="isModalOpen" class="edit-modal" @click.self="closeModal">
      <div class="edit-modal-content">
        <div class="edit-modal-header">
          <h2>회원정보 수정</h2>
          <button class="edit-close-button" @click="closeModal">&times;</button>
        </div>
        
        <div class="edit-profile-form">
          <div class="edit-form-group">
            <label>아이디</label>
            <input type="text" v-model="username" disabled class="edit-disabled-input" />
          </div>
          
          <div class="edit-form-group">
            <label>닉네임</label>
            <input type="text" v-model="nickname" required />
          </div>
          
          <div class="edit-form-group">
            <label>이메일</label>
            <input type="email" v-model="email" required />
          </div>
          
          <div class="edit-form-group">
            <label>현재 비밀번호</label>
            <input type="password" v-model="currentPassword" />
          </div>
          
          <div class="edit-form-group">
            <label>새 비밀번호</label>
            <input type="password" v-model="newPassword" />
          </div>
          
          <div class="edit-form-group">
            <label>새 비밀번호 확인</label>
            <input type="password" v-model="passwordConfirm" />
          </div>
          
          <div class="edit-button-group">
            <button class="edit-save-button" @click="saveChanges">저장</button>
            <button class="edit-cancel-button" @click="closeModal">취소</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 저축기간 선택 모달 -->
    <div v-if="showPeriodModal" class="modal" @click="closeModalOnOverlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>저축기간 선택</h3>
          <button class="close-button" @click="showPeriodModal = false">&times;</button>
        </div>
        <div class="period-options">
          <button 
            v-for="option in selectedProduct?.detail_options" 
            :key="option.save_trm"
            @click="selectPeriod(option.id)"
          >
            {{ option.save_trm }}개월
          </button>
        </div>
      </div>
    </div>

    <!-- 상품 상세 모 -->
    <ProductDetailModal
      v-if="selectedProduct"
      :isOpen="!!selectedProduct"
      :product="selectedProduct"
      :detailOptions="productOptions || []"
      :product_type="selectedProductType"
      @close="closeModal"
      @subscription-change="handleSubscriptionChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'

import { useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import ProductDetailModal from '../Products/ProductDetailModal.vue'
import { useAuthStore } from '@/stores/authStore'
import api from '@/utils/axios'
import { useProductStore } from '@/stores/productStore'
import type { Product } from '@/types/product'
import { Navigation } from 'swiper/modules';
import { Swiper, SwiperSlide } from 'swiper/vue';
import 'swiper/css';
import 'swiper/css/navigation';

Chart.register(...registerables)

const router = useRouter()
const authStore = useAuthStore()
const isEditing = ref(false)
const email = ref('')
const currentPassword = ref('')
const newPassword = ref('')
const passwordConfirm = ref('')
const username = ref('')
const nickname = ref('')
const isModalOpen = ref(false)

// 인증 상태 감시
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (!isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/')
  }
})

// 컴포넌트 마운트 시 인증 체크
onMounted(() => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/')
  }
})

const startEditing = () => {
  isEditing.value = true
}

const cancelEditing = () => {
  isEditing.value = false
  resetForm()
}

const resetForm = () => {
  email.value = ''
  currentPassword.value = ''
  newPassword.value = ''
  passwordConfirm.value = ''
  nickname.value = ''
  fetchProfile()
}

const saveChanges = async () => {
  try {
    if (newPassword.value && newPassword.value !== passwordConfirm.value) {
      alert('새 비밀번호가 일치하지 않습니다.')
      return
    }

    const updateData: any = {
      email: email.value,
      nickname: nickname.value
    }

    if (currentPassword.value && newPassword.value) {
      updateData.current_password = currentPassword.value
      updateData.new_password = newPassword.value
    }

    const response = await updateProfile(updateData)
    if (response?.data) {
      authStore.updateNickname(response.data.nickname)
      // user 정보도 업데이트
      authStore.user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      closeModal()
      alert('프로필이 성공적으로 업데이트되었습니다.')
    }
  } catch (error: any) {
    console.error('프로필 업데이트 실패:', error)
    if (error.response?.data) {
      alert(Object.values(error.response.data).flat().join('\n'))
    } else {
      alert('프로필 업데이트에 실패했습니다.')
    }
  }
}

const updateProfile = async (data: any) => {
  try {
    const response = await api.put('/api/accounts/profile/', data)
    if (response.data) {
      await fetchProfile()
      return response
    }
  } catch (error) {
    console.error('프로필 업데이트 실패:', error)
    throw error
  }
}

const fetchProfile = async () => {
  try {
    const response = await api.get('/api/accounts/profile/')
    email.value = response.data.email
    username.value = response.data.username
    nickname.value = response.data.nickname
  } catch (error) {
    console.error('프로필 정보 조회 실패:', error)
  }
}

onMounted(() => {
  fetchProfile()
})

// 모달 관련 함수 추가
const showEditModal = () => {
  isModalOpen.value = true
}
const closeModal = () => {
  selectedProduct.value = null
  productOptions.value = []
  isModalOpen.value = false
  resetForm()
}


// 상태 관리
const subscribedProducts = ref<any[]>([])
console.log('구독된 상품 데이터:', subscribedProducts.value)
const displayedProducts = computed(() => {
  return Array.from(subscribedProducts.value).slice(0, 5) || []
})
const showProductListModal = ref(false)
const activeTab = ref('deposit')
const selectedProduct = ref<Product | null>(null)
const productOptions = ref<Array<any>>([])
const selectedProductType = ref<'deposit' | 'saving'>('deposit')
const rateChart = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null
const productStore = useProductStore()

const productListProducts = computed(() => {
  return activeTab.value === 'deposit' 
    ? productStore.displayedDepositProducts 
    : productStore.displayedSavingProducts
})

const selectProduct = (product: any) => {
  showProductListModal.value = false
  showProductDetail(product)
}

onMounted(async () => {
  await productStore.initializeProductsData()
  // 구독 상태 초기화
  const response = await api.get('/api/products/user-products/subscriptions/')
  subscribedProducts.value = response.data.map((p: any) => p.fin_prdt_cd)
})

// 차트 관련
const initChart = (products: any[]) => {
  if (!rateChart.value || !products?.length) {
    console.log('차트 초기화 실패: 캔버스 또는 데이터 없음');
    return;
  }
  
  if (chart) {
    chart.destroy();
  }

  const ctx = rateChart.value.getContext('2d');
  if (!ctx) return;

  // 찜한 상품의 금리 이터 가공
  const chartData = products.slice(0, 5).map(p => {
    // 다양한 가능한 필드명 체크
    const baseRate = parseFloat(p.intr_rate || p.basic_rate || p.base_rate || 0);
    const maxRate = parseFloat(p.intr_rate2 || 0);
    
    console.log('차트 데이터 처리:', {
      bankName: p.kor_co_nm,
      baseRate: baseRate,
      maxRate: maxRate,
      originalData: p
    });
    
    return {
      bankName: p.kor_co_nm,
      baseRate: baseRate,
      maxRate: maxRate
    };
  });

  console.log('최종 차트 데이터:', chartData);

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.map(d => d.bankName),
      datasets: [
        {
          label: '기본금리',
          data: chartData.map(d => d.baseRate),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        },
        {
          label: '최고금리',
          data: chartData.map(d => d.maxRate),
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '금리 (%)'
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  });
}

// 데이터 가져기
const fetchSubscribedProducts = async () => {
  try {
    console.log('[fetchSubscribedProducts] 시작')
    
    const response = await api.get('/api/products/user-subscribed-products/')
    console.log('[fetchSubscribedProducts] 응답:', {
      status: response.status,
      headers: response.headers,
      data: response.data
    })
    
    if (response.data.results && Array.isArray(response.data.results)) {
      subscribedProducts.value = response.data.results
      console.log('[fetchSubscribedProducts] 상품 목:', subscribedProducts.value)
      
      // 각 상품의 세부 정보 로깅
      subscribedProducts.value.forEach((product, index) => {
        console.log(`[fetchSubscribedProducts] 상품 ${index + 1}:`, {
          id: product.id,
          productType: product.product_type,
          depositProduct: product.deposit_product,
          savingProduct: product.saving_product,
          optionId: product.option_id,
          bankName: getBankName(product),
          productName: getProductName(product)
        })
      })
      
      nextTick(() => {
        console.log('[차트 초기화] 시작')
        if (subscribedProducts.value.length > 0) {
          initChart(subscribedProducts.value)
        } else {
          console.log('[차트 기화] 건너뜀 - 데이터 없음')
        }
      })
    } else {
      console.warn('[fetchSubscribedProducts] 잘못된 응답 형식:', response.data)
    }
  } catch (error) {
    console.error('[fetchSubscribedProducts] 오류:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers
      }
    })
  }
}

onMounted(() => {
  fetchSubscribedProducts()
})

// 헬퍼 함수들
const getBankName = (product: any) => {
  const bankName = product.deposit_product?.kor_co_nm || 
                  product.saving_product?.kor_co_nm || 
                  product.product?.kor_co_nm || 
                  '은행명 없음'
  console.log('[getBankName]', { product, bankName })
  return bankName
}

const getProductName = (product: any) => {
  const productName = product.deposit_product?.fin_prdt_nm || 
                     product.saving_product?.fin_prdt_nm || 
                     product.product?.fin_prdt_nm || 
                     '상품명 없'
  console.log('[getProductName]', { product, productName })
  return productName
}

const showProductDetail = async (product: any) => {
  try {
    // 가입한 상품인 경우
    if (product.deposit_product || product.saving_product) {
      const baseProduct = product.deposit_product || product.saving_product;
      const productType = product.deposit_product ? 'deposit' : 'saving';
      
      // API 호출
      const response = await api.get(`/api/products/${productType}s/${baseProduct.fin_prdt_cd}/`);
      
      selectedProduct.value = response.data.product;
      productOptions.value = response.data.options || [];
      selectedProductType.value = productType;
    } 
    // 찜한 상품인 경우
    else {
      const productType = product.product_type || 'deposit';
      
      // API 호출
      const response = await api.get(`/api/products/${productType}s/${product.fin_prdt_cd}/`);
      
      selectedProduct.value = response.data.product;
      productOptions.value = response.data.options || [];
      selectedProductType.value = productType;
    }
  } catch (error: any) {
    console.error('상품 상세 정보 조회 실패:', error);
    if (error.response?.status === 404) {
      alert('상품을 찾을 수 없습니다.');
    } else {
      alert('상품 정보를 불러오는데 실패했습니다.');
    }
  }
};

// const closeModal = () => {
//   selectedProduct.value = null;
//   productOptions.value = [];
// };

// const handleSubscriptionChange = (productId: string, isSubscribed: boolean) => {
//   // 구독 상태 변경 시 필요한 처리
//   if (!isSubscribed) {
//     // 구독 취소된 경우 목록에서 제거하는 로직
//   }
// };

// 페이지네이 관련 상태
const currentPage = ref(1)
const itemsPerPage = 10
const selectedProductPeriods = ref<string[]>([])
const showPeriodModal = ref(false)

// 페이지네이션된 상품 목록
const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return productListProducts.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(productListProducts.value.length / itemsPerPage)
})

// 저축기간 선택 관련 함수
const showPeriodSelect = async (product: any) => {
  selectedProduct.value = product
  const detail = await productStore.fetchProductDetail(product.fin_prdt_cd, activeTab.value)
  if (detail && detail.detail_options) {
    selectedProduct.value = {
      ...product,
      detail_options: detail.detail_options
    }
    showPeriodModal.value = true
  }
}

const selectPeriod = (period: number) => {
  if (selectedProduct.value) {
    selectedProduct.value.selected_option_id = period
    showPeriodModal.value = false
  }
}

// 차트 관련 함수 수정
const getBaseRate = (product: any) => {
  try {
    if (product.selected_option && product.selected_option.intr_rate) {
      return parseFloat(product.selected_option.intr_rate);
    }
    console.log('기본금리 정보 없음:', product);
    return 0;
  } catch (error) {
    console.error('기본금리 계산 오류:', error);
    return 0;
  }
};

const getMaxRate = (product: any) => {
  try {
    if (product.selected_option && product.selected_option.intr_rate2) {
      return parseFloat(product.selected_option.intr_rate2);
    }
    console.log('최고금리 정보 없음:', product);
    return 0;
  } catch (error) {
    console.error('최고금리 계산 오류:', error);
    return 0;
  }
};

// 차트 데이터 계산 함수
const calculateChartData = computed(() => {
  if (!userStore.subscribedProducts) return [];
  
  return userStore.subscribedProducts.map(product => ({
    bankName: product.deposit_product?.kor_co_nm || product.saving_product?.kor_co_nm,
    baseRate: getBaseRate(product),
    maxRate: getMaxRate(product)
  }));
});

// 구독 상태 확인 함수
const isSubscribed = (product: any) => {
  return subscribedProducts.value.includes(product.fin_prdt_cd)
}

// 구독  함수
const handleSubscription = async (product: any) => {
  try {
    if (!product.selected_option_id) {
      alert('저축기간을 선택해주세요.')
      return
    }

    const response = await api.post('/api/products/user-products/', {
      fin_prdt_cd: product.fin_prdt_cd,
      option_id: product.selected_option_id,
      product_type: activeTab.value
    })

    if (response.status === 201 || response.status === 200) {
      // fetchSubscribedProducts 함수 호출로 수정
      await fetchSubscribedProducts()
      await loadProducts()
      
      alert(response.data.message)
    }
  } catch (error: any) {
    console.error('품 가입 실패:', error)
    if (error.response?.data?.error) {
      alert(error.response.data.error)
    } else {
      alert('상품 가입 중 오류가 발생했습니다.')
    }
  }
}

// 모달 닫기 함수들
const handleModalClose = () => {
  showProductListModal.value = false
  currentPage.value = 1
}

// const closeModalOnOverlay = (event: MouseEvent) => {
//   if ((event.target as HTMLElement).classList.contains('modal')) {
//     handleModalClose()
//   }
// }

// 구 상태 변경 처리
const handleSubscriptionChange = (productCode: string, isSubscribed: boolean) => {
  if (isSubscribed) {
    subscribedProducts.value.push(productCode)
  } else {
    subscribedProducts.value = subscribedProducts.value.filter(code => code !== productCode)
  }
}

// 저축기간 옵션 로드
const loadProductOptions = async (product: any) => {
  try {
    const response = await productStore.fetchProductDetail(product.fin_prdt_cd, activeTab.value)
    if (response && response.options) {
      product.detail_options = response.options
    }
  } catch (error) {
    console.error('저축기간 옵션 로드 실패:', error)
  }
}

// 저축기간 변경 처리
const handlePeriodChange = (product: any) => {
  if (product.selected_option_id) {
    const selectedOption = product.detail_options.find(
      (option: any) => option.id === product.selected_option_id
    )
    if (selectedOption) {
      product.save_trm = `${selectedOption.save_trm}개월`
    }
  }
}

const loadProducts = async () => {
  try {
    const response = await productStore.fetchProducts(activeTab.value)
    if (response?.results) {
      const productsWithOptions = await Promise.all(
        response.results.map(async (product) => {
          const detail = await productStore.fetchProductDetail(
            product.fin_prdt_cd, 
            activeTab.value
          )
          return {
            ...product,
            detail_options: detail?.options || []
          }
        })
      )
      productListProducts.value = productsWithOptions
    }
  } catch (error) {
    console.error('상품 목록 로드 패:', error)
  }
}

const userProducts = ref<any[]>([]);

// 사용자 상품 목록을 가져오는 함수
const fetchUserProducts = async () => {
  try {
    const response = await api.get('/api/products/user-subscribed-products/');
    userProducts.value = response.data.results;
  } catch (error) {
    console.error('사용자 상품 조회 실패:', error);
  }
};

const handleUnsubscribe = async (product: any) => {
  try {
    await api.post('/api/products/user-products/', {
      fin_prdt_cd: product.deposit_product?.fin_prdt_cd || product.saving_product?.fin_prdt_cd,
      option_id: product.option_id,
      product_type: product.product_type,
      is_active: false
    });
    
    // 로컬 상태 즉시 업데이트
    subscribedProducts.value = subscribedProducts.value.filter(p => 
      (p.deposit_product?.fin_prdt_cd || p.saving_product?.fin_prdt_cd) !== 
      (product.deposit_product?.fin_prdt_cd || product.saving_product?.fin_prdt_cd)
    );
    
    // 차트 업데이트
    nextTick(() => {
      if (subscribedProducts.value.length > 0) {
        initSubscribedChart(subscribedProducts.value);
      }
    });
    
  } catch (error) {
    console.error('상품 해지 패:', error);
  }
};

// 컴포넌트 마운트 시 상품 목록 가져오기
onMounted(() => {
  fetchUserProducts();
});

const wishlistProducts = ref([]);

const fetchWishlistProducts = async () => {
  try {
    console.log('[찜목록] 조회 시작');
    const response = await api.get('/api/recommendations/wishlist/');
    console.log('[찜목록] 원본 응답 데이터:', response.data);
    
    if (Array.isArray(response.data)) {
      wishlistProducts.value = response.data.map(product => {
        // 기본금리와 최고금리 필드 확인을 한 로깅
        console.log('상품 데이터:', {
          productName: product.fin_prdt_nm,
          allFields: product,
          baseRate: product.intr_rate || product.basic_rate || product.base_rate,
          maxRate: product.intr_rate2
        });
        
        // 다양한 가능한 필드명 체크
        const baseRate = parseFloat(product.intr_rate || product.basic_rate || product.base_rate || 0);
        const maxRate = parseFloat(product.intr_rate2 || 0);
        
        return {
          ...product,
          intr_rate: baseRate.toFixed(2),
          intr_rate2: maxRate.toFixed(2)
        };
      });
      
      console.log('[찜목록] 처리된 데이터:', wishlistProducts.value);
      
      nextTick(() => {
        if (wishlistProducts.value.length > 0) {
          initChart(wishlistProducts.value);
        }
      });
    }
  } catch (error) {
    console.error('[찜목록] 조회 실패:', error);
  }
};

// 찜 해제 함수
const removeFromWishlist = async (product) => {
  try {
    await api.delete(`/api/recommendations/wishlist/`, {
      params: {
        fin_prdt_cd: product.fin_prdt_cd,
        product_type: product.product_type
      }
    });
    await fetchWishlistProducts();
  } catch (error) {
    console.error('찜 제 실패:', error);
  }
};

const handleSubscribe = async (product) => {
  try {
    await subscribeProduct(product);
    activeTab.value = 'subscribed';
    await fetchUserProducts();
  } catch (error) {
    console.error('상품 가입 실패:', error);
  }
};

// 탭 변경 시 찜목록 새로고침
watch(() => activeTab.value, async (newTab) => {
  if (newTab === 'wishlist') {
    await fetchWishlistProducts();
  }
});

onMounted(async () => {
  if (activeTab.value === 'wishlist') {
    await fetchWishlistProducts();
  }
});

// 찜목록 변경 감시
watch(() => wishlistProducts.value, (newProducts) => {
  if (newProducts?.length > 0 && activeTab.value === 'wishlist') {
    nextTick(() => {
      initChart(newProducts);
    });
  }
}, { deep: true });

// 탭 변경 감시
watch(() => activeTab.value, (newTab) => {
  if (newTab === 'wishlist' && wishlistProducts.value?.length > 0) {
    nextTick(() => {
      initChart(wishlistProducts.value);
    });
  }
});

// 기존 드에 추가
const subscribedRateChart = ref(null)
let subscribedChart = null

// 가입 상품 차트 초기화 함수
const initSubscribedChart = (products) => {
  if (!subscribedRateChart.value || !products?.length) return;
  
  if (subscribedChart) {
    subscribedChart.destroy();
  }

  const ctx = subscribedRateChart.value.getContext('2d');
  if (!ctx) return;

  const chartData = products.map(product => ({
    bankName: getBankName(product),
    baseRate: product.selected_option?.intr_rate || 0,
    maxRate: product.selected_option?.intr_rate2 || 0
  }));

  subscribedChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.map(d => d.bankName),
      datasets: [
        {
          label: '기본금리',
          data: chartData.map(d => d.baseRate),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        },
        {
          label: '최고금리',
          data: chartData.map(d => d.maxRate),
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '금리 (%)'
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  });
};

// 가입 상품 데이터 변경 감시
watch(() => displayedProducts.value, (newProducts) => {
  if (newProducts?.length > 0 && activeTab.value === 'subscribed') {
    nextTick(() => {
      initSubscribedChart(newProducts);
    });
  }
}, { deep: true });

// 탭 변경 감시 수정
watch(() => activeTab.value, (newTab) => {
  nextTick(() => {
    if (newTab === 'subscribed' && displayedProducts.value?.length > 0) {
      initSubscribedChart(displayedProducts.value);
    } else if (newTab === 'wishlist' && wishlistProducts.value?.length > 0) {
      initChart(wishlistProducts.value);
    }
  });
});
</script>

<style lang="scss" scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  h2 {
    font-size: 1.8rem;
    color: #333;
    margin-bottom: 1.5rem;
  }

  .edit-button {
    padding: 0.8rem 1.5rem;
    border-radius: 8px;
    border: none;
    background: #2c3e50;
    color: white;
    cursor: pointer;
    transition: background-color 0.3s ease;

    &:hover {
      background: #34495e;
    }
  }
}

.profile-info {
  .info-row {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;

    .label {
      width: 120px;
      font-weight: 600;
      color: #2c3e50;
    }

    .value {
      flex: 1;
      color: #333;
    }
  }
}

.financial-products-section {
  margin-top: 2rem;

  .section-header {
    margin-bottom: 0.5rem;
    
    .tabs {
      display: flex;
      gap: 1rem;
    }
  }

  .products-section {
    display: flex;
    gap: 2rem;

    .products-list, .chart-section {
      flex: 1;
      background: white;
      border-radius: 12px;
      padding: 2rem;
      height: 500px;
      overflow: hidden;
      
      h3 {
        margin-bottom: 1.5rem;
        color: #2c3e50;
        font-size: 1.1rem;
        font-weight: 600;
      }
    }

    .products-list {
      .products-container {
        height: calc(100% - 3rem);
        overflow-y: auto;
      }
    }

    .chart-section {
      flex: 1;
      background: white;
      border-radius: 12px;
      padding: 2rem;
      height: 500px;
      overflow: hidden;
      display: flex;
      flex-direction: column;

      h3 {
        margin-bottom: 1.5rem;
        color: #2c3e50;
      }

      .chart-container {
        flex: 1;
        position: relative;
        width: 95%;  // 컨테이너 너비를 95%로 제한
        margin: 0 auto;  // 중앙 정렬
        
        canvas {
          position: absolute;
          top: 0;
          left: 0;
          width: 100% !important;
          height: 100% !important;
        }
      }
    }
  }
}

.section-header {
  margin-bottom: 2rem;
  
  .tabs {
    display: flex;
    gap: 1rem;
    
    .tab-button {
      padding: 0.8rem 1.5rem;
      border: none;
      border-radius: 8px;
      background: #f8f9fa;
      color: #2c3e50;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &.active {
        background: #2c3e50;
        color: white;
      }
    }
  }
}

.products-container {
  .swiper {
    padding: 0 2rem;
    
    :deep(.swiper-button-prev),
    :deep(.swiper-button-next) {
      color: #2c3e50;
      &:after {
        font-size: 1.5rem;
      }
    }
  }
}

.chart-container {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  height: 300px;
}

.edit-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;

  .edit-modal-content,  {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;

    .edit-modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;

      h2 {
        margin: 0;
        color: #2c3e50;
      }

      .edit-close-button {
        background: none;
        border: none;
        font-size: 1.5rem;
        color: #666;
        cursor: pointer;
        padding: 0.5rem;
        
        &:hover {
          color: #333;
        }
      }
    }
  }
}

.edit-profile-form {
  .edit-form-group {
    margin-bottom: 1.5rem;

    label {
      display: block;
      margin-bottom: 0.5rem;
      color: #2c3e50;
      font-weight: 600;
    }

    input {
      width: 100%;
      padding: 0.8rem;
      border: 1px solid #ddd;
      border-radius: 8px;
      transition: border-color 0.3s ease;

      &:focus {
        outline: none;
        border-color: #2c3e50;
      }

      &.edit-disabled-input {
        background-color: #f8f9fa;
        cursor: not-allowed;
      }
    }
  }

  .edit-button {
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  border: none;
  background: #2c3e50;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background: #34495e;
  }
}
  .edit-button-group,   {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;

    button {
      flex: 1;
      padding: 0.8rem;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      transition: background-color 0.3s ease;

      &.edit-save-button {
        background: #2c3e50;
        color: white;

        &:hover {
          background: #34495e;
        }
      }

      &.edit-cancel-button {
        background: #f8f9fa;
        color: #2c3e50;

        &:hover {
          background: #e9ecef;
        }
      }
    }
  }
}

.products-list-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 500px;
  // overflow-y: auto;
  padding-right: 1rem;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
  }
}

.product-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;

  &:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .product-info {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 1.5rem;

    .bank-logo-name {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      min-width: 150px;

      .bank-logo {
        width: 24px;
        height: 24px;
        object-fit: contain;
      }

      .bank-name {
        font-size: 0.9rem;
        color: #666;
      }
    }

    .product-name {
      flex: 1;
      border: none;
      background: none;
      color: #2c3e50;
      font-size: 1rem;
      font-weight: 500;
      text-align: left;
      cursor: pointer;
      padding: 0;

      &:hover {
        color: #3498db;
      }
    }

    .product-rate {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      min-width: 100px;

      .rate-label {
        font-size: 0.8rem;
        color: #666;
      }

      .rate-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
      }
    }
  }

  .unsubscribe-button {
    background: none;
    border: none;
    color: #e74c3c;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-left: 1rem;

    &:hover {
      background: #fee;
    }
  }
}

.products-section {
  .products-list {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;

    h3 {
      margin-bottom: 1.5rem;
      color: #2c3e50;
    }

    .products-container {
      .products-list-view, .products-grid {
        display: flex;
        flex-direction: column;
        gap: 1rem;

        .product-list-item, .product-card {
          display: flex;
          align-items: center;
          padding: 1rem;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
          transition: all 0.2s ease;

          &:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          }

          .product-info, .bank-logo-name {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 1.5rem;

            .bank-logo-name, .bank-name {
              display: flex;
              align-items: center;
              gap: 0.5rem;
              min-width: 150px;
              font-size: 0.9rem;
              color: #666;
            }

            .bank-logo {
              width: 24px;
              height: 24px;
              object-fit: contain;
            }
          }

          .product-name {
            flex: 1;
            border: none;
            background: none;
            color: #2c3e50;
            font-size: 1rem;
            font-weight: 500;
            text-align: left;
            cursor: pointer;
            padding: 0;

            &:hover {
              color: #3498db;
            }
          }

          .product-rate {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            min-width: 100px;

            .rate-label {
              font-size: 0.8rem;
              color: #666;
            }

            .rate-value {
              font-size: 1.1rem;
              font-weight: 600;
              color: #2c3e50;
            }
          }

          .unsubscribe-button {
            background: none;
            border: none;
            color: #e74c3c;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-left: 1rem;

            &:hover {
              background: #fee;
            }
          }
        }
      }
    }
  }
}

// Swiper 관련 스타일 추가
.swiper {
  padding: 1rem;
  
  .swiper-slide {
    height: auto;
  }

  .swiper-button-next,
  .swiper-button-prev {
    color: #2c3e50;
    
    &:after {
      font-size: 1.5rem;
    }
  }
}
</style>