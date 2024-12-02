from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.db.models import Max
from .models import UserPreference, RecommendationResult, DynamicQuestion, DynamicAnswer, WishlistProduct
from apps.products.models import DepositProduct, SavingProduct, DepositOption, SavingOption
from rest_framework.permissions import IsAuthenticated
from .serializers import UserPreferenceSerializer, RecommendationResultSerializer, DynamicQuestionSerializer, DynamicAnswerSerializer
import logging
# import openai
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
import traceback
from datetime import datetime
from openai import OpenAI
import re
import json
from django.views.decorators.csrf import csrf_exempt
import random
from django.db import IntegrityError

# 로그를 기록하기 위한 로거 설정
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s - %(pathname)s:%(lineno)d')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=20.0
)

def calculate_product_score(product, options, user_preference):
    scores = {
        'stability': 0.8 if product.kor_co_nm in ['KB국민은행', '신한은행', '우리은행', '하나은행'] else 0.6,
        'profitability': min(max(opt.intr_rate2 for opt in options) / 5, 1.0),
        'accessibility': 1.0 if not product.join_deny else 0.7,
        'flexibility': min(len(options) / 10, 1.0)
    }
    
    weights = {
        'stability': 0.3,
        'profitability': 0.3,
        'accessibility': 0.2,
        'flexibility': 0.2
    }
    
    final_score = sum(scores[key] * weights[key] for key in weights)
    
    return final_score, scores

