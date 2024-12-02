// ProductDetailModal.vue
<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <button class="close-button" @click="closeModal">&times;</button>
      
      <div class="modal-header">
        <p class="bank-name">{{ product.kor_co_nm }}</p>
        <h2 class="product-name">{{ product.fin_prdt_nm }}</h2>
      </div>

      <div class="modal-body">
        <!-- 가입 정보 섹션 -->
        <section class="info-section">
          <h3>가입 정보</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">가입 방법</span>
              <span class="value">{{ product.join_way }}</span>
            </div>
            <div class="info-item">
              <span class="label">가입 대상</span>
              <span class="value">{{ product.join_member }}</span>
            </div>
            <div class="info-item">
              <span class="label">가입 제한</span>
              <span class="value">{{ getJoinDenyText(product.join_deny) }}</span>
            </div>
            <div class="info-item">
              <span class="label">최고 한도</span>
              <span class="value">{{ formatAmount(product.max_limit) }}</span>
            </div>
          </div>
        </section>

        <!-- 금리 정보 섹션 -->
        <section class="info-section">
          <h3>금리 정보</h3>
          <div class="rate-type-tabs">
            <button 
              :class="['tab-button', { active: selectedRateType === '단리' }]"
              @click="selectedRateType = '단리'"
            >
              단리
            </button>
            <button 
              :class="['tab-button', { active: selectedRateType === '복리' }]"
              @click="selectedRateType = '복리'"
            >
              복리
            </button>
          </div>
          
          <div v-if="filteredOptions.length === 0" class="no-options-message">
            해당되는 상품이 없습니다.
          </div>
          
          <div v-else v-for="option in filteredOptions" :key="option.id" class="rate-option">
            <h4>{{ option.save_trm }}개월</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">금리 유형</span>
                <span class="value">{{ option.intr_rate_type_nm }}</span>
              </div>
              <div class="info-item">
                <span class="label">기본 금리</span>
                <span class="value">{{ option.intr_rate }}%</span>
              </div>
              <div class="info-item">
                <span class="label">최고 금리</span>
                <span class="value highlight">{{ option.intr_rate2 }}%</span>
              </div>
              <button 
                :class="[
                  'subscribe-button',
                  { 'subscribed': subscribedOptionId === option.id }
                ]"
                @click="subscribeProduct(option.fin_prdt_cd, option.id)"
                :disabled="subscribedOptionId !== null && subscribedOptionId !== option.id"
              >
                {{ subscribedOptionId === option.id ? '가입된 상품' : '미가입 상품' }}
              </button>
            </div>
          </div>
        </section>

        <!-- 우대조건 섹션 -->
        <section class="info-section">
          <h3>우대조건</h3>
          <p class="description">{{ product.spcl_cnd || '해당사항 없음' }}</p>
        </section>

        <!-- 유의사항 섹션 -->
        <section class="info-section">
          <h3>기타 유의사항</h3>
          <p class="description">{{ product.etc_note || '해당사항 없음' }}</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDate } from '@/utils/formatters';
import type { Product } from '@/types/product';
import { useAuthStore } from '@/stores/authStore';
import api from '@/utils/axios'
import type { AxiosError } from 'axios'
import { ref, watch, onMounted, onUpdated, computed } from 'vue'


const authStore = useAuthStore();
// const isSubscribed = ref(false);  // 추가
// const subscribedOptionId = ref<number | null>(null);
// const selectedOption = ref<number | null>(null);

const props = defineProps<{
  isOpen: boolean;
  product: Product;
  detailOptions: Array<{
    id: number;
    fin_prdt_cd: string;
    intr_rate_type_nm: string;
    intr_rate: number;
    intr_rate2: number;
    save_trm: number;
    product: number;
  }> | null;
  product_type: 'deposit' | 'saving';
}>();

const subscribedOptionId = ref<number | null>(null);
const selectedRateType = ref('단리');

const filteredOptions = computed(() => {
  return props.detailOptions?.filter(option => 
    option.intr_rate_type_nm === selectedRateType.value
  ) || [];
});

