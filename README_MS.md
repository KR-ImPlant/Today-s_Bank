# 프로젝트 개발 과정에서의 주요 이슈와 해결방안

## 1. 인증(Authentication) 관련 이슈

### 1.1. 토큰 기반 인증 구현
- **문제**: 로그인 후 페이지 새로고침 시 로그인 상태가 풀리는 현상
- **원인**: localStorage에 토큰만 저장하고 사용자 정보는 저장하지 않음
- **해결방안**: 
  ```typescript
  // authStore에서 토큰과 함께 사용자 정보도 저장
  const login = async (loginForm: LoginForm) => {
    const response = await api.post('/api/accounts/login/', loginForm)
    token.value = response.data.token
    username.value = response.data.user.username
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('username', response.data.user.username)
  }
  ```

### 1.2. 회원가입 후 자동 로그인
- **문제**: 회원가입 후 자동 로그인이 작동하지 않음
- **해결방안**: 
  - 백엔드에서 회원가입 시 토큰 생성 로직 추가
  - 프론트엔드에서 회원가입 응답 처리 시 로그인과 동일한 로직 적용

## 2. 게시판(Community) 관련 이슈

### 2.1. 게시글 접근 권한
- **문제**: 비회원도 볼 수 있어야 하는 게시글 목록이 인증 필요
- **원인**: 모든 API에 @permission_classes([IsAuthenticated]) 적용
- **해결방안**: 
  ```python
  @api_view(['GET', 'POST'])
  def article_list(request):
      if request.method == 'GET':
          # 조회는 인증 불필요
          articles = Article.objects.all()
          serializer = ArticleListSerializer(articles, many=True)
          return Response(serializer.data)
      
      # POST는 인증 필요
      if not request.user.is_authenticated:
          return Response({'error': '로그인이 필요합니다.'})
  ```

### 2.2. 게시글 작성자 확인
- **문제**: 게시글 수정/삭제 버튼이 작성자에게만 보여야 하는데 권한 체크 실패
- **원인**: 프론트엔드에서 사용자 정보 비교 로직 오류
- **해결방안**: 
  ```typescript
  const isArticleAuthor = computed(() => {
    return selectedArticle.value?.username === authStore.username
  })
  ```

## 3. 데이터베이스 관련 이슈

### 3.1. 모델 관계 설정
- **문제**: User와 Article, Comment 간의 관계 설정 오류
- **해결방안**: 
  - 마이그레이션 초기화 후 모델 재설계
  - ForeignKey 관계에 related_name 추가로 역참조 용이하게 수정

## 4. API 응답 처리

### 4.1. 에러 처리 표준화
- **문제**: API 에러 응답이 일관성 없이 처리됨
- **해결방안**: 
  - 백엔드에서 일관된 에러 응답 형식 정의
  - 프론트엔드에서 에러 처리 로직 통합

## 5. 현재 진행 중인 이슈

### 5.1. 이미지 업로드
- **상태**: 구현 중
- **계획**: 
  - 백엔드: 이미지 저장 경로 및 처리 로직 구현
  - 프론트엔드: 이미지 미리보기 및 업로드 UI 구현

### 5.2. 댓글 기능 개선
- **상태**: 기본 기능 구현 완료, 개선 필요
- **계획**:
  - 대댓글 기능 추가
  - 댓글 수정 시 실시간 업데이트

## 6. 추천 시스템(Recommendation) 관련 이슈

### 6.1. 추천 알고리즘 구현
- **문제**: 사용자 선호도와 금융 상품 특성을 매칭하는 복잡한 로직 필요
- **해결방안**: 
  ```python
  def calculate_recommendation(user_preference):
      # 투자 목적에 따른 가중치 부여
      purpose_weights = {
          'SAVINGS': {'deposit_rate': 0.7, 'risk': 0.3},
          'INVESTMENT': {'deposit_rate': 0.4, 'risk': 0.6}
      }
      
      # 투자 기간에 따른 상품 필터링
      period_filters = {
          'SHORT': {'min': 0, 'max': 12},
          'MEDIUM': {'min': 12, 'max': 36},
          'LONG': {'min': 36, 'max': float('inf')}
      }
      
      # 스코어링 시스템으로 최적 상품 추천
      weighted_score = (
          deposit_rate * purpose_weights[purpose]['deposit_rate'] +
          risk_score * purpose_weights[purpose]['risk']
      )
  ```

### 6.2. 추천 결과 저장 문제
- **문제**: 페이지 새로고침 시 추천 결과가 초기화되는 현상
- **원인**: 
  - 추천 결과를 프론트엔드 상태로만 관리
  - 백엔드 DB에 결과 저장 로직 미구현
- **현재 상태**: 미해결
- **향후 계획**:
  - RecommendationResult 모델에 결과 저장
  - 사용자별 추천 이력 관리 기능 추가

### 6.3. 직렬화(Serializer) 관련 이슈
- **문제**: UserPreference 직렬화 시 import 오류
- **원인**: views.py에서 serializer import 누락
- **해결방안**: 
  ```python
  # views.py
  from .serializers import UserPreferenceSerializer, RecommendationResultSerializer
  ```

