<template>
  <div class="home-page">
    <!-- 히어로 섹션 -->
    <swiper
      class="hero-swiper"
      :modules="swiperModules"
      :slides-per-view="1"
      :loop="true"
      :autoplay="{
        delay: 5000,
        disableOnInteraction: false
      }"
      @swiper="onSwiper"
      @slideChange="onSlideChange"
    >
      <!-- 1페이지: 기존 히어로 섹션 -->
      <swiper-slide>
        <section class="hero">
          <div class="hero-content">
            <h1>스마트한 금융생활의 시작</h1>
            <p>예적금 비교부터 환율계산까지 한번에</p>
            <div class="cta-buttons">
              <router-link to="/product" class="cta-button primary">
                <i class="fas fa-piggy-bank"></i>
                상품 둘러보기
              </router-link>
              <router-link to="/recommendation" class="cta-button secondary">
                <i class="fas fa-thumbs-up"></i>
                맞춤 상품 추천받기
              </router-link>
            </div>
          </div>
        </section>
      </swiper-slide>

      <!-- 2페이지: 최고금리 상품 섹션 -->
      <swiper-slide>
        <section class="hero hero-products">
          <div class="hero-content">
            <h1>오늘의 최고금리 상품</h1>
            <div class="top-products-grid">
              <div v-if="topProducts.deposit" class="product-section">
                <h2>예금</h2>
                <div class="product-info">
                  <ProductCard 
                    :product="{
                      ...topProducts.deposit.product,
                      intr_rate: topProducts.deposit.options[0]?.intr_rate || 0,
                      intr_rate2: topProducts.deposit.options[0]?.intr_rate2 || 0,
                      intr_rate_type_nm: topProducts.deposit.options[0]?.intr_rate_type_nm || '',
                      save_trm: topProducts.deposit.options[0]?.save_trm || 0,
                      product_type: 'deposit'
                    }"
                    :is-subscribed="subscriptionMap.get(topProducts.deposit.product.fin_prdt_cd)"
                    @click="openProductDetail"
                  />
                </div>
              </div>
              
              <div v-if="topProducts.saving" class="product-section">
                <h2>적금</h2>
                <div class="product-info">
                  <ProductCard 
                    :product="{
                      ...topProducts.saving.product,
                      intr_rate: topProducts.saving.options[0]?.intr_rate || 0,
                      intr_rate2: topProducts.saving.options[0]?.intr_rate2 || 0,
                      intr_rate_type_nm: topProducts.saving.options[0]?.intr_rate_type_nm || '',
                      save_trm: topProducts.saving.options[0]?.save_trm || 0
                    }"
                    :is-subscribed="subscriptionMap.get(topProducts.saving.product.fin_prdt_cd)"
                    @click="openProductDetail"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
      </swiper-slide>
    </swiper>

    <!-- 주요 기능 섹션 -->
    <section class="features">
      <div class="features-grid">
        <router-link to="/product" class="feature-card">
          <i class="fas fa-piggy-bank"></i>
          <h3>예적금 비교</h3>
          <p>최고의 금리 상품을 한눈에 비교하고 선택하세요</p>
          <div class="feature-link">자세히 보기</div>
        </router-link>
        <router-link to="/exchange" class="feature-card">
          <i class="fas fa-exchange-alt"></i>
          <h3>실시간 환율</h3>
          <p>실시간 환율 정보와 계산기를 제공합니다</p>
          <div class="feature-link">자세히 보기</div>
        </router-link>
        <router-link to="/map" class="feature-card">
          <i class="fas fa-map-marker-alt"></i>
          <h3>은행 찾기</h3>
          <p>내 주변 가까운 은행 위치를 확인하세요</p>
          <div class="feature-link">자세히 보기</div>
        </router-link>
        <router-link to="/community" class="feature-card">
          <i class="fas fa-comments"></i>
          <h3>커뮤니티</h3>
          <p>다른 사용자들과 정보를 공유하고 소통하세요</p>
          <div class="feature-link">자세히 보기</div>
        </router-link>
      </div>
    </section>

    <ProductDetailModal
      v-if="selectedProduct"
      :is-open="!!selectedProduct"
      :product="selectedProduct"
      :detail-options="productOptions"
      :product_type="selectedProduct?.product_type"
      @close="closeProductDetail"
      @subscription-change="handleSubscriptionChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useProductStore } from '@/stores/productStore';
