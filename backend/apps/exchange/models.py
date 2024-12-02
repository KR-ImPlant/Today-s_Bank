from django.db import models

"""
환율 관련 서비스
- 한국수출입은행 API 연동
- 환율 정보 조회
- 환율 계산 로직
"""

class Exchange(models.Model):
    # 필드 정의
    pass

class ExchangeRate(models.Model):
    currency_code = models.CharField(max_length=10)  # 통화 코드
    rate = models.DecimalField(max_digits=20, decimal_places=4)  # 환율
    date = models.DateField()  # 날짜
    
    class Meta:
        unique_together = ['currency_code', 'date']
        indexes = [
            models.Index(fields=['currency_code', 'date']),
        ]