const checkSubscription = async (fin_prdt_cd: string, option_id: number) => {
  try {
    const response = await api.get('/api/products/user-products/', {
      params: {
        fin_prdt_cd,
        option_id,
        product_type: props.product.product_type || props.product_type
      }
    });
    
    if (response.data.is_subscribed && response.data.option_id === option_id) {
      subscribedOptionId.value = option_id;
    } else if (subscribedOptionId.value === option_id) {
      subscribedOptionId.value = null;
    }
  } catch (error) {
    console.error('구독 상태 확인 실패:', error);
    subscribedOptionId.value = null;
  }
};
onMounted(async () => {
  if (props.detailOptions) {
    for (const option of props.detailOptions) {
      await checkSubscription(props.product.fin_prdt_cd, option.id);
    }
  }
});
watch(
  () => props.product,
  async () => {
    if (props.detailOptions) {
      for (const option of props.detailOptions) {
        await checkSubscription(props.product.fin_prdt_cd, option.id);
      }
    }
  }
);
// props.product나 props.product_type이 변경될 때만 체크


const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'subscription-change', productId: string, isSubscribed: boolean): void;
}>();

const subscribeProduct = async (fin_prdt_cd: string, option_id: number) => {
  try {
    const isCurrentlySubscribed = subscribedOptionId.value === option_id;
    await api.post('/api/products/user-products/', {
      fin_prdt_cd,
      option_id,
      product_type: props.product.product_type || props.product_type
    });
    
    // 상태 업데이트 전에 서버에서 현재 상태 다시 확인
    await checkSubscription(fin_prdt_cd, option_id);
    
    const newSubscriptionState = subscribedOptionId.value === option_id;

    
    emit('subscription-change', props.product.fin_prdt_cd, newSubscriptionState);
    
  } catch (error) {
    const axiosError = error as AxiosError;
    if (axiosError.response?.status === 404) {
      alert('존재하지 않는 상품입니다.');
    } else if (axiosError.response?.status === 400) {
      alert(axiosError.response.data.error || '상품 가입에 실패했습니다.');
    } else {
      alert('상품 가입 중 오류가 발생했습니다.');
    }
    console.error('상품 가입 실패:', error);
  }
};

const getJoinDenyText = (joinDeny: number) => {
  const texts = {
    1: '제한없음',
    2: '서민전용',
    3: '일부제한'
  };
  return texts[joinDeny as keyof typeof texts] || '정보없음';
};

const formatAmount = (amount: number) => {
  if (!amount) return '제한없음';
  return new Intl.NumberFormat('ko-KR').format(amount) + '원';
};

const closeModal = () => {
  emit('close');
};


</script>

<style lang="scss" scoped>
.modal-overlay {
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;

  .close-button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    border: none;
    background: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
  }

  .modal-header {
    margin-bottom: 2rem;

    .bank-name {
      color: #666;
      font-size: 1rem;
      margin: 0;
    }

    .product-name {
      color: #333;
      font-size: 1.5rem;
      margin: 0.5rem 0;
    }
  }

  .modal-body {
    .info-section {
      margin-bottom: 2rem;
      
      h3 {
        color: #2c3e50;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        border-bottom: 2px solid #eee;
        padding-bottom: 0.5rem;
      }

      .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;

        .info-item {
          display: flex;
          flex-direction: column;
          
          .label {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.25rem;
          }

          .value {
            font-weight: 500;
            
            &.highlight {
              color: #2c3e50;
              font-weight: 600;
            }
          }
        }
      }

      .description {
        white-space: pre-line;
        color: #666;
        line-height: 1.6;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
      }
    }

    .rate-option {
      margin-bottom: 1.5rem;
      padding: 1rem;
      background: #f8f9fa;
      border-radius: 8px;

      h4 {
        color: #2c3e50;
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
      }

      &:last-child {
        margin-bottom: 0;
      }

      .info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
      }
    }

    .rate-type-tabs {
      display: flex;
      gap: 1rem;
      margin-bottom: 1.5rem;
      
      .tab-button {
        padding: 0.5rem 2rem;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background: white;
        cursor: pointer;
        font-size: 1rem;
        transition: all 0.3s ease;

        &.active {
          background: #2c3e50;
          color: white;
          border-color: #2c3e50;
        }
      }
    }

    .subscribe-button {
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.3s ease;
      width: 100%;
      margin-top: 1rem;
      
      &:not(.subscribed) {
        background: #f0f0f0;
        color: #666;
        
        &:hover:not(:disabled) {
          background: #e0e0e0;
        }
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
      
      &.subscribed {
        background: #fae300; // KB 스타일 노란색
        color: #000000;
        font-weight: bold;
        
        &:hover {
          background: #e6d000;
        }
      }
    }

    .no-options-message {
      text-align: center;
      color: #999;
      padding: 2rem;
      background: #f8f9fa;
      border-radius: 8px;
      margin: 1rem 0;
    }
  }
}
</style>