### 6.4. 추천 시스템 성능 최적화
- **문제**: 대량의 금융 상품 데이터 처리 시 응답 속도 저하
- **해결방안**: 
  - 캐싱 시스템 도입
  - 데이터베이스 인덱싱 최적화
  ```python
  class FinancialProduct(models.Model):
      class Meta:
          indexes = [
              models.Index(fields=['fin_prdt_cd']),
              models.Index(fields=['product_type'])
          ]
  ```

### 6.5. 사용자 선호도 입력 검증
- **문제**: 프론트엔드에서 잘못된 선호도 값 전송 가능성
- **해결방안**: 
  ```python
  class UserPreferenceSerializer(serializers.ModelSerializer):
      def validate_investment_period(self, value):
          valid_periods = ['SHORT', 'MEDIUM', 'LONG']
          if value not in valid_periods:
              raise serializers.ValidationError("Invalid investment period")
          return value
  ```

### 6.6. CSRF 및 인증 관련 이슈

#### 6.6.1. CSRF 검증 실패
- **문제**: 답변 저장 API 호출 시 403 Forbidden (CSRF verification failed) 오류 발생
- **원인**: 
  - TokenAuthentication을 사용함에도 CSRF 검증이 수행됨
  - 프론트엔드와 백엔드의 URL 경로 불일치
  - CSRF 미들웨어가 인증 미들웨어보다 먼저 실행되는 문제
- **시도한 해결방안**:
  1. `@csrf_exempt` 데코레이터 추가
  ```python
  @csrf_exempt
  @api_view(['POST'])
  @authentication_classes([TokenAuthentication])
  @permission_classes([IsAuthenticated])
  def save_dynamic_answer(request):
      # 기존 코드...
  ```
  2. 미들웨어 순서 조정
  ```python
  MIDDLEWARE = [
      'corsheaders.middleware.CorsMiddleware',
      'django.middleware.security.SecurityMiddleware',
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',  # 인증 미들웨어를 앞으로 이동
      'django.middleware.common.CommonMiddleware',
      'django.middleware.csrf.CsrfViewMiddleware',
      # ...
  ]
  ```
  3. REST Framework 설정 보완
  ```python
  REST_FRAMEWORK = {
      'DEFAULT_AUTHENTICATION_CLASSES': [
          'rest_framework.authentication.TokenAuthentication',
      ],
      'DEFAULT_PERMISSION_CLASSES': [
          'rest_framework.permissions.IsAuthenticated',
      ],
  }
  ```

#### 6.6.2. URL 경로 불일치
- **문제**: 프론트엔드의 API 요청이 백엔드의 올바른 뷰에 매핑되지 않음
- **원인**: 
  - 백엔드: `/api/recommendations/questions/answers/`
  - 프론트엔드: `/api/recommendations/answers/save/`
- **해결방안**: 
  ```typescript
  // 프론트엔드 코드 수정
  const response = await axios.post(
    '/api/recommendations/questions/answers/',  // URL 경로 수정
    requestData,
    {
      headers: { 
        Authorization: `Token ${auth.token}`,
        'Content-Type': 'application/json'
      }
    }
  )
  ```

#### 6.6.3. 디버깅 및 로깅 개선
- **문제**: 인증 및 CSRF 관련 문제 추적이 어려움
- **해결방안**: 
  ```python
  @api_view(['POST'])
  def save_dynamic_answer(request):
      try:
          logger.info("====== 인증 정보 ======")
          logger.info(f"인증된 사용자 여부: {request.user.is_authenticated}")
          logger.info(f"사용자 ID: {request.user.id if request.user.is_authenticated else 'Anonymous'}")
          logger.info(f"인증 헤더: {request.headers.get('Authorization', 'None')}")
          logger.info(f"요청 메소드: {request.method}")
          logger.info(f"CSRF 토큰: {request.META.get('CSRF_COOKIE', 'None')}")
          # ... 기존 코드
  ```

#### 6.6.4. 최종 해결책
1. URL 경로 일치시키기
2. 인증 미들웨어 순서 조정
3. 명시적인 토큰 인증 설정
4. 상세한 디버깅 로그 추가

#### 6.6.5. 교훈
- API 엔드포인트 설계 시 일관된 URL 패턴 중요성
- 미들웨어 순서가 인증 및 보안에 미치는 영향
- 디버깅을 위한 로깅의 중요성

### 6.7. 추천 결과 중복 및 라우팅 문제

#### 6.7.1. 추천 결과 중복 표시
- **문제**: 동일한 상품이 여러 번 표시되는 현상 발생
- **원인**: 
  - `distinct()` 쿼리 사용 시 데이터베이스 호환성 문제
  - 추천 결과 저장 시 중복 체크 로직 부재
