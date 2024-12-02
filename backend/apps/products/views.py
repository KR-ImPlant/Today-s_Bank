# products/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator
import requests, logging

from .models import (
    Bank, DepositProduct, DepositOption, 
    SavingProduct, SavingOption, UserFinancialProduct
)
from .serializers import (
    BankSerializer, DepositProductSerializer, DepositOptionSerializer,
    SavingProductSerializer, SavingOptionSerializer, UserFinancialProductSerializer,
    UserFinancialProductDetailSerializer
)

# 은행명 정규화 함수 추가
def normalize_bank_name(bank_name: str) -> str:
    """은행명에서 공백을 제거하고 정규화"""
    return bank_name.replace(' ', '')

# FIRST_TIER_BANKS 정의 수정
FIRST_TIER_BANKS = [
    '우리은행',
    '한국스탠다드차타드은행',
    '아이엠뱅크',
    '부산은행',  # 정규화된 이름으로 저장
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
    '주식회사케이뱅크',
    '수협은행',
    '주식회사카카오뱅크',
    '토스뱅크주식회사'
]

SAVING_BANKS = [
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
    '오케이저축은행'
]
############################################################################## 
# API 키 설정
##############################################################################   
API_KEY = settings.API_KEY

############################################################################## 
# 캐시 설정
############################################################################## 
PAGE_SIZE = 10
logger = logging.getLogger(__name__)

############################################################################## 
# 은행 정보 저장
############################################################################## 
@api_view(['GET'])
def saving_bank_list(request):
    try:
        url = f'http://finlife.fss.or.kr/finlifeapi/companySearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'
        response = requests.get(url).json()
        bank_list = response.get('result').get('baseList', [])

        for bank_data in bank_list:
            bank_serializer = BankSerializer(data=bank_data)
            if bank_serializer.is_valid():
                bank_serializer.save()
        return Response({'message': '은행 정보 저장이 완료되었습니다.'})
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)

############################################################################## 
# 은행 정보 조회
############################################################################## 
@api_view(['GET'])
def bank_list(request):
    banks = Bank.objects.all()
    serializer = BankSerializer(banks, many=True)
    return Response(serializer.data)

############################################################################## 
# 예금상품 옵션 저장
############################################################################## 
def save_product_options(product, option_list, fin_prdt_cd):
    """상품 옵션 저장 헬퍼 함"""
    try:
        for option in option_list:
            if option.get('fin_prdt_cd') == fin_prdt_cd:
                option_data = {
                    'product': product,
                    'fin_prdt_cd': fin_prdt_cd,
                    'intr_rate_type_nm': option.get('intr_rate_type_nm', ''),
                    'intr_rate': option.get('intr_rate', 0.0),
                    'intr_rate2': option.get('intr_rate2', 0.0),
                    'save_trm': option.get('save_trm', 0),
                }
                DepositOption.objects.create(**option_data)
    except Exception as e:
        logger.error(f'옵션 저장 중 오류 발생: {str(e)}')
        raise

