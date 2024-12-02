from rest_framework import serializers
from .models import DynamicQuestion, DynamicAnswer, UserPreference, RecommendationResult
import json

class DynamicQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicQuestion
        fields = ['id', 'question_text', 'question_type', 'options', 'created_at', 'order']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # options가 문자열로 저장된 경우 JSON으로 파싱
        if isinstance(data['options'], str):
            data['options'] = json.loads(data['options'])
        return data

class DynamicAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicAnswer
        fields = ['id', 'user', 'question', 'answer', 'preference', 'created_at']
        read_only_fields = ['created_at']

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'investment_purpose', 'investment_period', 'investment_amount', 'risk_tolerance', 'created_at']
        read_only_fields = ['risk_tolerance', 'created_at']
        
    def validate_investment_purpose(self, value):
        valid_purposes = dict(UserPreference.INVESTMENT_PURPOSE_CHOICES)
        if value not in valid_purposes:
            raise serializers.ValidationError(f"유효하지 않은 투자 목적입니다. 가능한 값: {list(valid_purposes.keys())}")
        return value
        
    def validate_investment_period(self, value):
        valid_periods = [period[0] for period in UserPreference.INVESTMENT_PERIOD_CHOICES]
        if value not in valid_periods:
            raise serializers.ValidationError(f"유효하지 않은 투자 기간입니다. 가능한 값: {valid_periods}")
        return value

class RecommendationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationResult
        fields = ['id', 'user_preference', 'product_type', 'fin_prdt_cd', 
                 'score', 'explanation', 'created_at']
        read_only_fields = ['created_at', 'explanation']