- **시도한 해결방안**:
  1. `distinct('fin_prdt_cd')` 사용
  ```python
  existing_results = RecommendationResult.objects.filter(
      user_preference__user=request.user
  ).order_by('-created_at').distinct('fin_prdt_cd')
  ```
  2. Python 로직으로 중복 제거
  ```python
  recommendations = []
  seen_products = set()  # 중복 체크용 set
  
  for result in existing_results:
      if result.fin_prdt_cd in seen_products:
          continue
      seen_products.add(result.fin_prdt_cd)
      # ... 결과 처리 로직
  ```

#### 6.7.2. 결과 페이지 라우팅 오류
- **문제**: 결과가 '/recommendation/4'에서 표시되고 '/recommendation/result'로 이동하지 않음
- **원인**: 
  - 라우팅 로직과 상태 관리 불일치
  - 결과 완료 상태 체크 로직 오류
- **해결방안**: 
  ```typescript
  // 결과 로드 후 올바른 경로로 이동
  const getRecommendations = async () => {
    try {
      const response = await axios.get('/api/recommendations/')
      if (response.data.status === 'success') {
        recommendations.value = response.data.data
        router.push('/recommendation/result')
      }
    } catch (error) {
      console.error('추천 결과 로드 중 오류:', error)
    }
  }
  ```

#### 6.7.3. 서버 오류 처리
- **문제**: 추천 결과 조회 시 500 Internal Server Error 발생
- **원인**: 
  - 데이터베���스 쿼리 최적화 문제
  - 존재하지 않는 상품 참조
- **해결방안**: 
  ```python
  try:
      product = None
      if result.product_type == 'deposit':
          product = DepositProduct.objects.get(fin_prdt_cd=result.fin_prdt_cd)
      else:
          product = SavingProduct.objects.get(fin_prdt_cd=result.fin_prdt_cd)
      
      recommendations.append({
          'product_type': result.product_type,
          'fin_prdt_cd': result.fin_prdt_cd,
          'fin_prdt_nm': product.fin_prdt_nm,
          'kor_co_nm': product.kor_co_nm,
          'score': result.score
      })
  except (DepositProduct.DoesNotExist, SavingProduct.DoesNotExist):
      logger.warning(f"상품을 찾을 수 없음: {result.fin_prdt_cd}")
      continue
  ```

#### 6.7.4. 교훈
- 데이터베이스 쿼리 최적화의 중요성
- 중복 데이터 처리를 위한 명확한 전략 수립 필요
- 프론트엔드 라우팅과 상태 관리의 일관성 유지

### 6.8. 금융상품 가입/해지 관련 이슈

#### 6.8.1. 가입 상품 목록 표시 문제
- **문제**: 상품 가입 후에도 미가입 금융상품 목록에 계속 표시되는 현상
- **원인**: 
  - `is_active` 상태 변경 후 목록 갱신 로직 부재
  - 프론트엔드와 백엔드 상태 불일치

- **시도한 해결방안**:
  1. ProductStore 수정 시도
  ```typescript
  // 상태 관리 스토어 수정 (실패)
  export const useProductStore = defineStore('product', {
    actions: {
      updateDisplayedProducts(type: string, products: Product[]) {
        if (type === 'deposit') {
          this.displayedDepositProducts = products
        } else {
          this.displayedSavingProducts = products
        }
      }
    }
  })
  ```

  2. 컴포넌트 내부 상태 관리 (성공)
  ```typescript
  // UserProfile.vue
  const handleSubscription = async (product: any) => {
    try {
      const response = await api.post('/api/products/user-products/', {
        fin_prdt_cd: product.fin_prdt_cd,
        option_id: product.selected_option_id,
        product_type: activeTab.value
      })

      if (response.status === 201 || response.status === 200) {
        // 가입된 상품 목록에서 해당 상품 제거
        const updatedProducts = paginatedProducts.value.filter(
          p => p.fin_prdt_cd !== product.fin_prdt_cd
        )
        paginatedProducts.value = updatedProducts
        await fetchSubscribedProducts()
      }
    } catch (error) {
      console.error('상품 가입 실패:', error)
    }
  }
  ```

#### 6.8.2. 상품 상세 정보 조회 오류
- **문제**: 상품 상세 정보 모달에서 "은행명 없음" 표시 및 404 에러
- **원인**: 
  - 상품 타입(deposit/saving) 구분 로직 오류
  - API 엔드포인트 경로 불일치

- **해결방안**: 
  ```typescript
  const showProductDetail = async (product: any) => {
    try {
      const productType = product.product_type || 
        (product.deposit_product ? 'deposit' : 'saving')
      
      const endpoint = productType === 'deposit' 
        ? `/api/products/deposits/${product.fin_prdt_cd}/`
        : `/api/products/savings/${product.fin_prdt_cd}/`

      const response = await api.get(endpoint)
      
      if (response.data) {
        selectedProduct.value = response.data.product
        productDetailOptions.value = response.data.options
        showDetailModal.value = true
      }
    } catch (error) {
      console.error('[showProductDetail] 오류:', error)
    }
  }
  ```

#### 6.8.3. 교훈
- 상태 관리의 중요성과 컴포넌트 간 데이터 동기화 전략
- API 응답에 따른 즉각적인 UI 업데이트 필요성
- 상품 타입에 따른 조건부 로직 처리의 중요성
