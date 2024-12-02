// productStore.ts

// Pinia store와 axios import
import { defineStore } from 'pinia';
import axios from 'axios';

// 기본 상품 정보 인터페이스
interface Product {
  fin_prdt_cd: string;
  kor_co_nm: string;
  fin_prdt_nm: string;
  intr_rate_type_nm: string;
  intr_rate2: number;
  save_trm: number;
  join_way: string;
  product_type?: 'deposit' | 'saving';  // 추가
}

// 상품 옵션 정보 인터페이스
interface Option {
  intr_rate_type_nm: string;    // 금리유형명 (단리/복리)
  intr_rate: number;            // 기본금리
  intr_rate2: number;           // 최고금리
  save_trm: number;             // 저축기간(개월)
  rsrv_type_nm: string;         // 적립유형명 (자유적립식/정액적립식)
  rsrv_type: string;            // 적립유형 코드
  intr_rate_type: string;       // 금리유형 코드
}

// 상품 상세 정보 인터페이스 (기본 상품 정보 확장)
interface DetailProduct extends Product {
  join_deny: number;            // 가입제한 (1:제한없음, 2:서민전용, 3:일부제한)
  join_member: string;          // 가입대상
  join_way: string;            // 가입방법
  spcl_cnd: string;            // 우대조건
  etc_note: string;            // 기타 유의사항
  max_limit: number;           // 최고한도
  detail_options: Option[];     // 상품의 모든 옵션 목록
}


// store의 state 인터페이스
interface ProductState {
  depositProductsList: Product[];
  savingProductsList: Product[];
  displayedDepositProducts: Product[];  // 추가
  displayedSavingProducts: Product[];   // 추가
  currentDepositPage: number;           // 추가
  currentSavingPage: number;           // 추가
  itemsPerPage: number;                // 추가
  loading: boolean;
  error: string | null;
  currentPage: number;
  totalPages: number;
  pageSize: number;
  isLoading: boolean;
  firstTierBanks: string[];
  savingBanks: string[];
  hasMoreDeposits: boolean;
  hasMoreSavings: boolean;
  depositPage: number;    // 예금 페이지 번호
  savingPage: number;     // 적금 페이지 번호
  depositTotalPages: number;  // 예금 총 페이지
  savingTotalPages: number;   // 적금 총 페이지
  firstTierOnly: boolean;
  selectedBanks: string[];
  savingBankOnly: boolean;  // 추가
  bankLogos: { [key: string]: string };
  cachedProducts: {
    deposit: Map<number, Product[]>;  // 페이지별 예금상품 캐시
    saving: Map<number, Product[]>;   // 페이지별 적금상품 캐시
  };
  loadedPages: {
    deposit: Set<number>;
    saving: Set<number>
  }
  wishlist: Product[];
}

