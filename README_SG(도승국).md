# 프로젝트 개발 과정에서의 주요 이슈와 해결방안

## 목차
1. [금융상품 데이터 초기화 및 로딩 문제](#1-금융상품-데이터-초기화-및-로딩-문제)
2. [금융상품 가입 기능 구현 시 인증 및 상태 관리 문제](#2-금융상품-가입-기능-구현-시-인증-및-상태-관리-문제)
3. [금융상품 가입여부 확인 기능 구현](#3-금융상품-가입여부-확인-기능-구현)
4. [금융상품 가입 시 외래키 제약조건 오류](#4-금융상품-가입-시-외래키-제약조건-오류)
5. [금융상품 가입/해지 토글 기능 구현 문제](#5-금융상품-가입해지-토글-기능-구현-문제)
6. [환전 계산기의 양방향 입력 문제](#6-환전-계산기의-양방향-입력-문제-해결)
7. [은행 지점 목록의 정렬 기능 문제](#7-은행-지점-목록의-정렬-기능-문제)

## 1. 금융상품 데이터 초기화 및 로딩 문제

### 문제 상황
- Django 서버에서 금융상품 API(`save-deposits`, `save-savings`)를 직접 호출해야만 데이터가 로드되는 현상 발생
- 프론트엔드에서 상품 목록 페이지 접속 시 데이터가 표시되지 않음
- 새로고침 시 데이터가 사라지는 현상 발생

### 원인 분석
1. 프론트엔드의 `onMounted` 훅에서 데이터 초기화 로직이 누락
2. 상품 데이터 저장 API와 조회 API의 호출 순서가 보장되지 않음
3. 백엔드에서 데이터 중복 저장 방지 로직 미흡

### 해결 방안
1. `productStore.ts`에 데이터 초기화 로직 추가
```typescript
async initializeProductsData() {
  try {
    this.loading = true;
    this.error = null;
    
    // 예금과 적금 상품 데이터 저장 요청을 동시에 실행
    await Promise.all([
      axios.get('/api/products/save-deposits/'),
      axios.get('/api/products/save-savings/')
    ]);

    // 저장된 상품 데이터 불러오기
    await Promise.all([
      this.fetchDepositProducts(),
      this.fetchSavingProducts()
    ]);
  } catch (error) {
    console.error('상품 데이터 초기화 실패:', error);
    this.error = '상품 데이터를 가져오는데 실패했습니다.';
  } finally {
    this.loading = false;
  }
}
```

2. `ProductsView.vue`의 `onMounted` 훅에서 초기화 함수 호출
```typescript
onMounted(async () => {
  try {
    await productStore.initializeProductsData();
    await loadProducts();
  } catch (error) {
    console.error('상품 데이터 초기화 및 로드 실패:', error);
  }
});
```

3. 백엔드에서 데이터 중복 저장 방지를 위한 `get_or_create` 사용
```python
bank, _ = Bank.objects.get_or_create(
    fin_co_no=bank_data['fin_co_no'],
    defaults=bank_data
)

product, created = DepositProduct.objects.get_or_create(
    fin_prdt_cd=fin_prdt_cd,
    defaults=product_data
)
```

### 개선 결과
1. 페이지 접속 시 자동으로 데이터 초기화 및 로드
2. 새로고침 시에도 데이터 유지
3. 중복 데이터 저장 방지
4. 에러 처리 및 로딩 상태 표시 개선

### 학습 포인트
1. Vue.js의 생명주기 훅(`onMounted`) 활용
2. Pinia store를 통한 상태 관리
3. Promise.all을 통한 비동기 작업 최적화
4. Django ORM의 `get_or_create` 메서드 활용
5. 프론트엔드와 백엔드 간의 데이터 흐름 설계

## 2. 금융상품 가입 기능 구현 시 인증 및 상태 관리 문제

### 문제 상황
- 금융상품 가입 시 403 Forbidden 에러 발생
- 가입 버튼 클릭 후 상태가 초기화되는 현상
- 금리별 옵션 선택 시 데이터가 유지되지 않는 문제

### 원인 분석
1. axios 요청에 인증 토큰이 포함되지 않음
2. 상품 가입 후 상태 업데이트 순서가 잘못됨
3. ProductDetailModal과 ProductsView 간의 데이터 동기화 미흡

### 해결 방안
1. axios 인스턴스 생성 및 인터셉터 설정
```typescript
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  }
);
```

2. ProductDetailModal 컴포넌트의 상태 관리 개선
```typescript
const handleSubscribe = (option: any) => {
  if (selectedOptionId.value === option.id) {
    emit('subscribe', {
      fin_prdt_cd: props.product.fin_prdt_cd,
      save_trm: option.save_trm,
      intr_rate: option.intr_rate
    });
  } else {
    selectedOptionId.value = option.id;
  }
};
```

3. ProductsView에서 상태 업데이트 순서 조정
```typescript
const handleSubscribe = async (data: SubscribeData) => {
  try {
    await productStore.subscribeToProduct(data);
    
    // 모달의 상품 정보 업데이트
    if (selectedProduct.value) {
      selectedProduct.value.is_subscribed = true;
    }

    // 상품 상세 정보 다시 불러오기
    productOptions.value = await productStore.fetchProductDetail(
      data.fin_prdt_cd,
      activeType.value
    );

    // 상품 목록 새로고침
    await productStore.fetchProducts();
  } catch (error) {
    console.error('상품 가입 실패:', error);
  }
};
```

### 개선 결과
1. 인증된 사용자만 상품 가입 가능
2. 가입 후 상태가 올바르게 유지됨
3. 금리별 옵션 선택이 정상적으로 작동
4. 상품 목록과 상세 정보가 동기화됨

### 학습 포인트
1. axios 인터셉터를 통한 인증 토큰 관리
2. Vue 컴포넌트 간 이벤트 통신
3. Pinia store를 활용한 상태 관리
4. 비동기 작업의 순서 보장
5. 프론트엔드 상태 동기화 전략


## 3. 금융상품 가입여부 확인 기능 구현

### 문제 상황
- 사용자별 가입한 상품 목록이 표시되지 않음
- 상품 목록에서 가입 여부가 실시간으로 반영되지 않음
- Product 인터페이스에 가입 여부 필드가 누락됨

### 원인 분석
1. Product 타입에 is_subscribed 필드 누락
2. 백엔드 API 응답에 가입 여부 정보가 포함되지 않음
3. 상품 목록 조회 시 사용자별 가입 정보를 함께 조회하지 않음

### 해결 방안
1. Product 인터페이스 수정
```typescript
export interface Product {
  // 기존 필드들...
  is_subscribed: boolean;       // 가입 여부 추가
}
```

2. 백엔드 API 수정
```python
class ProductSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.subscriptions.filter(user=user).exists()
        return False
```

3. 상품 목록 조회 로직 개선
```typescript
async fetchDepositProducts() {
  try {
    const response = await axiosInstance.get('/api/products/deposits/');
    const products = response.data.results;
    
    // 가입 여부 정보가 포함된 상품 데이터 처리
    this.depositProducts = await this.processProductOptions(products);
  } catch (error) {
    console.error('예금 상품 조회 실패:', error);
  }
}
```

### 개선 결과
1. 상품 목록에서 가입 여부가 시각적으로 표시됨
2. 가입/해지 시 실시간으로 상태가 업데이트됨
3. 사용자별 가입 상품 필터링 가능
4. 상품 상세 모달에서도 가입 상태 확인 가능

### 학습 포인트
1. TypeScript 인터페이스 확장
2. Django Serializer 커스터마이징
3. 백엔드-프론트엔드 데이터 구조 설계
4. 사용자별 데이터 필터링 구현
5. RESTful API 응답 구조 최적화


## 4. 금융상품 가입 시 외래키 제약조건 오류

### 문제 상황
- 상품 가입 시 `FOREIGN KEY constraint failed` 500 에러 발생
- 게시글 작성은 정상적으로 작동하지만 상품 가입에서만 실패
- 인증 토큰이 포함되어 있음에도 데이터베이스 저장 실패

### 원인 분석
1. `UserFinancialProduct` 모델의 외래키 설정 문제
2. 상품 가입 API에서 `product_type` 정보 누락
3. 게시글 작성과 상품 가입의 데이터 처리 방식 차이

### 해결 방안
1. **`UserFinancialProduct` 모델 수정**
   ```python
   class UserFinancialProduct(models.Model):
       user = models.ForeignKey(
           settings.AUTH_USER_MODEL,
           on_delete=models.CASCADE,
           related_name='user_financial_products'
       )
       deposit_product = models.ForeignKey(
           DepositProduct, 
           on_delete=models.CASCADE,
           null=True,
           blank=True
       )
       saving_product = models.ForeignKey(
           SavingProduct,
           on_delete=models.CASCADE,
           null=True,
           blank=True
       )
       product_type = models.CharField(
           max_length=10,
           choices=[('deposit', '예금'), ('saving', '적금')]
       )
       is_active = models.BooleanField(default=True)
       created_at = models.DateTimeField(auto_now_add=True)
   ```

2. **상품 가입 API 호출 수정**
   ```typescript
   const subscribeProduct = async (fin_prdt_cd: string) => {
       try {
           if (!authStore.isAuthenticated) {
               alert('로그인이 필요한 서비스입니다.');
               return;
           }

           const response = await api.post('/api/products/user-products/', {
               fin_prdt_cd: fin_prdt_cd,
               product_type: props.product.product_type || 'deposit'
           });

           alert('상품 가입이 완료되었습니다.');
           closeModal();
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
   ```

### 모델 수정으로 생기는 관계

1. **사용자와 상품의 관계**:
   - 한 사용자(`User`)는 여러 금융 상품에 가입할 수 있습니다. (1:N 관계)
   - `related_name='user_financial_products'`를 통해 사용자 모델에서 `user.user_financial_products.all()`로 가입한 모든 상품을 조회할 수 있습니다.

2. **상품 타입별 관계**:
   ```python
   deposit_product = models.ForeignKey(DepositProduct, ..., null=True, blank=True)
   saving_product = models.ForeignKey(SavingProduct, ..., null=True, blank=True)
   ```
   - 하나의 가입 기록은 예금 상품 또는 적금 상품 중 하나만 가질 수 있습니다.
   - `null=True, blank=True`로 설정되어 있어 각각의 상품 타입에 대해 선택적으로 연결됩니다.

3. **상품 타입 구분**:
   ```python
   product_type = models.CharField(
       choices=[('deposit', '예금'), ('saving', '적금')]
   )
   ```
   - 실제로 어떤 타입의 상품인지 명시적으로 저장됩니다.
   - 조회 시 타입 필터링이 용이해집니다.

4. **중복 가입 방지**:
   ```python
   class Meta:
       unique_together = ('user', 'deposit_product', 'saving_product')
   ```
   - 동일한 사용자가 같은 상품에 중복 가입하는 것을 방지합니다.

5. **사용 예시**:
   ```python
   # 예금 상품 가입 조회
   user.user_financial_products.filter(product_type='deposit')

   # 적금 상품 가입 조회
   user.user_financial_products.filter(product_type='saving')

   # 활성화된 상품만 조회
   user.user_financial_products.filter(is_active=True)
   ```

### 개선 결과
1. 외래키 제약조건 오류 해결
2. 상품 유형에 따른 정확한 데이터 저장
3. 상품 가입 시 적절한 에러 메시지 표시
4. 데이터베이스 무결성 보장

### 학습 포인트
1. Django 모델 관계 설정 (`Foreign Key`)
2. 데이터베이스 제약조건 설정의 중요성
3. API 요청 및 응답 데이터 구조 설계
4. 프론트엔드 에러 핸들링
5. 타입스크립트를 활용한 데이터 타입 안정성 확보


## 5. 금융상품 가입/해지 토글 기능 구현 문제

### 문제 상황
- 금융상품 가입 후 해지 기능이 동작하지 않음
- 가입된 상품의 상태가 UI에 제대로 반영되지 않음
- 다른 옵션 선택 시 이전 가입 상태가 유지되는 문제

### 원인 분석
1. 백엔드의 가입/해지 로직이 불완전

2. 프론트엔드의 상태 관리 미흡

3. 상품 옵션 간 상태 동기화 문제

### 해결 방안
1. 백엔드 가입/해지 토글 로직 개선
```python
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_financial_products(request):
    if request.method == 'POST':
        fin_prdt_cd = request.data.get('fin_prdt_cd')
        option_id = request.data.get('option_id')
        product_type = request.data.get('product_type', 'deposit')

        try:
            if product_type == 'deposit':
                product = DepositProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
                subscription, created = UserFinancialProduct.objects.get_or_create(
                    user=request.user,
                    deposit_product=product,
                    option_id=option_id,
                    defaults={
                        'product_type': product_type,
                        'is_active': True
                    }
                )
            
            if not created and subscription.is_active:
                # 이미 가입된 상품이면 해지 처리
                subscription.is_active = False
                subscription.save()
                return Response({'message': '상품 가입이 해지되었습니다.'}, status=200)
            
            # 새로 가입하거나 해지된 상품을 다시 가입
            subscription.is_active = True
            subscription.save()
            return Response({'message': '상품 가입이 완료되었습니다.'}, status=201)

        except DepositProduct.DoesNotExist:
            return Response({'error': '존재하지 않는 상품입니다.'}, status=404)
```

2. 프론트엔드 상태 관리 및 UI 업데이트 로직 개선
```typescript
const subscribeProduct = async (fin_prdt_cd: string, option_id: number) => {
  try {
    const response = await api.post('/api/products/user-products/', {
      fin_prdt_cd,
      option_id,
      product_type: props.product.product_type || 'deposit'
    });
    
    if (response.status === 200) {
      // 해지 완료
      subscribedOptionId.value = null;
      alert('상품 가입이 해지되었습니다.');
    } else {
      // 가입 완료
      subscribedOptionId.value = option_id;
      alert('상품 가입이 완료되었습니다.');
    }
  } catch (error) {
    const axiosError = error as AxiosError;
    if (axiosError.response?.status === 404) {
      alert('존재하지 않는 상품입니다.');
    } else if (axiosError.response?.status === 400) {
      alert(axiosError.response.data.error || '상품 가입에 실패했습니다.');
    } else {
      alert('상품 가입 중 오류가 발생했습니다.');
    }
  }
};
```

### 개선 결과
1. 가입/해지 토글 기능이 정상적으로 동작
2. UI에 가입 상태가 정확하게 반영됨
3. 다른 옵션 선택 시 이전 가입 상태가 올바르게 초기화됨
4. 사용자에게 적절한 피드백 메시지 제공

### 학습 포인트
1. Django REST framework의 Response status code 활용
2. Vue.js의 반응형 상태 관리
3. 프론트엔드와 백엔드 간의 상태 동기화
4. HTTP 상태 코드를 통한 결과 처리
5. 사용자 경험(UX)을 고려한 인터페이스 설계

## 6. 환전 계산기의 양방향 입력 문제 해결

### 문제 상황
환전 계산기에서 **도착 금액 입력 시 무한 루프**가 발생하여 사용자 경험에 심각한 문제를 야기.

```javascript
// 금액, 통화 변경 감지 후 자동 재계산
watch([amount], () => {
  if (amount.value !== null) {
    calculateConversion();
  }
});

watch([convertedAmount], () => {
  if (convertedAmount.value !== null) {
    calculateReverseConversion();
  }
});
```

### 원인 분석
1. **문제 시나리오**:
   - 도착 금액(`convertedAmount`)이 변경되면 `calculateReverseConversion()` 실행
   - `calculateReverseConversion()`이 출발 금액(`amount`)을 수정
   - 출발 금액 변경으로 `calculateConversion()` 실행
   - `calculateConversion()`이 도착 금액을 수정하여 무한 루프 발생

2. **문제의 핵심**:
   - `watch` 함수 간 상호작용으로 인해 데이터가 반복적으로 갱신됨

---

### 해결 방안

#### 1차 시도: **플래그를 사용한 상태 구분**
```javascript
const isCalculatingFromAmount = ref(true);

watch([amount], () => {
  isCalculatingFromAmount.value = true;
  calculateConversion();
});

watch([convertedAmount], () => {
  isCalculatingFromAmount.value = false;
  calculateReverseConversion();
});
```
- **결과**: 실패  
  플래그 값이 두 `watch` 간에서 정확히 동기화되지 않아 무한 루프 발생.

---

#### 2차 시도: **비동기 처리 플래그 사용**
```javascript
const isProcessing = ref(false);

watch([amount], () => {
  if (!isProcessing.value) {
    isProcessing.value = true;
    calculateConversion();
    isProcessing.value = false;
  }
});
```
- **결과**: 실패  
  플래그가 비동기 작업과 충돌하며 상태가 정확히 초기화되지 않음.

---

#### 최종 해결: **카운터 도입을 통한 제어**
```javascript
const updateCounter = ref(0);

watch([amount], () => {
  if (updateCounter.value < 1) {
    updateCounter.value++;
    calculateConversion();
  } else {
    updateCounter.value = 0;
  }
});

watch([convertedAmount], () => {
  if (updateCounter.value < 1) {
    updateCounter.value++;
    calculateReverseConversion();
  } else {
    updateCounter.value = 0;
  }
});
```
- **원리**:  
  - `updateCounter`를 사용해 각 `watch`가 실행되는 횟수를 제한
  - 한 번의 계산 이후 카운터를 초기화하여 무한 루프 방지

---

### 개선 결과
1. **문제 해결**:
   - 출발 금액과 도착 금액 변경 시 상호 간의 반복 갱신이 방지됨
   - 양방향 데이터 입력이 정상 작동

2. **장점**:
   - 간단한 로직으로 복잡한 문제 해결
   - 양방향 계산의 안정성과 데이터 일관성 유지
   - 코드 가독성과 유지보수성 향상

---

### 교훈 및 학습 포인트
1. **플래그보다 카운터 기반 접근이 효과적**:  
   플래그는 동기화 문제가 발생할 수 있지만, 카운터는 명확한 계산 횟수를 보장.

2. **무한 루프는 반복 제한으로 해결 가능**:  
   비즈니스 로직에 따라 적절한 제어 방식을 선택해야 함.

3. **양방향 데이터 바인딩의 제어 필요성**:  
   데이터 갱신이 연쇄적으로 발생하는 구조에서는 상호작용의 제어가 필수.

## 7. 은행 지점 목록의 정렬 기능 문제

### 문제 상황
- 은행 지점 목록에서 거리순/이름순 정렬이 제대로 작동하지 않음
- 정렬 버튼 클릭 시 목록이 새로고침되지만 정렬이 적용되지 않음
- 정렬된 결과가 마커 번호와 일치하지 않는 문제 발생

### 원인 분석
1. 정렬 로직이 실제로 적용되지 않음
2. 정렬된 데이터가 마커와 목록에 일관되게 반영되지 않음
3. 거리 계산 정보가 정렬 전에 저장되지 않음

### 해결 방안

#### 변경 전 코드
```typescript
// 단순히 검색만 다시 수행
const applyFilters = () => {
  const center = map.value.getCenter();
  searchNearbyBranches(center.getLat(), center.getLng());
};

const setSortBy = (type) => {
  sortBy.value = type;
  applyFilters();
};

const updateMarkersAndList = (places) => {
  clearMarkersAndList();
  places.forEach((place, index) => {
    addPlaceMarker(place, index);
    displayedList.value.push(place);
  });
};
```

#### 변경 후 코드
```typescript
const updateMarkersAndList = async (places) => {
  clearMarkersAndList();
  
  // 거리 정보와 로드뷰 정보를 포함한 확장된 장소 데이터 생성
  const placesWithInfo = await Promise.all(
    places.map(async (place) => ({
      ...place,
      hasRoadview: await checkRoadviewAvailable(place.y, place.x),
      distance: currentLocation.value ? 
        calculateDistance(
          currentLocation.value.lat,
          currentLocation.value.lng,
          place.y,
          place.x
        ) : 0
    }))
  );

  // 정렬 로직 적용
  let sortedPlaces = [...placesWithInfo];
  if (sortBy.value === 'distance' && currentLocation.value) {
    sortedPlaces.sort((a, b) => a.distance - b.distance);
  } else if (sortBy.value === 'name') {
    sortedPlaces.sort((a, b) => a.place_name.localeCompare(b.place_name));
  }

  // 정렬된 결과를 마커와 목록에 반영
  sortedPlaces.forEach((place, index) => {
    addPlaceMarker(place, index);
    displayedList.value.push(place);
  });
};
```

### 개선 결과
1. 거리순/이름순 정렬이 정상적으로 작동
2. 마커 번호와 목록 순서가 일치하게 됨
3. 정렬 시 실시간으로 목록과 마커가 업데이트됨
4. 사용자 경험이 개선됨

### 학습 포인트
1. Vue.js의 반응형 상태 관리와 데이터 정렬
2. 카카오맵 API의 마커 관리
3. 비동기 작업 처리와 Promise.all 활용
4. 사용자 인터페이스의 일관성 유지
5. 정렬 알고리즘의 효율적인 적용