############################################################################## 
# 예금 상품 저장
############################################################################## 
@api_view(['GET'])
def save_deposit_products(request):
    try:
        saved_count = 0
        skipped_count = 0
        
        for code in ['020000', '030300']:
            page = 1
            while True:
                url = 'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json'
                params = {
                    'auth': API_KEY,
                    'topFinGrpNo': code,
                    'pageNo': page
                }
                
                response = requests.get(url, params=params).json()
                base_list = response.get('result', {}).get('baseList', [])
                option_list = response.get('result', {}).get('optionList', [])
            
                for product_data in base_list:
                    fin_prdt_cd = product_data.get('fin_prdt_cd')
                    
                    # 이미 존재하는 상품인지 확인
                    if DepositProduct.objects.filter(fin_prdt_cd=fin_prdt_cd).exists():
                        skipped_count += 1
                        continue
                        
                    # 은행 정보 처리
                    bank_data = {
                        'fin_co_no': product_data.get('fin_co_no'),
                        'kor_co_nm': product_data.get('kor_co_nm'),
                        'homp_url': product_data.get('homp_url'),
                        'cal_tel': product_data.get('cal_tel')
                    }
                    
                    bank, _ = Bank.objects.get_or_create(
                        fin_co_no=bank_data['fin_co_no'],
                        defaults=bank_data
                    )
                    
                    product_data['bank'] = bank.fin_co_no
                    
                    serializer = DepositProductSerializer(data=product_data)
                    if serializer.is_valid():
                        product = serializer.save()
                        save_product_options(product, option_list, fin_prdt_cd)
                        saved_count += 1
                    else:
                        logger.error(f'상품 데이터 유효성 검사 실패: {serializer.errors}')
                
                page += 1
                if response.get('result', {}).get('max_page_no', '') < page:
                    break
                    
        return Response({
            'message': f'예금 상품 처리 완료 (새로 저장: {saved_count}개, 이미 존재: {skipped_count}개)'
        })
        
    except Exception as e:
        logger.error(f'예금 상품 저장 중 오류 발생: {str(e)}')
        return Response({'error': '데이터 저장 중 오류가 발생했습니다.'}, status=500)
    
############################################################################## 
# 예금 상품 조회
############################################################################## 
@api_view(['GET'])
def deposit_products_list(request):
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 8))
        first_tier_only = request.GET.get('first_tier_only') == 'true'
        saving_bank_only = request.GET.get('saving_bank_only') == 'true'
        banks = request.GET.get('banks', '').split(',') if request.GET.get('banks') else []
        
        logger.info(f'Request params: first_tier_only={first_tier_only}, banks={banks}')
        
        products = DepositProduct.objects.all()
        
        if first_tier_only:
            # 정규화된 은행명으로 필터링
            normalized_banks = [normalize_bank_name(bank) for bank in FIRST_TIER_BANKS]
            products = products.filter(kor_co_nm__in=FIRST_TIER_BANKS)
            
        elif saving_bank_only:
            products = products.filter(kor_co_nm__in=SAVING_BANKS)
            logger.info(f'Found {products.count()} products after saving only filtering')

        elif banks and banks[0]:
            products = products.filter(kor_co_nm__in=banks)
        
        # 전체 쿼리 결과 확인
        total_count = products.count()
        logger.info(f'Total products before pagination: {total_count}')
        
        # 은행명 목록 로깅
        distinct_banks = products.values_list('kor_co_nm', flat=True).distinct()
        logger.info(f'Available banks: {list(distinct_banks)}')
        
        products = products.order_by('-id')
        paginator = Paginator(products, page_size)
        
        try:
            current_page = paginator.page(page)
        except:
            return Response({
                'results': [],
                'total_pages': 0,
                'current_page': page,
                'total_count': 0
            })
            
        serializer = DepositProductSerializer(current_page.object_list, many=True)
        
        response_data = {
            'results': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_count': total_count
        }
        
        logger.info(f'Sending response with {len(serializer.data)} items')
        return Response(response_data)
        
    except Exception as e:
        logger.error(f'Error in deposit_products_list: {str(e)}')
        return Response({
            'error': str(e),
            'results': [],
            'total_pages': 0,
            'current_page': page,
            'total_count': 0
        })



# 예금 상품 상세 조회 뷰
@api_view(['GET'])
def deposit_product_detail(request, fin_prdt_cd):
    if not fin_prdt_cd:
        return Response({'error': '상품 코드가 필요합니다.'}, status=400)
    
    try:
        options = DepositOption.objects.select_related('product').filter(
            product__fin_prdt_cd=fin_prdt_cd
        )
        if not options:
            return Response({'error': '상품을 찾을 수 없습니다.'}, status=404)

        product = options.first().product  # 상품 정보 가져오기
        
        product_serializer = DepositProductSerializer(product)  # 상품 직렬화
        options_serializer = DepositOptionSerializer(options, many=True)  # 옵션 직렬화
        
        # 상품 + 옵션 데이터 함께 반환
        data = {
            'product': product_serializer.data,
            'options': options_serializer.data
        }
        return Response(data)
    
    except Exception as e:
        logger.error(f'상품 상세 조회 중 오류 발생: {str(e)}')
        return Response({'error': '상품 상세 조회 중 오류가 발생했습니다.'}, status=500)