def extract_question_and_options(gpt_response):
    """GPT 응답에서 질문과 선택지를 분리"""
    lines = gpt_response.split('\n')
    question = lines[0].strip()
    options = []
    
    for line in lines[1:]:
        # 숫자. 텍스트 형식의 선택지 찾기
        match = re.match(r'(\d+)\.\s*(.+)', line.strip())
        if match:
            value, text = match.groups()
            options.append({
                "text": text.strip(),
                "value": value
            })
    
    return question, options

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save_preference(request):
    """사용자 선호도 저장 API"""
    try:
        logger.info(f"선호도 저장 요청 - User: {request.user.id}")
        logger.debug(f"Request Data: {request.data}")
        
        serializer = UserPreferenceSerializer(data={
            'user': request.user.id,
            'investment_purpose': request.data.get('investment_purpose'),
            'investment_period': request.data.get('investment_period'),
            'investment_amount': request.data.get('investment_amount'),
        })
        
        if serializer.is_valid():
            preference = serializer.save()
            logger.info(f"선호도 저장 성공 - ID: {preference.id}")
            return Response({
                'status': 'success',
                'id': preference.id
            })
            
        logger.error(f"Serializer 효성 검 실패: {serializer.errors}")
        return Response(serializer.errors, status=400)
        
    except Exception as e:
        logger.error(f"선호도 저장 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({
            'error': '선호도 저장 중 오류가 발생했습니다.',
            'detail': str(e)
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_next_question(request):
    """다음 질문 생성 API"""
    try:
        logger.info(f"다음 질문 생성 요청 - User: {request.user.id}")
        
        preference_id = request.data.get('preference_id')
        if not preference_id:
            logger.error("preference_id가 제공되지 않음")
            return Response({
                'status': 'error',
                'message': 'preference_id is required',
                'code': 'MISSING_PREFERENCE_ID'
            }, status=400)
            
        user_preference = get_object_or_404(UserPreference, id=preference_id, user=request.user)
        
        # 이미 생성된 질문이 있는지 확인
        existing_questions = DynamicQuestion.objects.filter(preference_id=preference_id)
        if existing_questions.exists():
            return Response({
                'status': 'success',
                'data': DynamicQuestionSerializer(existing_questions, many=True).data
            })

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 예금과 적금 상품 추천을 전문으로 하는 금융 상담사입니다. 
                        다음 규칙을 반드시 따라 5개의 질문을 생성해주세요:

                        1. 모든 질문은 예금과 적금 상품 선택에만 관련되어야 합니다
                        2. 각 질문은 독립적이고 중복되지 않아야 합니다
                        3. 복잡한 금융 용는 피하고 쉬운 단어를 사용하세요
                        4. 각 질문은 3-5개의 선택지를 가져야 합니다
                        
                        응답은 다음 JSON 형식을 따라주세요:
                        {
                            "questions": [
                                {
                                    "question": "질문 내용",
                                    "options": [
                                        {"text": "선택지1", "value": "1"},
                                        {"text": "선택지2", "value": "2"}
                                    ]
                                }
                            ]
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"""다음 사용자 정보를 참고하여 5개의 질문을 생성해주세요:
                        - 투자 목적: {user_preference.get_investment_purpose_display()}
                        - 투자 기간: {user_preference.investment_period}개월
                        - 투자 금액: {user_preference.investment_amount}원
                        
                        주의사항:
                        - 이미 수집된 위 정보와 비슷한 내용의 질문은 하지 마세요
                        - 예금과 적금 상품 추천에 필요한 새로운 정보를 얻기 위한 질문을 해주세요
                        - 아이, MZ , 나 특정 조건이 있어야 되는건 추천내용에서 제외해주세요 변별력이 없습니다.
                        """
                        
                    }
                ],
                response_format={ "type": "json_object" }
            )
            
            response_data = json.loads(response.choices[0].message.content)
            questions = response_data.get("questions", [])
            
            created_questions = []
            for question_data in questions:
                question = DynamicQuestion.objects.create(
                    question_text=question_data["question"],
                    question_type='risk',
                    options=question_data["options"],
                    preference_id=preference_id
                )
                created_questions.append(question)
            
            return Response({
                'status': 'success',
                'data': DynamicQuestionSerializer(created_questions, many=True).data
            })

        except Exception as gpt_error:
            logger.error(f"GPT 질문 생성 실패: {str(gpt_error)}")
            # 기본 질문들 생성
            default_questions = [
                {
                    "question_text": "귀하의 투자 위험 감수 성향 어떠신가요?",
                    "type": "risk",
                    "options": [
                        {"text": "매우 보수적", "value": "1"},
                        {"text": "보수적", "value": "2"},
                        {"text": "중립적", "value": "3"},
                        {"text": "공격적", "value": "4"},
                        {"text": "매우 공격적", "value": "5"}
                    ]
                },
                {
                    "question_text": "귀하의 투자 위험 감수 성향은 어떠신가요?",
                    "type": "risk",
                    "options": [
                        {"text": "매우 보수적", "value": "1"},
                        {"text": "보수적", "value": "2"},
                        {"text": "중립적", "value": "3"},
                        {"text": "공격적", "value": "4"},
                        {"text": "매우 공격적", "value": "5"}
                    ]
                },
                {
                    "question_text": "귀하의 투자 위험 감수 성향은 어떠신가요?",
                    "type": "risk",
                    "options": [
                        {"text": "매우 보수적", "value": "1"},
                        {"text": "보수적", "value": "2"},
                        {"text": "중립적", "value": "3"},
                        {"text": "공격적", "value": "4"},
                        {"text": "매우 공격적", "value": "5"}
                    ]
                },
                {
                    "question_text": "귀하의 투자 위험 감수 성향은 어떠신가요?",
                    "type": "risk",
                    "options": [
                        {"text": "매우 보수적", "value": "1"},
                        {"text": "보수적", "value": "2"},
                        {"text": "중립적", "value": "3"},
                        {"text": "공격적", "value": "4"},
                        {"text": "매우 공격적", "value": "5"}
                    ]
                },
                {
                    "question_text": "귀하의 투자 위험 감수 성향은 어떠신가요?",
                    "type": "risk",
                    "options": [
                        {"text": "매우 보수적", "value": "1"},
                        {"text": "보수적", "value": "2"},
                        {"text": "중립적", "value": "3"},
                        {"text": "공격적", "value": "4"},
                        {"text": "매우 공격적", "value": "5"}
                    ]
                },
                {
                    "question_text": "투자 험이 얼마 되시나요?",
                    "type": "experience",
                    "options": [
                        {"text": "경험 없음", "value": "1"},
                        {"text": "1년 미만", "value": "2"},
                        {"text": "1-3년", "value": "3"},
                        {"text": "3-5년", "value": "4"},
                        {"text": "5년 이상", "value": "5"}
                    ]
                }
            ]
            
            created_questions = []
            for q_data in default_questions:
                question = DynamicQuestion.objects.create(
                    question_text=q_data["question_text"],
                    question_type=q_data["type"],
                    options=q_data["options"],
                    preference_id=preference_id
                )
                created_questions.append(question)
            
            return Response({
                'status': 'success',
                'data': DynamicQuestionSerializer(created_questions, many=True).data
            })

    except Exception as e:
        logger.error(f"질문 생성 중 오류 발생: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': '질문 생성 중 오류가 발생했습니다.'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save_dynamic_answer(request):
    """사용자의 답변을 저장하는 API"""
    try:
        # 인증 디버깅을 위한 로그 추가
        logger.info("====== 인증 정보 ======")
        logger.info(f"인증된 사용자 여부: {request.user.is_authenticated}")
        logger.info(f"사용자 ID: {request.user.id if request.user.is_authenticated else 'Anonymous'}")
        logger.info(f"인증 헤더: {request.headers.get('Authorization', 'None')}")
        
        # 기존 로깅 유지
        logger.info("====== 답변 저장 요청 시작 ======")
        logger.info(f"요청 사용자: {request.user.id}")
        logger.info(f"요청 METHOD: {request.method}")
        logger.info(f"요청 PATH: {request.path}")
        logger.info(f"요청 Headers: {dict(request.headers)}")
        logger.info(f"요청 데이터: {request.data}")
        
        # 개 필드 검증 로깅
        question_id = request.data.get("question_id")
        preference_id = request.data.get("preference_id")
        answer_data = request.data.get("answer")
        
        logger.info(f"질문 ID: {question_id}")
        logger.info(f"선호도 ID: {preference_id}")
        logger.info(f"답변 데이터: {answer_data}")
        
        # 관련 객체 존재 여부 확인
        try:
            question = DynamicQuestion.objects.get(id=question_id)
            logger.info(f"질문 조회 성공: {question.question_text}")
        except DynamicQuestion.DoesNotExist:
            logger.error(f"질문 ID {question_id}가 존재하지 않음")
            return Response({"error": "질문을 찾을 수 없습니다."}, status=404)
            
        try:
            preference = UserPreference.objects.get(id=preference_id, user=request.user)
            logger.info(f"선호도 조회 성공: {preference.id}")
        except UserPreference.DoesNotExist:
            logger.error(f"선호도 ID {preference_id}가 존재하지 않음")
            return Response({"error": "선호도 정보를 찾을 수 없습니."}, status=404)
        
        # 시리얼라이저 ��이터 준비
        serializer_data = {
            "question": question_id,
            "answer": answer_data,
            "preference": preference_id,
            "user": request.user.id
        }
        
        logger.info(f"시리얼라이저 입력 데이터: {serializer_data}")
        
        serializer = DynamicAnswerSerializer(data=serializer_data)
        if serializer.is_valid():
            logger.info("시리얼라이저 유효성 검사 통과")
            logger.info(f"검증된 데이터: {serializer.validated_data}")
            answer = serializer.save()
            logger.info(f"답변 저장 완료: {answer.id}")
            
            # 모든 질문에 답변했는지 확인
            total_questions = DynamicQuestion.objects.filter(preference=preference).count()
            answered_questions = DynamicAnswer.objects.filter(preference=preference).count()
            
            if answered_questions >= total_questions:
                # 모든 질문에 답변 완료 시 위험 성향 업데이트
                update_risk_tolerance(preference)
            
            return Response({
                'status': 'success',
                'data': serializer.data,
                'is_completed': answered_questions >= total_questions
            })
        else:
            logger.error(f"시얼라이저 유효성 검사 실패: {serializer.errors}")
            return Response(serializer.errors, status=400)

    except Exception as e:
        logger.error("====== 예외 발생 ======")
        logger.error(f"예외 타입: {type(e)}")
        logger.error(f"예외 메시지: {str(e)}")
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    try:
        user_preference = UserPreference.objects.filter(
            user=request.user
        ).latest('created_at')
        
        recommendations = []
        
        # 예금 상품 평가
        for product in DepositProduct.objects.all():
            options = DepositOption.objects.filter(fin_prdt_cd=product.fin_prdt_cd)
            if options:
                score, detail_scores = calculate_product_score(product, options, user_preference)
                if score > 0.5:
                    recommendations.append({
                        'fin_prdt_cd': product.fin_prdt_cd,
                        'fin_prdt_nm': product.fin_prdt_nm,
                        'kor_co_nm': product.kor_co_nm,
                        'max_rate': max(opt.intr_rate2 for opt in options),
                        'score': score + random.uniform(-0.05, 0.05),  # 약간의 랜덤성 추가
                        'scores': detail_scores,
                        'product_type': 'deposit'
                    })
        
        # 적금 상품도 동일한 방식으로 리
        for product in SavingProduct.objects.all():
            options = SavingOption.objects.filter(fin_prdt_cd=product.fin_prdt_cd)
            if options:
                score, detail_scores = calculate_product_score(product, options, user_preference)
                if score > 0.5:
                    recommendations.append({
                        'fin_prdt_cd': product.fin_prdt_cd,
                        'fin_prdt_nm': product.fin_prdt_nm,
                        'kor_co_nm': product.kor_co_nm,
                        'max_rate': max(opt.intr_rate2 for opt in options),
                        'score': score,
                        'scores': detail_scores,
                        'product_type': 'saving'
                    })
        
        recommendations.sort(key=lambda x: (-x['score'], -x['max_rate']))  # 점수 내림차순, 같은 점수는 금리 내림차순

        # 상위 2개 상품은 점수 조정 없이 유지
        for i in range(2, len(recommendations)):
            recommendations[i]['score'] *= 0.95  # 상위 2개 외 상품은 표시 점수를 약간 낮춤

        top_recommendations = recommendations[:10]
        
        return Response({
            'status': 'success',
            'data': top_recommendations
        })
            
    except Exception as e:
        logger.error(f"추천 처리 중 오류 발생: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

def generate_recommendation_explanation(scores, user_preference):
    """AI를 사용하여 추천 이유 설명 생성"""
    try:
        content = {
            "scores": scores,
            "user_info": {
                "purpose": user_preference.get_investment_purpose_display(),
                "period": f"{user_preference.investment_period}개월",
                "amount": f"{user_preference.investment_amount:,}원",
                "risk_tolerance": user_preference.risk_tolerance
            }
        }
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """금융 상품 추천 이유를 설명하는 전문가입니다.
                    다음 점수와 사용자 정보를 바탕으로 이 상품이 추천된 이유를 설명해주세요.
                    - 안정성, 수익성, 접근성, 유연성 점수를 참고하세요
                    - 사용자의 투자 목적과 기간을 고려하세요
                    - 전문 용어는 피하고 이해하기 쉽게 설명하세요"""
                },
                {
                    "role": "user",
                    "content": f"다음 상품이 추천된 이유를 설명해주세요: {recommendation}"
                }
            ],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"설명 생성 중 오류 발생: {str(e)}", exc_info=True)
        return "추천 이유를 생성하는 중 오류가 발생했습니다."

