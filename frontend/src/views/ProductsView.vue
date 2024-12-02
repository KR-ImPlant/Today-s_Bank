// ProductsView.vue
<template>
  <div class="products-view">
    <div class="filter-selector">
      <div class="product-type-selector">
        <div class="switch-container">
          <button 
            :class="{ active: activeType === 'deposit' }"
            @click="() => changeProductType('deposit')"
          >
            예금상품
          </button>
          <button 
            :class="{ active: activeType === 'saving' }"
            @click="() => changeProductType('saving')"
          >
            적금상품
          </button>
          <div class="slider" :class="{ 'slide-right': activeType === 'saving' }"></div>
        </div>
      </div>

      <div class="bank-filter-buttons">
        <button
          :class="{ active: productStore.firstTierOnly }"
          @click="toggleFirstTier"
        >
          <img 
            v-if="productStore.bankLogos['1금융권']"
            :src="productStore.bankLogos['1금융권']"
            :alt="'1금융권'"
            class="bank-logo"
          />
          1금융권
        </button>

        <button
          :class="{ active: productStore.savingBankOnly }"
          @click="handleSavingBankToggle"
        >
          <img 
            v-if="productStore.bankLogos['저축은행']"
            :src="productStore.bankLogos['저축은행']"
            :alt="'저축은행'"
            class="bank-logo"
          />
          저축은행
        </button>
      </div>

      <div class="bank-lists-container">
        <div class="bank-list">
          <swiper
            :slides-per-view="'auto'"
            :space-between="10"
            class="bank-swiper"
          >
            <swiper-slide 
              v-for="bank in productStore.firstTierBanks"
              :key="bank"
              class="bank-slide"
            >
              <button
                :class="{ active: productStore.selectedBanks.includes(bank) }"
                @click="toggleBank(bank)"
              >
                <img 
                  v-if="productStore.bankLogos[formatBankName(bank)]"
                  :src="productStore.bankLogos[formatBankName(bank)]"
                  :alt="bank"
                  class="bank-logo"
                />
                <span>{{ formatBankName(bank) }}</span>
              </button>
            </swiper-slide>
          </swiper>
        </div>

        <div class="bank-list">
          <swiper
            :slides-per-view="'auto'"
            :space-between="10"
            class="bank-swiper"
          >
            <swiper-slide 
              v-for="bank in productStore.savingBanks"
              :key="bank"
              class="bank-slide"
            >
              <button
                :class="{ active: productStore.selectedBanks.includes(bank) }"
                @click="toggleBank(bank)"
              >
                <img 
                  :src="productStore.bankLogos[bank] || '/bank-logos/저축은행.png'"
                  :alt="bank"
                  class="bank-logo"
                />
                <span>{{ bank }}</span>
              </button>
            </swiper-slide>
          </swiper>
        </div>
      </div>
    </div>

    <div class="sort-selector">
      <select v-model="sortOption" class="sort-dropdown">
        <option value="none">정렬 기준</option>
        <option value="basic_rate">최고 기본금리 순</option>
        <option value="prime_rate">최고 우대금리 순</option>
      </select>
    </div>

    <div class="products-grid">
      <TransitionGroup 
        name="product-list" 
        tag="div" 
        class="products-grid-inner"
      >
        <ProductCard 
          v-for="product in displayedProducts" 
          :key="product.fin_prdt_cd"
          :product="product"
          :is-subscribed="subscriptionMap.get(product.fin_prdt_cd)"
          @click="openProductDetail"
        />
      </TransitionGroup>
    </div>

    <div 
      v-if="productStore.loadingMore" 
      class="loading-indicator"
    >
      로딩 중...
    </div>

    <div 
      ref="observerTarget" 
      class="observer-target"
      v-show="activeType === 'deposit' ? productStore.canLoadMoreDeposits : productStore.canLoadMoreSavings"
    ></div>

    <ProductDetailModal
    v-if="selectedProduct"
    :is-open="!!selectedProduct"
    :product="selectedProduct"
    :detail-options="productOptions"
    :product_type="activeType"
    @close="closeProductDetail"
    @subscription-change="handleSubscriptionChange"
  />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useProductStore } from '@/stores/productStore';
import ProductCard from '@/components/Products/ProductCard.vue';
import ProductDetailModal from '@/components/Products/ProductDetailModal.vue';
import type { Product } from '@/types/product';
import api from '@/utils/axios';
import { formatBankName } from '@/utils/bankNameFormatter';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Navigation } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';

