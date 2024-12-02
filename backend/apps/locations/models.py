from django.db import models

class BankBranch(models.Model):
    brch_name = models.CharField(max_length=100)  # 지점명
    addr = models.CharField(max_length=200)       # 주소
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # 위도
    longitude = models.DecimalField(max_digits=9, decimal_places=6) # 경도
    brch_telno = models.CharField(max_length=20, null=True, blank=True)  # 전화번호
    
    def __str__(self):
        return self.brch_name

class FinMapToken(models.Model):
    access_token = models.CharField(max_length=1000)
    token_type = models.CharField(max_length=50)
    expires_in = models.IntegerField()
    scope = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)