############################################################################## 
# 예금 상품 최고 금리 조회
############################################################################## 
@api_view(['GET'])
def deposit_top_rate(request):
    try:
        # 데이터 존재 여부 확인
        if not DepositOption.objects.exists():
            return Response({'error': '저장된 예금 상품이 없습니다.'}, status=404)

        top_option = (DepositOption.objects
                     .select_related('product', 'product__bank')
                     .order_by('-intr_rate2')
                     .first())

        if not top_option:
            return Response({'error': '최고 금리 상품을 찾을 수 없습니다.'}, status=404)
        
        product = top_option.product
        product_serializer = DepositProductSerializer(product)
        options_serializer = DepositOptionSerializer(
            DepositOption.objects.filter(product=product), 
            many=True
        )
        
        data = {
            'product': product_serializer.data,
            'options': options_serializer.data
        }
    
        return Response(data)
    
    except Exception as e:
        logger.error(f'최고 금리 조회 중 오류 발생: {str(e)}')
        return Response({'error': '최고 금리 조회  오류가 발생했습니다.'}, status=500)

    
############################################################################## 
# 적금 상품 옵션 저장
############################################################################## 
def save_saving_options(product, option_list, fin_prdt_cd):
    """적금 상품 옵션 저장 헬퍼 함수"""
    try:
        for option in option_list:
            if option.get('fin_prdt_cd') == fin_prdt_cd:
                option_data = {
                    'product': product,
                    'fin_prdt_cd': fin_prdt_cd,
                    'intr_rate_type_nm': option.get('intr_rate_type_nm', ''),
                    'intr_rate': option.get('intr_rate', 0.0),
                    'intr_rate2': option.get('intr_rate2', 0.0),
                    'save_trm': option.get('save_trm', 0),
                }
                SavingOption.objects.create(**option_data)
    except Exception as e:
        logger.error(f'적금 옵션 저장 중 오류 발생: {str(e)}')

        raise


############################################################################## 
# 적금 상품 저장
############################################################################## 
@api_view(['GET'])
def save_saving_products(request):
    try:
        saved_count = 0
        skipped_count = 0
        
        for code in ['020000', '030300']:
            page = 1
            while True:
                url = 'http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json'
                params = {
                    'auth': API_KEY,
                    'topFinGrpNo': code,
                    'pageNo': page
                }
                
                response = requests.get(url, params=params).json()
                base_list = response.get('result', {}).get('baseList', [])
                option_list = response.get('result', {}).get('optionList', [])
                
                # 더 이상 데이터가 없으면 반복 중단
                if not base_list:
                    break
                    
                for product_data in base_list:
                    fin_prdt_cd = product_data.get('fin_prdt_cd')
                    
                    # 이미 존재하는 상품인지 확인
                    if SavingProduct.objects.filter(fin_prdt_cd=fin_prdt_cd).exists():
                        skipped_count += 1
                        continue
                        
                    # 은행 정보 처리
                    bank_data = {
                        'fin_co_no': product_data.get('fin_co_no'),
                        'kor_co_nm': product_data.get('kor_co_nm'),
                        'homp_url': product_data.get('homp_url'),
                        'cal_tel': product_data.get('cal_tel')
                    }
                    
                    bank, _ = Bank.objects.get_or_create(
                        fin_co_no=bank_data['fin_co_no'],
                        defaults=bank_data
                    )
                    
                    product_data['bank'] = bank.fin_co_no
                    
                    serializer = SavingProductSerializer(data=product_data)
                    if serializer.is_valid():
                        product = serializer.save()
                        save_saving_options(product, option_list, fin_prdt_cd)
                        saved_count += 1
                    else:
                        logger.error(f'상품 데이터 유효성 검사 실패: {serializer.errors}')
                
                page += 1
                if response.get('result', {}).get('max_page_no', '') < page:
                    break
                
        return Response({
            'message': f'적금 상품 처리 완료 (새로 저장: {saved_count}개, 이미 존재: {skipped_count}개)'
        })
        
    except Exception as e:
        logger.error(f'적금 상품 저장 중 오류 발생: {str(e)}')
        return Response({'error': '데이터 저장 중 오류가 발생했습니다.'}, status=500)
    