import { formatBankName } from '@/utils/bankNameFormatter';
import ProductCard from '@/components/Products/ProductCard.vue';
import ProductDetailModal from '@/components/Products/ProductDetailModal.vue';
import api from '@/utils/axios';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Autoplay, Navigation } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/autoplay';

const productStore = useProductStore();
const topProducts = ref({
  deposit: null,
  saving: null
});
const subscriptionMap = ref(new Map<string, boolean>());
const selectedProduct = ref<Product | null>(null);
const productOptions = ref<Array<Option> | null>(null);

const fetchTopProducts = async () => {
  try {
    const depositResponse = await api.get('/api/products/deposits/top-rate/');
    const savingResponse = await api.get('/api/products/savings/top-rate/');

    if (depositResponse.data.product && depositResponse.data.options?.length > 0) {
      const option = depositResponse.data.options[0];
      depositResponse.data.product = {
        ...depositResponse.data.product,
        product_type: 'deposit',
        intr_rate: option.intr_rate,
        intr_rate2: option.intr_rate2,
        intr_rate_type_nm: option.intr_rate_type_nm,
        save_trm: option.save_trm
      };
    }

    if (savingResponse.data.product && savingResponse.data.options?.length > 0) {
      const option = savingResponse.data.options[0];
      savingResponse.data.product = {
        ...savingResponse.data.product,
        product_type: 'saving',
        intr_rate: option.intr_rate,
        intr_rate2: option.intr_rate2,
        intr_rate_type_nm: option.intr_rate_type_nm,
        save_trm: option.save_trm
      };
    }

    topProducts.value = {
      deposit: depositResponse.data,
      saving: savingResponse.data
    };

    console.log('Processed products:', {
      deposit: depositResponse.data.product,
      saving: savingResponse.data.product
    });
  } catch (error) {
    console.error('최고금리 상품 조회 실패:', error);
  }
};

const handleSubscriptionChange = async (productId: string, isSubscribed: boolean) => {
  subscriptionMap.value.set(productId, isSubscribed);
  await fetchAllSubscriptions();
};

const fetchAllSubscriptions = async () => {
  try {
    const depositResponse = await api.get('/api/products/user-products/all/', {
      params: { product_type: 'deposit' }
    });
    const savingResponse = await api.get('/api/products/user-products/all/', {
      params: { product_type: 'saving' }
    });
    
    const newMap = new Map();
    // 예금 상품 구독 상태
    Object.entries(depositResponse.data).forEach(([fin_prdt_cd, data]: [string, any]) => {
      newMap.set(fin_prdt_cd, data.is_subscribed);
    });
    // 적금 상품 구독 상태
    Object.entries(savingResponse.data).forEach(([fin_prdt_cd, data]: [string, any]) => {
      newMap.set(fin_prdt_cd, data.is_subscribed);
    });
    
    subscriptionMap.value = newMap;
  } catch (error) {
    console.error('구독 상태 조회 실패:', error);
  }
};

const openProductDetail = async (product: Product) => {
  try {
    const response = await api.get(`/api/products/${product.product_type}s/${product.fin_prdt_cd}/`);
    if (response.data) {
      selectedProduct.value = {
        ...response.data.product,
        product_type: product.product_type
      };
      productOptions.value = response.data.options;
    }
  } catch (error) {
    console.error('상품 상세 정보 조회 실패:', error);
  }
};

const closeProductDetail = () => {
  selectedProduct.value = null;
  productOptions.value = null;
};

