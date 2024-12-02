// ProductCard.vue
<template>
  <div class="product-card" @click="openModal">
    <div class="subscription-badge" v-if="isSubscribed">
      가입중
    </div>
    <div class="card-header">
      <div class="bank-info">
        <img 
          class="bank-logo" 
          :src="productStore.bankLogos[formatBankName(product.kor_co_nm)]|| '/bank-logos/저축은행.png'" 
          :alt="product.kor_co_nm"
        >
        <span class="bank-name">{{ formatBankName(product.kor_co_nm) }}</span>
      </div>
      <h3 class="product-name">{{ product.fin_prdt_nm }}</h3>
    </div>
    <div class="card-body">
      <div class="info-row">
        <span class="label">금리유형</span>
        <span class="value">{{ product.intr_rate_type_nm }}</span>
      </div>
      <div class="info-row">
        <span class="label">기본금리</span>
        <span class="value">{{ product.intr_rate }}%</span>
      </div>
      <div class="info-row">
        <span class="label">최고금리</span>
        <span class="value highlight">{{ product.intr_rate2 }}%</span>
      </div>
      <div class="info-row">
        <span class="label">저축기간</span>
        <span class="value">{{ product.save_trm }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import api from '@/utils/axios';
import { useProductStore } from '@/stores/productStore';
import { formatBankName } from '@/utils/bankNameFormatter';

interface Product {
  fin_prdt_cd: string
  kor_co_nm: string
  fin_prdt_nm: string
  intr_rate_type_nm: string
  intr_rate: number
  intr_rate2: number
  save_trm: string
  product_type?: 'deposit' | 'saving'
}
const productStore = useProductStore();
const props = defineProps<{
  product: Product;
  isSubscribed?: boolean;
}>()

const emit = defineEmits<{
  (e: 'click', product: Product): void;
}>();

const isSubscribed = computed(() => props.isSubscribed || false);

const openModal = () => {
  emit('click', props.product);
};
</script>

<style lang="scss" scoped>
.product-card {
  position: relative;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-2px);
  }

  .subscription-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background-color: #4CAF50;
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
  }

  .card-header {
    margin-bottom: 1rem;
    
    .bank-info {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .bank-logo {
        height: 20px;
        width: auto;
        object-fit: contain;
      }

      .bank-name {
        font-size: 0.9rem;
        color: #666;
      }
    }

    .product-name {
      color: #333;
      font-size: 1.2rem;
      margin: 0.5rem 0;
    }
  }

  .card-body {
    .info-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.5rem;

      .label {
        color: #666;
        font-size: 0.9rem;
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
}
</style>