############################################################################## 
# 적금 상품 조회
############################################################################## 
@api_view(['GET'])
def saving_products_list(request):
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 8))
        first_tier_only = request.GET.get('first_tier_only') == 'true'
        saving_only = request.GET.get('saving_only') == 'true'
        banks = request.GET.get('banks', '').split(',') if request.GET.get('banks') else []
        
        products = SavingProduct.objects.all()
        
        if first_tier_only:

            products = products.filter(kor_co_nm__in=FIRST_TIER_BANKS)


        elif saving_only:
            products = products.filter(kor_co_nm__in=SAVING_BANKS)

            
        elif banks and banks[0]:
            products = products.filter(kor_co_nm__in=banks)
        
        total_count = products.count()
        products = products.order_by('-id')
        
        paginator = Paginator(products, page_size)
        
        try:
            current_page = paginator.page(page)
        except:
            return Response({
                'results': [],
                'total_pages': 0,
                'current_page': page,
                'total_count': 0
            })
            
        serializer = SavingProductSerializer(current_page.object_list, many=True)
        
        response_data = {
            'results': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_count': total_count
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'results': [],
            'total_pages': 0,
            'current_page': page,
            'total_count': 0
        })


############################################################################## 
# 적금 상품 상세 조회
############################################################################## 
@api_view(['GET'])
def saving_product_detail(request, fin_prdt_cd):
    if not fin_prdt_cd:
        return Response({'error': '상품 코드가 필요합니다.'}, status=400)
    
    try:
        options = SavingOption.objects.select_related('product').filter(
            product__fin_prdt_cd=fin_prdt_cd
        )

        if not options:
            return Response({'error': '상품을 찾을 수 없습니다.'}, status=404)
        
        product = options.first().product
        
        product_serializer = SavingProductSerializer(product)
        options_serializer = SavingOptionSerializer(options, many=True)
        
        data = {
            'product': product_serializer.data,
            'options': options_serializer.data
        }
        return Response(data)
    
    except Exception as e:
        logger.error(f'적금 상품 상세 조회 중 오류 발생: {str(e)}')
        return Response({'error': '상품 상세 조회 중 오류가 발생했습니다.'}, status=500)

############################################################################## 
# 적금 상품 최고 금리 조회
############################################################################## 
@api_view(['GET'])
def saving_top_rate(request):

    try:
        if not SavingOption.objects.exists():
            return Response({'error': '저장된 적금 상품이 없습니다.'}, status=404)

        top_option = (SavingOption.objects
                     .select_related('product', 'product__bank')
                     .order_by('-intr_rate2')
                     .first())

        if not top_option:
            return Response({'error': '최고 금리 상품을 찾을 수 습니다.'}, status=404)
        
        product = top_option.product
        product_serializer = SavingProductSerializer(product)
        options_serializer = SavingOptionSerializer(
            SavingOption.objects.filter(product=product), 
            many=True
        )
        
        data = {
            'product': product_serializer.data,
            'options': options_serializer.data
        }
 
        return Response(data)
    
    except Exception as e:
        logger.error(f'최고 금리 조회 중 오류 발생: {str(e)}')
        return Response({'error': '최고 금리 조회 중 오류가 발생했습니다.'}, status=500)