def update_risk_tolerance(preference):
    """사용자의 위험 성향 점수를 업데이트하는 함수"""
    answers = DynamicAnswer.objects.filter(preference=preference)
    if not answers:
        return
    
    total_score = 0
    weights = {
        'risk': 0.4,
        'experience': 0.3,
        'preference': 0.3
    }
    
    type_scores = {'risk': [], 'experience': [], 'preference': []}
    
    for answer in answers:
        question_type = answer.question.question_type
        if question_type in weights:
            selected_value = int(answer.answer.get('selected_option', '3'))
            type_scores[question_type].append(selected_value)
    
    # 각 타입별 평균 계산
    for q_type, scores in type_scores.items():
        if scores:
            avg_score = sum(scores) / len(scores)
            total_score += (avg_score * weights[q_type])
    
    # 0~1 범위로 정규화
    preference.risk_tolerance = (total_score - 1) / 4
    preference.save()
    
    logger.info(f"위험 성향 점수 업데이트: {preference.risk_tolerance}")

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def wishlist_products(request):
    if request.method == 'GET':
        try:
            logger.info(f"[wishlist_products] GET 요청 시작 - 사용자: {request.user.username}")
            
            wishlist = WishlistProduct.objects.filter(user=request.user)
            products = []
            
            for item in wishlist:
                try:
                    if item.product_type == 'deposit' and item.deposit_product:
                        product = item.deposit_product
                        options = DepositOption.objects.filter(product=product)
                        base_rate = options.aggregate(Max('intr_rate'))['intr_rate__max'] or 0  # 기본금리 추가
                        max_rate = options.aggregate(Max('intr_rate2'))['intr_rate2__max'] or 0
                    elif item.product_type == 'saving' and item.saving_product:
                        product = item.saving_product
                        options = SavingOption.objects.filter(product=product)
                        base_rate = options.aggregate(Max('intr_rate'))['intr_rate__max'] or 0  # 기본금리 추가
                        max_rate = options.aggregate(Max('intr_rate2'))['intr_rate2__max'] or 0
                    else:
                        continue
                        
                    products.append({
                        'fin_prdt_cd': product.fin_prdt_cd,
                        'fin_prdt_nm': product.fin_prdt_nm,
                        'kor_co_nm': product.kor_co_nm,
                        'product_type': item.product_type,
                        'intr_rate': base_rate,  # 기본금리 필드 추가
                        'intr_rate2': max_rate
                    })
                except Exception as e:
                    logger.error(f"[wishlist_products] 개별 상품 처리 중 오류: {str(e)}")
                    continue
            
            logger.info(f"[wishlist_products] 조회 성공 - 상품 수: {len(products)}")
            return Response(products)
            
        except Exception as e:
            logger.error(f"[wishlist_products] GET 요청 처리 중 오류: {str(e)}")
            return Response(
                {'error': '찜 목록 조회 중 오류가 발생했습니다.'}, 
                status=500
            )
        
    elif request.method == 'POST':
        fin_prdt_cd = request.data.get('fin_prdt_cd')
        product_type = request.data.get('product_type', 'deposit')
        
        try:
            if product_type == 'deposit':
                product = DepositProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
                WishlistProduct.objects.create(
                    user=request.user,
                    deposit_product=product,
                    product_type=product_type
                )
            else:
                product = SavingProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
                WishlistProduct.objects.create(
                    user=request.user,
                    saving_product=product,
                    product_type=product_type
                )
            
            return Response({'message': '찜 목록에 추가되었습니다.'}, status=201)
            
        except IntegrityError:
            return Response({'message': '이미 찜한 상품입니다.'}, status=400)
        except (DepositProduct.DoesNotExist, SavingProduct.DoesNotExist):
            return Response({'message': '존재하지 않는 상품입니다.'}, status=404)
            
    elif request.method == 'DELETE':
        fin_prdt_cd = request.query_params.get('fin_prdt_cd')
        product_type = request.query_params.get('product_type', 'deposit')
        
        try:
            if product_type == 'deposit':
                WishlistProduct.objects.filter(
                    user=request.user,
                    deposit_product__fin_prdt_cd=fin_prdt_cd
                ).delete()
            else:
                WishlistProduct.objects.filter(
                    user=request.user,
                    saving_product__fin_prdt_cd=fin_prdt_cd
                ).delete()
                
            return Response({'message': '찜 목록에서 제거되었습니다.'})
            
        except Exception as e:
            return Response({'message': str(e)}, status=400)
