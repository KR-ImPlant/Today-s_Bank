from django.db import models
from django.conf import settings
"""
금융 상품 모델 정의
- Bank: 은행 정보
- DepositProduct: 예금 상품
- SavingProduct: 적금 상품
- ProductOption: 상품 옵션(금리 등)
"""

"""
은행 정보를 저장하는 모델
- fin_co_no: 금융회사 코드 (PK)
- kor_co_nm: 금융회사명
- homp_url: 홈페이지 주소
- cal_tel: 대표 전화번호
"""
class Bank(models.Model):
    fin_co_no = models.CharField(max_length=20, primary_key=True)
    kor_co_nm = models.CharField(max_length=100, null=False)
    homp_url = models.URLField(null=True, blank=True)
    cal_tel = models.CharField(max_length=20, null=True, blank=True)

"""
예금 상품 정보를 저장하는 모델
- fin_prdt_cd: 금융상품 코드 (Unique)
- kor_co_nm: 금융회사명
- fin_prdt_nm: 금융상품명
- etc_note: 기타 유의사항
- join_deny: 가입제한 (1: 제한없음, 2: 서민전용, 3: 일부제한)
- join_member: 가입대상
- join_way: 가입방법
- spcl_cnd: 우대조건
- bank: 은행 정보 (FK)
"""
class DepositProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=100, unique=True)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=100)
    etc_note = models.TextField(null=True, blank=True)
    join_deny = models.IntegerField()
    join_member = models.TextField(null=True, blank=True)
    join_way = models.TextField(null=True, blank=True)
    spcl_cnd = models.TextField(null=True, blank=True)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)

"""
예금 상품의 금리 옵션을 저장하는 모델
- product: 연결된 예금 상품 (FK)
- fin_prdt_cd: 금융상품 코드
- intr_rate_type_nm: 금리유형
- intr_rate: 기본금리
- intr_rate2: 최고우대금리
- save_trm: 저축기간(개월)
"""
class DepositOption(models.Model):
    product = models.ForeignKey(DepositProduct, on_delete=models.CASCADE)
    fin_prdt_cd = models.CharField(max_length=100)
    intr_rate_type_nm = models.CharField(max_length=100)
    intr_rate = models.FloatField()
    intr_rate2 = models.FloatField()
    save_trm = models.IntegerField()

class SavingProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=100, unique=True)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=100)
    etc_note = models.TextField(null=True, blank=True)
    join_deny = models.IntegerField()
    join_member = models.TextField(null=True, blank=True)
    join_way = models.TextField(null=True, blank=True)
    spcl_cnd = models.TextField(null=True, blank=True)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)

class SavingOption(models.Model):
    product = models.ForeignKey(SavingProduct, on_delete=models.CASCADE)
    fin_prdt_cd = models.CharField(max_length=100)
    intr_rate_type_nm = models.CharField(max_length=100)
    intr_rate = models.FloatField()
    intr_rate2 = models.FloatField()
    save_trm = models.IntegerField()

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
        default='deposit',
        choices=[('deposit', '예금'), ('saving', '적금')]
    )
    option_id = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'deposit_product', 'saving_product', 'option_id')