watch(
  [() => topProducts.value.deposit, () => topProducts.value.saving],
  () => {
    fetchAllSubscriptions();
  }
);

onMounted(async () => {
  try {
    await fetchTopProducts();
    await fetchAllSubscriptions();
  } catch (error) {
    console.error('초기 데이터 로드 실패:', error);
  }
});


const onSlideChange = () => {
  console.log('slide change');
};

// Swiper 설정
const swiperModules = [Autoplay];  // 모듈 배열 생성

const swiperInstance = ref(null);

// 모달 상태 감시
watch(() => selectedProduct.value, (newVal) => {
  if (!swiperInstance.value) return;
  
  if (newVal) {
    // 모달이 열릴 때
    swiperInstance.value.autoplay.stop();
    swiperInstance.value.allowTouchMove = false;  // 터치 이동도 비활성화
  } else {
    // 모달이 닫힐 때
    swiperInstance.value.autoplay.start();
    swiperInstance.value.allowTouchMove = true;   // 터치 이동 다시 활성화
  }
});

const onSwiper = (swiper) => {
  swiperInstance.value = swiper;
};

// Swiper 옵션 수정
const swiperOptions = {
  modules: [Autoplay, Navigation],
  slidesPerView: 1,
  loop: true,
  navigation: true,
  autoplay: {
    delay: 5000,
    disableOnInteraction: false,
    pauseOnMouseEnter: true  // 마우스 오버 시 일시정지 추가
  }
};

// displayedProducts computed 속성 추가
const displayedProducts = computed(() => {
  const products = [];
  
  // 예금 상품이 있으면 추가
  if (topProducts.value.deposit?.product) {
    products.push({
      ...topProducts.value.deposit.product,
      options: topProducts.value.deposit.options
    });
  }
  
  // 적금 상품이 있으면 추가
  if (topProducts.value.saving?.product) {
    products.push({
      ...topProducts.value.saving.product,
      options: topProducts.value.saving.options
    });
  }
  
  return products;
});

// 데이터가 제대로 전달되는지 확인하기 위한 watch 추가
watch(topProducts, (newValue) => {
  console.log('topProducts updated:', newValue);
  if (newValue.deposit) {
    console.log('Deposit product options:', newValue.deposit.options[0]);
  }
  if (newValue.saving) {
    console.log('Saving product options:', newValue.saving.options[0]);
  }
}, { deep: true });
</script>

