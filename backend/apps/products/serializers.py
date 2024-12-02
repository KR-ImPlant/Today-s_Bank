from rest_framework import serializers
from .models import Bank, DepositProduct, DepositOption, SavingProduct, SavingOption, UserFinancialProduct



"""
은행 정보 시리얼라이저
- 은행의 기본 정보를 JSON 형식으로 변환
- 모든 필드 포함 (fin_co_no, kor_co_nm, homp_url, cal_tel)
"""
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'

"""
예금 상품 옵션 시리얼라이저
- 예금 상품의 금리 정보와 저축 기간 정보를 JSON으로 변환
- 모든 필드 포함 (product, fin_prdt_cd, intr_rate_type_nm, intr_rate, intr_rate2, save_trm)
"""
class DepositOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOption
        fields = '__all__'

"""
예금 상품 시리얼라이저
- 예금 상품의 기본 정보와 연관된 옵션 정보를 JSON으로 변환
- options 필드: 해당 상품의 모든 옵션 정보를 포함 (읽기 전용)
"""
class DepositProductSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = DepositProduct
        fields = '__all__'

"""
적금 상품 옵션 시리얼라이저
- 적금 상품의 금리 정보와 저축 기간 정보를 JSON으로 변환
- 모든 필드 포함 (product, fin_prdt_cd, intr_rate_type_nm, intr_rate, intr_rate2, save_trm)
"""
class SavingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOption
        fields = '__all__'

"""
적금 상품 시리얼라이저
- 적금 상품의 기본 정보와 연관된 옵션 정보를 JSON으로 변환
- options 필드: 해당 상품의 모든 옵션 정보를 포함 (읽기 전용)
"""
class SavingProductSerializer(serializers.ModelSerializer):
    options = SavingOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = SavingProduct
        fields = '__all__'

"""
사용자 금융 상품 시리얼라이저
- 사용자가 가입하거나 관심 있는 금융 상품 정보를 JSON으로 변환
- 필드:
  - id: 레코드 식별자
  - user: 사용자 정보 (읽기 전용)
  - deposit_product: 예금 상품 정보 (읽기 전용)
  - saving_product: 적금 상품 정보 (읽기 전용)
  - product_type: 상품 유형 (읽기 전용)
  - option_id: 옵션 ID (읽기 전용)
  - is_active: 활성화 상태
  - created_at: 생성 일시 (읽기 전용)
"""
class UserFinancialProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFinancialProduct
        fields = [
            'id', 
            'user', 
            'deposit_product',
            'saving_product',
            'product_type',
            'option_id', 
            'is_active', 
            'created_at'
        ]
        read_only_fields = ['user', 'created_at']

class UserFinancialProductDetailSerializer(serializers.ModelSerializer):
    deposit_product = DepositProductSerializer(read_only=True)
    saving_product = SavingProductSerializer(read_only=True)
    selected_option = serializers.SerializerMethodField()

    class Meta:
        model = UserFinancialProduct
        fields = [
            'id',
            'deposit_product',
            'saving_product',
            'product_type',
            'option_id',
            'is_active',
            'selected_option',
            'created_at'
        ]
    
    def get_selected_option(self, obj):
        if hasattr(obj, 'selected_option'):
            return obj.selected_option
        return None