const bankLogos: { [key: string]: string } = {
    '우리은행': '/bank-logos/woori.png',
    'SC제일은행': '/bank-logos/sc.png',
    '아이엠뱅크': '/bank-logos/im.png',
    '부산은행': '/bank-logos/busan.png',
    '광주은행': '/bank-logos/gwangju.png',
    '제주은행': '/bank-logos/jeju.png',
    '전북은행': '/bank-logos/jeonbuk.png',
    '경남은행': '/bank-logos/gyeongnam.png',
    'IBK기업은행': '/bank-logos/ibk.png',
    'KDB산업은행': '/bank-logos/kdb.png',
    '국민은행': '/bank-logos/kb.png',
    '신한은행': '/bank-logos/shinhan.png',
    '농협은행': '/bank-logos/nh.png',
    '하나은행': '/bank-logos/hana.png',
    '케이뱅크': '/bank-logos/kbank.png',
    '수협은행': '/bank-logos/suhyup.png',
    '카카오뱅크': '/bank-logos/kakao.png',
    '토스뱅크': '/bank-logos/toss.png',
    '1금융권': '/bank-logos/1.png',
    '애큐온저축은행': '/bank-logos/에큐온.png',
    '오에스비저축은행': '/bank-logos/오에스비.png',
    '디비저축은행': '/bank-logos/디비.png',
    '스카이저축은행': '/bank-logos/스카이.png',
    '민국저축은행': '/bank-logos/민국.png',
    '푸른상호저축은행': '/bank-logos/푸른.png',
    'HB저축은행': '/bank-logos/에이치비.png',
    '키움예스저축은행': '/bank-logos/키움.png',
    '더케이저축은행': '/bank-logos/더케이.png',
    '조은저축은행': '/bank-logos/조은.png',
    '저축은행': '/bank-logos/저축은행.png',
    '흥국저축은행': '/bank-logos/흥국.png',
    '우리저축은행': '/bank-logos/우리.png',
    '키움저축은행': '/bank-logos/키움.png',
    '삼정저축은행': '/bank-logos/삼정.png',
    '영진저축은행': '/bank-logos/영진.png',
    '융창저축은행': '/bank-logos/융창.png',
    '더블저축은행': '/bank-logos/더블.png',
    '센트럴저축은행': '/bank-logos/센트럴.png',
    '오성저축은행': '/bank-logos/오성.png',
    '에스앤티저축은행': '/bank-logos/에스앤티.png',
    '솔브레인저축은행': '/bank-logos/솔브레인.png',
    '신한저축은행': '/bank-logos/신한.png',
    '대신저축은행': '/bank-logos/대신.png',
    '웰컴저축은행': '/bank-logos/웰컴.png',
    '다올저축은행': '/bank-logos/다올.png',
    '인천저축은행': '/bank-logos/인천.png',
    '모아저축은행': '/bank-logos/모아.png',
    '페퍼저축은행': '/bank-logos/페퍼.png',
    '오케이저축은행': '/bank-logos/오케이.png',
    '우리금융저축은행': '/bank-logos/우리금융.png',
    '청주저축은행': '/bank-logos/청주.png',
    '한성저축은행': '/bank-logos/한성.png',
    '상상인플러스저축은행': '/bank-logos/상상인.png',
    '제이티친애저축은행': '/bank-logos/제이티.png',
    '예가람저축은행': '/bank-logos/예가람.png',
    '엔에이치저축은행': '/bank-logos/엔에이치.png',
    '조흥저축은행': '/bank-logos/조흥.png',
    '참저축은행': '/bank-logos/참.png',
    '한국투자저축은행': '/bank-logos/한국투자.png',
    '비엔케이저축은행': '/bank-logos/비엔케이.png',
    '스마트저축은행': '/bank-logos/스마트.png',
    '아이비케이저축은행': '/bank-logos/아이비케이.png',
    '대한저축은행': '/bank-logos/대한.png'
};