<style lang="scss" scoped>
.home-page {
  .hero-swiper {
    height: 100%;
    margin-top: -97px;
    margin-bottom: 2rem;
  }

  // 히어로 섹션 공통 스타일
  .hero {
    height: 80vh;
    background: linear-gradient(135deg, #000000, #37474f);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;

    .hero-content {
      h1 {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        font-weight: bold;
      }
      
      p {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        opacity: 0.9;
      }
    }

    // 상품 히어로 섹션
    &.hero-products {
      background: linear-gradient(135deg, #2c3e50, #37474f);

      .hero-content {
        width: 100%;
        max-width: 1200px;
        padding: 0 2rem;

        h1 {
          margin-bottom: 2rem;
        }

        .top-products-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          
          .product-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 15px;
            backdrop-filter: blur(10px);

            h2 {
              color: white;
              font-size: 1.5rem;
              margin-bottom: 1.5rem;
            }

            .product-info {
              :deep(.product-card) {
                background: rgba(0, 0, 0, 0.534);
                border-radius: 12px;
                padding: 1.5rem;
                color: white;
                backdrop-filter: blur(5px);
                
                .card-header {
                  .bank-info {
                    img.bank-logo {
                      filter: brightness(0) invert(1);
                    }
                    .bank-name {
                      color: #ffffff;
                    }
                  }
                  .product-name {
                    color: #ffffff;
                    font-size: 1.5rem;
                    
                  }
                }

                .card-body {
                  margin-left: 1rem;
                  margin-right: 1rem;
                  .info-row {

                    .label {
                      color: rgba(255, 255, 255, 0.7);
                      
                    }
                    padding-bottom: 0.5rem;
                    .value {
                      color: white;
                      &.highlight {
                        color: #fffb00;
                      }
                    }
                  }
                }

                &:hover {
                  background: rgba(255, 255, 255, 0.2);
                }
              }
            }
          }
        }
      }
    }
  }

  // CTA 버튼 스타일
  .cta-buttons {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    
    .cta-button {
      padding: 1rem 2rem;
      border-radius: 30px;
      text-decoration: none;
      font-weight: bold;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: transform 0.3s;
      
      i {
        font-size: 1.2rem;
      }
      
      &.primary {
        background: white;
        color: #37474f;
      }
      
      &.secondary {
        border: 2px solid white;
        color: white;
      }
      
      &:hover {
        transform: translateY(-3px);
      }
    }
  }

  // 기능 섹션
  .features {
    padding: 0rem 2rem;
    background: #f8f9fa;
    
    h2 {
      text-align: center;
      font-size: 2.1rem;
      margin-bottom: 0.5rem;
      color: #333;
    }
    
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 2rem;
      max-width: 1200px;
      margin: 0 auto;
      
      .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        text-decoration: none;
        color: inherit;
        display: block;
        
        &:hover {
          transform: translateY(-5px);
        }
        
        i {
          font-size: 2.5rem;
          color: #37474f;
          margin-bottom: 1rem;
        }
        
        h3 {
          font-size: 1.5rem;
          margin-bottom: 1rem;
          color: #333;
        }
        
        p {
          color: #666;
          margin-bottom: 1.5rem;
          line-height: 1.6;
        }
        
        .feature-link {
          color: #37474f;
          text-decoration: none;
          font-weight: bold;
          
          &:hover {
            text-decoration: underline;
          }
        }
      }
    }
  }
}

// 반응형 타일
@media (max-width: 768px) {
  .home-page {
    .hero {
      .hero-content {
        padding: 0 1rem;
        
        h1 {
          font-size: 2.5rem;
        }
        
        p {
          font-size: 1.2rem;
        }
      }

      &.hero-products .top-products-grid {
        grid-template-columns: 1fr;
      }
    }

    .cta-buttons {
      flex-direction: column;
      gap: 1rem;
      
      .cta-button {
        width: 100%;
        justify-content: center;
      }
    }
  }
}

// 히어로 섹션 애니메이션
.hero {
  .hero-content {
    animation: fadeInUp 0.8s ease-out;
    
    h1 {
      animation: slideInDown 1s ease-out;
    }
    
    p {
      animation: slideInLeft 1s ease-out 0.3s;
      animation-fill-mode: both;
    }
    
    .cta-buttons {
      animation: fadeIn 1s ease-out 0.6s;
      animation-fill-mode: both;
      
      .cta-button {
        transition: all 0.3s ease;
        
        &:hover {
          transform: translateY(-3px) scale(1.05);
          box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        &:active {
          transform: translateY(-1px);
        }
      }
    }
  }
}

// 상품 섹션 애니메이션
.hero-products {
  .product-section {
    animation: fadeInUp 0.8s ease-out;
    
    .product-info {
      :deep(.product-card) {
        transition: all 0.3s ease;
        
        &:hover {
          transform: translateY(-5px) scale(1.02);
          box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
      }
    }
  }
}

// 기능 섹션 애니메이션
.features {
  .features-grid {
    .feature-card {
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      animation: fadeInUp 0.8s ease-out;
      animation-fill-mode: both;
      
      @for $i from 1 through 4 {
        &:nth-child(#{$i}) {
          animation-delay: #{$i * 0.15}s;
        }
      }
      
      &:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        
        i {
          transform: scale(1.1) rotate(5deg);
        }
        
        .feature-link {
          color: #1a237e;
        }
      }
      
      i {
        transition: transform 0.3s ease;
      }
    }
  }
}

// 키프레임 정의
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>