############################################################################## 
# 사용자 금융상품 관련 조회
############################################################################## 

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_financial_products(request):
    if request.method == 'GET':
        try:
            fin_prdt_cd = request.GET.get('fin_prdt_cd')
            option_id = request.GET.get('option_id')
            product_type = request.GET.get('product_type', 'deposit')
            check_any_option = request.GET.get('check_any_option') == 'true'
            
            query = {
                'user': request.user,
                'is_active': True
            }
            
            if product_type == 'deposit':
                query['deposit_product__fin_prdt_cd'] = fin_prdt_cd
            else:
                query['saving_product__fin_prdt_cd'] = fin_prdt_cd
                
            if not check_any_option and option_id:
                query['option_id'] = option_id
            
            subscription = UserFinancialProduct.objects.filter(**query).first()
            
            return Response({
                'is_subscribed': bool(subscription),
                'option_id': subscription.option_id if subscription else None
            })
            
        except Exception as e:
            logger.error(f'사용자 금융상품 조회 중 오류 발생: {str(e)}')
            return Response({
                'error': '상품 조회 중 오류가 발생했습니다.',
                'is_subscribed': False,
                'option_id': None
            }, status=500)

    elif request.method == 'POST':
        fin_prdt_cd = request.data.get('fin_prdt_cd')
        option_id = request.data.get('option_id')
        product_type = request.data.get('product_type', 'deposit')

        try:
            if product_type == 'deposit':
                product = DepositProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
                subscription = UserFinancialProduct.objects.filter(
                    user=request.user,
                    deposit_product=product,
                    option_id=option_id,
                ).first()
            else:
                product = SavingProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
                subscription = UserFinancialProduct.objects.filter(
                    user=request.user,
                    saving_product=product,
                    option_id=option_id,
                ).first()

            if subscription:
                # 이미 존재하는 구독이면 상태를 토글
                subscription.is_active = not subscription.is_active
                subscription.save()
                message = '상품 가입이 해지되었습니다.' if not subscription.is_active else '상품 가입이 완료되었습니다.'
                status_code = 200
            else:
                # 새로운 구독 생성
                subscription = UserFinancialProduct.objects.create(
                    user=request.user,
                    deposit_product=product if product_type == 'deposit' else None,
                    saving_product=product if product_type == 'saving' else None,
                    product_type=product_type,
                    option_id=option_id,
                    is_active=True
                )
                message = '상품 가입이 완료되었습니다.'
                status_code = 201

            return Response({'message': message}, status=status_code)

        except (DepositProduct.DoesNotExist, SavingProduct.DoesNotExist):
            return Response({'error': '존재하지 않는 상품입니다.'}, status=404)
        except Exception as e:
            logger.error(f'상품 가입/해지 중 오류 발생: {str(e)}')
            return Response({'error': '처리 중 오류가 발생했습니다.'}, status=500)