// Pinia store 정의
export const useProductStore = defineStore('product', {
  // 초기 상태 정의
  state: (): ProductState => ({
    depositProductsList: [],
    savingProductsList: [],
    displayedDepositProducts: [],  // 추가
    displayedSavingProducts: [],   // 추가
    currentDepositPage: 1,         // 추가
    currentSavingPage: 1,          // 추가
    itemsPerPage: 8,              // 추가
    loading: false,
    error: null,
    currentPage: 1,
    totalPages: 1,
    pageSize: 8,
    isLoading: false,
    firstTierBanks: [
      '우리은행',
      '한국스탠다드차타드은행',
      '아이엠뱅크',
      '부산은행',
      '광주은행',
      '제주은행',
      '전북은행',
      '경남은행',
      '중소기업은행',
      '한국산업은행',
      '국민은행',
      '신한은행',
      '농협은행주식회사',
      '하나은행',
      '주식회사 케이뱅크',
      '수협은행',
      '주식회사 카카오뱅크',
      '토스뱅크 주식회사'
    ],
    savingBanks: [
      '애큐온저축은행',
      '오에스비저축은행',
      '디비저축은행',
      '스카이저축은행',
      '민국저축은행',
      '푸른상호저축은행',
      'HB저축은행',
      '키움예스저축은행',
      '더케이저축은행',
      '조은저축은행',
      '흥국저축은행',
      '우리저축은행',
      '키움저축은행',
      '삼정저축은행',
      '영진저축은행',
      '융창저축은행',
      '더블저축은행',
      '센트럴저축은행',
      '오성저축은행',
      '에스앤티저축은행',
      '솔브레인저축은행',
      '신한저축은행',
      '대신저축은행',
      '웰컴저축은행',
      '다올저축은행',
      '인천저축은행',
      '모아저축은행',
      '페퍼저축은행',
      '오케이축은행',
      '우리금융저축은행',
      '청주저축은행',
      '한성저축은행',
      '상상인플러스저축은행',
      '제이티친애저축은행',
      '예가람저축은행',
      '엔에이치저축은행',
      '조흥저축은행',
      '참저축은행',
      '한국투자저축은행',
      '비엔케이저축은행',
      '스마트저축은행',
      '아이비케이저축은행',
      '대한저축은행',
      '전주저축은행',
      '하나저축은행',
      '진주저축은행',
      '드림저축은행',
      '대명상호저축은행',
      '한화저축은행',
      '상상인저축은행',
      '세람상호저축은행',
      '평택저축은행',
      '남양저축은행',
      '안국저축은행',
      '금화저축은행',
      '디에이치저축은행',
      '국제저축은행',
      '고려저축은행',
      '유안타저축은행',
      '바로저축은행',
      '에스비아이저축은행'
    ],
    hasMoreDeposits: true,
    hasMoreSavings: true,
    depositPage: 1,    // 예금 페이지 번호
    savingPage: 1,     // 적금 페이지 번호
    depositTotalPages: 1,  // 예금 총 페이지
    savingTotalPages: 1,   // 적금 총 페이지
    firstTierOnly: false,
    selectedBanks: [],
    savingBankOnly: false,  // 추가
    bankLogos,
    cachedProducts: {
      deposit: new Map<number, Product[]>(),  // 페이지별 예금상품 캐시
      saving: new Map<number, Product[]>()    // 페이지별 적금상품 캐시
    },
    loadedPages: {
      deposit: new Set<number>(),
      saving: new Set<number>()
    },
    wishlist: []
  }),
  // 계산된 속성 정의
  getters: {
    depositProducts: (state) => state.depositProductsList,  // getter 추가
    savingProducts: (state) => state.savingProductsList,   // getter 추가
    
    // 더 표시할 예금상품이 있는지 확인
    canLoadMoreDeposits: (state) => {
      const canLoad = state.depositPage < state.depositTotalPages;
      console.log('Check can load more deposits:', {
        currentPage: state.depositPage,
        totalPages: state.depositTotalPages,
        canLoad
      });
      return canLoad;
    },
    // 더 표시할 적금상품이 있는지 확인
    canLoadMoreSavings: (state) => {
      const canLoad = state.savingPage < state.savingTotalPages;
      console.log('Check can load more savings:', {
        currentPage: state.savingPage,
        totalPages: state.savingTotalPages,
        canLoad
      });
      return canLoad;
    },
    // 1금융권 상품만 필터링
    firstTierProducts: (state) => (products: Product[]) => {
      return products.filter(product => 
        state.firstTierBanks.includes(product.kor_co_nm)
      );
    },
    // 저축은행 상품만 필터링하는 getter 추가
    savingBankProducts: (state) => (products: Product[]) => {
      return products.filter(product => 
        state.savingBanks.includes(product.kor_co_nm)
      );
    },
    // savingBankOnly 상태를 확인하는 getter 추가
    isSavingBankOnly(): boolean {
      return this.savingBankOnly;
    }
  },

  // 액션(비동기 작업 포함) 정의
  actions: {
    // 상품 옵션 처리 함수
    async processProductOptions(products: Product[], endpoint: string) {
      try {
        return await Promise.all(products.map(async (product) => {
          try {
            // 상품별 상세 옵션 조회
            const response = await axios.get(`${endpoint}${product.fin_prdt_cd}/`);
            const options: Option[] = response.data.options || response.data;
            
            // 옵션이 하나만 있는 경우
            if (options.length === 1) {
              const option = options[0];
              return {
                ...product,
                intr_rate_type_nm: option.intr_rate_type_nm,
                intr_rate: option.intr_rate,
                intr_rate2: option.intr_rate2,
                save_trm: `${option.save_trm}개월`
              };
            } 
            // 옵션이 여러 개인 경우
            else {
              const sortedOptions = [...options].sort((a, b) => a.save_trm - b.save_trm);
              const highestRateOption = options.reduce((max, curr) => 
                curr.intr_rate2 > max.intr_rate2 ? curr : max, options[0]);
              
              return {
                ...product,
                intr_rate_type_nm: highestRateOption.intr_rate_type_nm,
                intr_rate: highestRateOption.intr_rate,
                intr_rate2: highestRateOption.intr_rate2,
                save_trm: sortedOptions[0].save_trm === sortedOptions[sortedOptions.length-1].save_trm
                  ? `${highestRateOption.save_trm}개월`
                  : `${sortedOptions[0].save_trm}~${sortedOptions[sortedOptions.length-1].save_trm}개월`
              };
            }
          } catch (error) {
            console.warn(`상품 ${product.fin_prdt_cd}의 옵션 조회 실패:`, error);
            // 에러 발생 시 기본 상품 정보만 반환
            return {
              ...product,
              intr_rate_type_nm: '정보 없음',
              intr_rate: 0,
              intr_rate2: 0,
              save_trm: '정보 없음'
            };
          }
        }));
      } catch (error) {
        console.error('상품 옵션 처리 중 오류 발생:', error);
        return products.map(product => ({
          ...product,
          intr_rate_type_nm: '정보 없음',
          intr_rate: 0,
          intr_rate2: 0,
          save_trm: '정보 없음'
        }));
      }
    },

    // 예금상품 목록 조회
    async fetchDepositProducts() {
      try {
        this.isLoading = true;
        this.error = null;
        
        const params = {
          page: this.depositPage,
          page_size: this.pageSize,
          first_tier_only: this.firstTierOnly,
          saving_bank_only: this.savingBankOnly,
          banks: this.selectedBanks.length > 0 ? this.selectedBanks.join(',') : undefined
        };
        
        console.log('Requesting deposits with params:', params);
        
        const response = await axios.get('/api/products/deposits/', { params });
        
        this.depositTotalPages = response.data.total_pages;
        const results = response.data.results || [];
        
        const processedProducts = await this.processProductOptions(results, '/api/products/deposits/');
        
        if (this.depositPage === 1) {
          this.depositProductsList = processedProducts;
          this.displayedDepositProducts = processedProducts;
        } else {
          this.depositProductsList = [...this.depositProductsList, ...processedProducts];
          this.displayedDepositProducts = this.depositProductsList;
        }
        
      } catch (error) {
        console.error('예금 상품 조회 실패:', error);
        this.error = '예금 상품을 불러오는데 실패했습니다.';
        this.depositProductsList = [];
        this.displayedDepositProducts = [];
      } finally {
        this.isLoading = false;
      }
    },
    // firstTierBanks 배열이 백엔드의 FIRST_TIER_BANKS와 일치하는지 확인
    
    
    async fetchSavingProducts() {
      try {
        this.isLoading = true;
        this.error = null;
        
        const params = {
          page: this.savingPage,
          page_size: this.pageSize,
          first_tier_only: this.firstTierOnly,
          saving_bank_only: this.savingBankOnly,
          banks: this.selectedBanks.length > 0 ? this.selectedBanks.join(',') : undefined
        };
        
        console.log('Requesting savings with params:', params);
        
        const response = await axios.get('/api/products/savings/', { params });
        
        this.savingTotalPages = response.data.total_pages;
        const results = response.data.results || [];
        
        const processedProducts = await this.processProductOptions(results, '/api/products/savings/');
        
        if (this.savingPage === 1) {
          this.savingProductsList = processedProducts;
          this.displayedSavingProducts = processedProducts;
        } else {
          this.savingProductsList = [...this.savingProductsList, ...processedProducts];
          this.displayedSavingProducts = this.savingProductsList;
        }
        
      } catch (error) {
        console.error('적금 상품 조회 실패:', error);
        this.error = '적금 상품을 불러오는데 실패했습니다.';
        this.savingProductsList = [];
        this.displayedSavingProducts = [];
      } finally {
        this.isLoading = false;
      }
    },

    async loadMoreDeposits() {
      if (!this.canLoadMoreDeposits || this.isLoading) {
        console.log('Cannot load more deposits:', { 
          canLoad: this.canLoadMoreDeposits, 
          isLoading: this.isLoading,
          currentPage: this.depositPage,
          totalPages: this.depositTotalPages
        });
        return;
      }

      try {
        this.isLoading = true;
        this.depositPage += 1;
        
        console.log(`Loading deposits page ${this.depositPage}`);
        
        const params = {
          page: this.depositPage,
          page_size: this.pageSize,
          banks: this.selectedBanks.length > 0 ? this.selectedBanks.join(',') : undefined
        };

        if (this.firstTierOnly) {
          params.banks = this.firstTierBanks.join(',');
        } else if (this.savingBankOnly) {
          params.banks = this.savingBanks.join(',');
        }
        
        const response = await axios.get('/api/products/deposits/', { params });
        const results = response.data.results || [];
        
        if (results.length > 0) {
          const newProducts = await this.processProductOptions(results, '/api/products/deposits/');
          this.depositProductsList = [...this.depositProductsList, ...newProducts];
          this.displayedDepositProducts = this.depositProductsList;
          
          // 페이지네이션 정보 업데이트
          this.depositTotalPages = response.data.total_pages;
          console.log(`Added ${newProducts.length} new deposits, total: ${this.depositProductsList.length}`);
        } else {
          console.log('No more deposits to load');
          this.canLoadMoreDeposits = false;
        }
        
      } catch (error) {
        console.error('추가 예금 상품 로드 실패:', error);
        this.depositPage -= 1;  // 실패 시 페이지 번호 롤백
      } finally {
        this.isLoading = false;
      }
    },

    async loadMoreSavings() {
      if (!this.canLoadMoreSavings || this.isLoading) {
        console.log('Cannot load more savings:', { 
          canLoad: this.canLoadMoreSavings, 
          isLoading: this.isLoading,
          currentPage: this.savingPage,
          totalPages: this.savingTotalPages
        });
        return;
      }

      try {
        this.isLoading = true;
        this.savingPage += 1;
        
        console.log(`Loading savings page ${this.savingPage}`);
        
        const params = {
          page: this.savingPage,
          page_size: this.pageSize,
          banks: this.selectedBanks.length > 0 ? this.selectedBanks.join(',') : undefined
        };

        if (this.firstTierOnly) {
          params.banks = this.firstTierBanks.join(',');
        } else if (this.savingBankOnly) {
          params.banks = this.savingBanks.join(',');
        }
        
        const response = await axios.get('/api/products/savings/', { params });
        const results = response.data.results || [];
        
        if (results.length > 0) {
          const newProducts = await this.processProductOptions(results, '/api/products/savings/');
          this.savingProductsList = [...this.savingProductsList, ...newProducts];
          this.displayedSavingProducts = this.savingProductsList;
          
          // 페이지네이션 정보 업데이트
          this.savingTotalPages = response.data.total_pages;
          console.log(`Added ${newProducts.length} new savings, total: ${this.savingProductsList.length}`);
        } else {
          console.log('No more savings to load');
          this.canLoadMoreSavings = false;
        }
        
      } catch (error) {
        console.error('추가 적금 상품 로드 실패:', error);
        this.savingPage -= 1;  // 실패 시 페이지 번호 롤백
      } finally {
        this.isLoading = false;
      }
    },

    resetPagination() {
      this.depositPage = 1;
      this.savingPage = 1;
      this.depositTotalPages = 1;  // 변경
      this.savingTotalPages = 1;   // 변경
      this.depositProductsList = [];
      this.savingProductsList = [];
      this.displayedDepositProducts = [];
      this.displayedSavingProducts = [];
      // savingBankOnly는 여기서 초기화하지 않음
    },

    async fetchProductDetail(productCode: string, type: 'deposit' | 'saving') {
      try {
        const endpoint = type === 'deposit' ? 'deposits' : 'savings';
        const response = await axios.get(`/api/products/${endpoint}/${productCode}/`);
        return response.data;  // 전체 응답 데이터를 그대로 반환
      } catch (error) {
        console.error('상품 상세정보 조회 실패:', error);
        return null;
      }
    },

    // 상품 데이터 초기 저
    async initializeProductsData() {
      try {
        this.loading = true;
        this.error = null;
        
        await Promise.all([
          axios.get('/api/products/save-deposit-products/'),
          axios.get('/api/products/save-saving-products/')
        ]);

        await this.fetchProducts('deposit', 1);
        await this.fetchProducts('saving', 1);

      } catch (error) {
        console.error('상품 데이터 초기화 실패:', error);
        this.error = '상품 데이터를 가져는데 실패했습니다.';
      } finally {
        this.loading = false;
      }
    },

    async fetchProducts(type: 'deposit' | 'saving', page: number) {
      try {
        // 이미 로드된 페이지인지 확인
        if (this.loadedPages[type].has(page)) {
          return true;
        }

        this.isLoading = true;
        const endpoint = type === 'deposit' ? 'deposits' : 'savings';
        
        const params = {
          page,
          page_size: this.pageSize,
          first_tier_only: this.firstTierOnly,
          saving_bank_only: this.savingBankOnly,
          banks: this.selectedBanks.length > 0 ? this.selectedBanks.join(',') : undefined
        };

        const response = await axios.get(`/api/products/${endpoint}/`, { params });
        const newProducts = response.data.results;
        
        // 페이지 정보 업데이트 및 데이터 병합
        if (type === 'deposit') {
          this.depositTotalPages = response.data.total_pages;
          this.depositPage = page;
          this.depositProductsList = [...this.depositProductsList, ...newProducts];
          this.displayedDepositProducts = this.depositProductsList;
        } else {
          this.savingTotalPages = response.data.total_pages;
          this.savingPage = page;
          this.savingProductsList = [...this.savingProductsList, ...newProducts];
          this.displayedSavingProducts = this.savingProductsList;
        }

        // 로드된 페이지 기록
        this.loadedPages[type].add(page);
        
        return true;
      } catch (error) {
        console.error(`${type} 상품 조회 실패:`, error);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async loadMoreProducts(type: 'deposit' | 'saving') {
      if (this.currentPage < this.totalPages && !this.isLoading) {
        this.currentPage++;
        await this.fetchProducts(type, this.currentPage);
      }
    },

    // 저축은행 토글 액션 수정
    async toggleSavingBank() {
      this.savingBankOnly = !this.savingBankOnly;
      console.log('toggleSavingBank called:', this.savingBankOnly);
      
      // 다른 필터 초기화
      this.firstTierOnly = false;
      this.selectedBanks = [];
      
      this.resetPagination();
      
      // 현재 상태에 따라 데이터 다시 불러오기
      await this.fetchDepositProducts();
      await this.fetchSavingProducts();
    },

    // resetFilters 액션 수정
    resetFilters() {
      this.firstTierOnly = false;
      this.savingBankOnly = false;  // 추가
      this.selectedBanks = [];
      this.clearCache(); // 캐시 초기화 추가
    },

    // changeProductType 액션 수정.
    changeProductType(type: 'deposit' | 'saving') {
      this.resetFilters();  // 필터 초기화
    },

    // 필터 변경 시 캐시 초기화
    clearCache() {
      this.cachedProducts.deposit.clear();
      this.cachedProducts.saving.clear();
    },

    // 필터 변경 시 데이터 초기화
    resetProducts(type: 'deposit' | 'saving') {
      if (type === 'deposit') {
        this.depositProductsList = [];
        this.displayedDepositProducts = [];
      } else {
        this.savingProductsList = [];
        this.displayedSavingProducts = [];
      }
      this.loadedPages[type].clear();
    },

    addToWishlist(product: Product) {
      if (!this.wishlist.some(p => p.fin_prdt_cd === product.fin_prdt_cd)) {
        this.wishlist.push(product);
        localStorage.setItem('wishlist', JSON.stringify(this.wishlist));
      }
    },

    removeFromWishlist(productCode: string) {
      this.wishlist = this.wishlist.filter(p => p.fin_prdt_cd !== productCode);
      localStorage.setItem('wishlist', JSON.stringify(this.wishlist));
    }
  },
  
});