const productStore = useProductStore();
const activeType = ref<'deposit' | 'saving'>('deposit');
const selectedBanks = ref<string[]>([]);
const selectedProduct = ref<Product | null>(null);
const productOptions = ref<Array<{
  id: number;
  fin_prdt_cd: string;
  intr_rate_type_nm: string;
  intr_rate: number;
  intr_rate2: number;
  save_trm: number;
  product: number;
}> | null>(null);
//수정

// 구독 상태를 저장할 Map 추가
const subscriptionMap = ref(new Map<string, boolean>());

// 정렬 옵션을 위한 ref 추가 (기존 ref 선언부 근처에 추가)
const sortOption = ref('none');

// activeType이 변경될 때마다 페이지네이션 초기화
watch(activeType, () => {
  productStore.resetPagination();
});

// 상품 타입 변경 함수
const changeProductType = async (type: 'deposit' | 'saving') => {
  activeType.value = type;
  productStore.firstTierOnly = false;
  productStore.selectedBanks = [];
  await loadProducts();
};

// 상품 데이터 로드 함수
const loadProducts = async () => {
  try {
    if (activeType.value === 'deposit') {
      await productStore.fetchDepositProducts();
    } else {
      await productStore.fetchSavingProducts();
    }
  } catch (error) {
    console.error('상품 데이터 로드 실패:', error);
  }
};

const toggleFirstTier = async () => {
  productStore.firstTierOnly = !productStore.firstTierOnly;
  productStore.savingBankOnly = false;
  productStore.selectedBanks = [];
  productStore.resetPagination();
  await loadProducts();
};

const toggleBank = async (bank: string) => {
  productStore.firstTierOnly = false;
  productStore.savingBankOnly = false;
  const index = productStore.selectedBanks.indexOf(bank);
  if (index === -1) {
    productStore.selectedBanks.push(bank);
  } else {
    productStore.selectedBanks.splice(index, 1);
  }
  
  productStore.resetPagination();
  await loadProducts();
};

const handleSavingBankToggle = async () => {
  productStore.savingBankOnly = !productStore.savingBankOnly;
  productStore.firstTierOnly = false;
  productStore.selectedBanks = [];
  productStore.resetPagination();
  await loadProducts();
};

const displayedProducts = computed(() => {
  let products = activeType.value === 'deposit' 
    ? productStore.displayedDepositProducts 
    : productStore.displayedSavingProducts;

  // 정렬 로직 추가
  if (sortOption.value !== 'none') {
    return [...products].sort((a, b) => {
      if (sortOption.value === 'basic_rate') {
        return b.intr_rate - a.intr_rate;
      } else if (sortOption.value === 'prime_rate') {
        return b.intr_rate2 - a.intr_rate2;
      }
      return 0;
    });
  }

  return products;
});

const openProductDetail = async (product: Product) => {
  try {
    const response = await productStore.fetchProductDetail(
      product.fin_prdt_cd, 
      activeType.value
    );
    if (response) {
      selectedProduct.value = response.product;
      productOptions.value = response.options;
    }
  } catch (error) {
    console.error('상품 상세 정보 조회 실패:', error);
  }
};

const closeProductDetail = () => {
  selectedProduct.value = null;
  productOptions.value = null;
};

// 구독 상태 변경 핸들러 추가
const handleSubscriptionChange = async (productId: string, isSubscribed: boolean) => {
  subscriptionMap.value.set(productId, isSubscribed);
  await fetchAllSubscriptions();
};

// 한 번의 API 호출로 모든 상품의 구독 상태를 가져오는 함수
const fetchAllSubscriptions = async () => {
  try {
    const response = await api.get('/api/products/user-products/all/', {
      params: {
        product_type: activeType.value,
      }
    });
    
    // 응답 데이터가 객체 형태이므로 Map으로 변환
    const newMap = new Map();
    Object.entries(response.data).forEach(([fin_prdt_cd, data]: [string, any]) => {
      newMap.set(fin_prdt_cd, data.is_subscribed);
    });
    subscriptionMap.value = newMap;
  } catch (error) {
    console.error('구독 상태 조회 실패:', error);
  }
};

// 상품 목록이 변경될 때마다 구독 상태 일괄 조회
watch([activeType, displayedProducts], () => {
  fetchAllSubscriptions();
});