############################################################################## 
# 백엔드에서 일괄 조회 API 추가
############################################################################## 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_products_all(request):
    try:
        product_type = request.query_params.get('product_type', 'deposit')
        
        # product_type에 따라 적절한 드 선택
        if product_type == 'deposit':
            subscriptions = UserFinancialProduct.objects.filter(
                user=request.user,
                product_type=product_type,
                is_active=True,
                deposit_product__isnull=False  # deposit_product가 있는 경우만
            ).values(
                'deposit_product__fin_prdt_cd',  # 실제 fin_prdt_cd 필드 경로
                'option_id'
            )
            # 키 이름 변경
            subscription_data = {
                item['deposit_product__fin_prdt_cd']: {
                    'is_subscribed': True,
                    'option_id': item['option_id']
                }
                for item in subscriptions
            }
        else:
            subscriptions = UserFinancialProduct.objects.filter(
                user=request.user,
                product_type=product_type,
                is_active=True,
                saving_product__isnull=False  # saving_product가 있는 경우만
            ).values(
                'saving_product__fin_prdt_cd',  # 실제 fin_prdt_cd 필드 경로
                'option_id'
            )
            # 키 이름 변경
            subscription_data = {
                item['saving_product__fin_prdt_cd']: {
                    'is_subscribed': True,
                    'option_id': item['option_id']
                }
                for item in subscriptions
            }
        
        return Response(subscription_data)
        
    except Exception as e:
        logger.error(f'구독 상태 일괄 조회 중 오류 발생: {str(e)}')
        return Response({'error': '구독 상태 조회 중 오류가 발생했습니다.'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_subscribed_products(request):
    try:
        subscriptions = UserFinancialProduct.objects.filter(
            user=request.user,
            is_active=True
        ).select_related(
            'deposit_product',
            'saving_product'
        )
        
        # 각 상품의 옵션 정보를 올바르게 조회
        for subscription in subscriptions:
            if subscription.deposit_product:
                option = DepositOption.objects.filter(
                    product=subscription.deposit_product,
                    id=subscription.option_id
                ).values('intr_rate', 'intr_rate2').first()
                
                if option:
                    subscription.selected_option = {
                        'intr_rate': option['intr_rate'],
                        'intr_rate2': option['intr_rate2']
                    }
            elif subscription.saving_product:
                option = SavingOption.objects.filter(
                    product=subscription.saving_product,
                    id=subscription.option_id
                ).values('intr_rate', 'intr_rate2').first()
                
                if option:
                    subscription.selected_option = {
                        'intr_rate': option['intr_rate'],
                        'intr_rate2': option['intr_rate2']
                    }
        
        serializer = UserFinancialProductDetailSerializer(subscriptions, many=True)
        response_data = {
            'results': serializer.data,
            'total_count': subscriptions.count()
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f'[user_subscribed_products] 오류 발생: {str(e)}')
        return Response({'error': '조회 중 오류가 발생했습니다.'}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_product(request):
    try:
        fin_prdt_cd = request.data.get('fin_prdt_cd')
        product_type = request.data.get('product_type')
        option_id = request.data.get('option_id')

        subscription = UserFinancialProduct.objects.filter(
            user=request.user,
            option_id=option_id,
            is_active=True
        )

        if product_type == 'deposit':
            subscription = subscription.filter(deposit_product__fin_prdt_cd=fin_prdt_cd)
        else:
            subscription = subscription.filter(saving_product__fin_prdt_cd=fin_prdt_cd)

        if not subscription.exists():
            return Response({'error': '해당 상품의 가입 정보를 찾을 수 없습니다.'}, status=404)

        subscription = subscription.first()
        subscription.is_active = False
        subscription.save()

        return Response({'message': '상품이 성공적으로 해지되었습니다.'})

    except Exception as e:
        logger.error(f'상품 해지 중 오류 발생: {str(e)}')
        return Response({'error': '상품 해지 중 오류가 발생했습니다.'}, status=500)

def calculate_product_score(product, options, user_preference):
    """상품 점수 계산 함수"""
    scores = {
        'stability': 0,    # 안정성
        'profitability': 0,  # 수익성
        'accessibility': 0,  # 접근성
        'flexibility': 0     # 유연성
    }
    
    # 안정성 점수 (은행 종류, 예금자보호 등)
    scores['stability'] = 0.8 if product.kor_co_nm in FIRST_TIER_BANKS else 0.6
    
    # 수익성 점수 (금리 기반)
    max_rate = max(opt.intr_rate2 for opt in options)
    scores['profitability'] = min(max_rate / 5, 1.0)
    
    # 접근성 점수 (가입 방법, 제한사항 등)
    accessibility = 1.0
    if product.join_deny > 1:  # 가입 제한이 있는 경우
        accessibility *= 0.7
    scores['accessibility'] = accessibility
    
    # 유연성 점수 (중도해지 불이익, 옵션 다양성)
    scores['flexibility'] = len(options) / 10  # 옵션이 많을수록 유연성 높음
    
    # 최종 점수 계산
    weights = {
        'stability': 0.3,
        'profitability': 0.3,
        'accessibility': 0.2,
        'flexibility': 0.2
    }
    
    final_score = sum(scores[key] * weights[key] for key in weights)
    
    return final_score, scores

def generate_recommendation_explanation(recommendation, scores):
    if recommendation['is_best'] or recommendation['is_optimal']:
        explanation = f"• 안정성: {scores['stability']*100:.0f}점\n"
        explanation += f"• 수익성: {scores['profitability']*100:.0f}점\n"
        explanation += f"• 접근성: {scores['accessibility']*100:.0f}점\n"
        explanation += f"• 유연성: {scores['flexibility']*100:.0f}점"
        return explanation
    return None