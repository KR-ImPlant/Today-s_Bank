from django.db import models
from django.conf import settings
"""
추천 시스템 서비스
- 사용자 선호도 분석
- 상품 추천 알고리즘
- 추천 결과 생성
"""
from django.db import models
from apps.accounts.models import User
from apps.products.models import DepositProduct, SavingProduct

class UserPreference(models.Model):
    """사용자 선호도 모델"""
    INVESTMENT_PURPOSE_CHOICES = [
        ('investment', '투자'),
        ('saving', '저축'),
        ('other', '기타'),
    ]
    
    INVESTMENT_PERIOD_CHOICES = [
        (6, '6개월'),
        (12, '12개월'),
        (24, '24개월'),
        (36, '36개월'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    investment_purpose = models.CharField(max_length=20, choices=INVESTMENT_PURPOSE_CHOICES)
    investment_period = models.IntegerField(choices=INVESTMENT_PERIOD_CHOICES)
    investment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    risk_tolerance = models.FloatField(default=0.0)  # 위험 성향 점수 (0.0 ~ 1.0)
    created_at = models.DateTimeField(auto_now_add=True)

class DynamicQuestion(models.Model):
    """동적 질문 모델"""
    QUESTION_TYPE_CHOICES = [
        ('risk', '위험 성향'),
        ('goal', '투자 목표'),
        ('experience', '투자 경험'),
        ('preference', '선호도'),
    ]
    
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    options = models.JSONField()  # [{"text": "옵션1", "value": "1"}, ...]
    created_at = models.DateTimeField(auto_now_add=True)
    preference = models.ForeignKey(
        UserPreference, 
        on_delete=models.CASCADE, 
        related_name='questions',
        null=True
    )
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.question_type}: {self.question_text[:30]}"
    
    class Meta:
        ordering = ['order', 'created_at']

class DynamicAnswer(models.Model):
    """사용자의 동적 질문 답변 모델"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(DynamicQuestion, on_delete=models.CASCADE)
    answer = models.JSONField()  # {"selected_option": "1", "additional_info": "..."}
    preference = models.ForeignKey(UserPreference, on_delete=models.CASCADE, related_name='answers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class RecommendationResult(models.Model):
    """추천 결과 모델"""
    user_preference = models.ForeignKey(UserPreference, on_delete=models.CASCADE)
    deposit_product = models.ForeignKey(DepositProduct, on_delete=models.CASCADE, null=True, blank=True)
    saving_product = models.ForeignKey(SavingProduct, on_delete=models.CASCADE, null=True, blank=True)
    score = models.FloatField()
    scores = models.JSONField()  # 상세 점수를 JSON으로 저장
    product_type = models.CharField(max_length=10)  # 'deposit' 또는 'saving'
    created_at = models.DateTimeField(auto_now_add=True)

class WishlistProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('user', 'deposit_product'),
            ('user', 'saving_product')
        ]