// 인터섹션 옵저버 대상 요소 참조
const observerTarget = ref<HTMLElement | null>(null);

// 인터섹션 옵저버 설정
const setupIntersectionObserver = () => {
  const observer = new IntersectionObserver(
    async (entries) => {
      const target = entries[0];
      if (target.isIntersecting && !productStore.isLoading) {
        if (activeType.value === 'deposit') {
          await productStore.loadMoreDeposits();
        } else {
          await productStore.loadMoreSavings();
        }
      }
    },
    {
      threshold: 0.1,
      rootMargin: '100px'
    }
  );

  if (observerTarget.value) {
    observer.observe(observerTarget.value);
  }

  return observer;
};

// 컴포넌트 마운트 시 옵저버 설정
onMounted(() => {
  const observer = setupIntersectionObserver();
  
  onUnmounted(() => {
    observer.disconnect();
  });
});

const hasMoreProducts = computed(() => {
  return productStore.currentPage < productStore.totalPages;
});

onMounted(async () => {
  try {
    await changeProductType('deposit')
    await productStore.initializeProductsData()
  } catch (error) {
    console.error('상품 데이터 로드 실패:', error);
  }
});

</script>

<style lang="scss" scoped>
.products-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 15px;

  h1 {
    text-align: center;
    margin-bottom: 2rem;
  }

  .product-type-selector {
    display: flex;
    justify-content: center;
    margin-bottom: 2rem;

    .switch-container {
      position: relative;
      display: flex;
      background: #f0f0f0;
      border-radius: 30px;
      padding: 4px;
      width: fit-content;
      
      > button {
        all: unset;
        position: relative;
        z-index: 1;
        padding: 8px 24px;
        cursor: pointer;
        font-weight: 500;
        color: #666;
        transition: color 0.3s ease;
        border-radius: 30px;

        &.active {
          color: #fff;
        }
      }

      .slider {
        position: absolute;
        top: 4px;
        left: 4px;
        width: calc(50% - 4px);
        height: calc(100% - 8px);
        background: #2c3e50;
        border-radius: 30px;
        transition: transform 0.3s ease;

        &.slide-right {
          transform: translateX(100%);
        }
      }
    }
  }

  .products-grid {
    .products-grid-inner {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }
  }

  .loading-indicator {
    text-align: center;
    padding: 1rem;
    color: #666;
  }

  .error {
    color: #ff4444;
  }

  .filter-selector {
    margin: 1rem 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    align-items: center;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 1rem;
    background: #ffffff;
    overflow: hidden;

    .bank-filter-buttons {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .bank-lists-container {
      width: 100%;
      overflow: hidden;
    }

    .bank-list {
      width: 100%;
      margin-bottom: 1rem;
    }

    .bank-swiper {
      width: 100%;
      
      .bank-slide {
        width: 120px !important;
        height: 70px !important;
      }
    }

    button {
      width: 120px;
      height: 70px;
      padding: 0.5rem 1rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      background: white;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;

      &.active {
        background: #2c3e50 !important;
        color: white !important;
        border-color: #2c3e50 !important;

        img {
          filter: brightness(0) invert(1);
        }
      }

      img {
        width: 24px;
        height: 24px;
        object-fit: contain;
      }

      span {
        font-size: 0.9rem;
        text-align: center;
        white-space: nowrap;
      }
    }
  }

  .observer-target {
    height: 20px;
    margin-top: 1rem;
  }
}

.sort-selector {
  display: flex;
  justify-content: flex-end;
  margin: 1rem 0;
  padding: 0 1rem;

  .sort-dropdown {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
    font-size: 0.9rem;
    cursor: pointer;
    outline: none;
    transition: border-color 0.2s;

    &:hover {
      border-color: #2c3e50;
    }

    &:focus {
      border-color: #2c3e50;
      box-shadow: 0 0 0 2px rgba(44, 62, 80, 0.1);
    }

    option {
      padding: 0.5rem;
    }
  }
}

.chart-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 2rem;
  height: 500px;
  overflow: hidden;

  .chart-container {
    height: calc(100% - 3rem);
    position: relative;
    width: 100%;
    padding-right: 1rem;
    
    canvas {
      max-width: 98% !important;
      max-height: 100% !important;
      width: 98% !important;
      height: 100% !important;
      object-fit: contain;
    }
  }
}
</style>