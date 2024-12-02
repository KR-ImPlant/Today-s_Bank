from rest_framework import serializers
from .models import User
from apps.products.models import UserFinancialProduct

# 회원가입용 시리얼라이저
class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        error_messages={'required': '비밀번호는 필수 항목입니다.'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        error_messages={'required': '비밀번호 확인은 필수 항목입니다.'}
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': '이메일은 필수 항목입니다.',
            'invalid': '올바른 이메일 형식이 아닙니다.'
        }
    )
    nickname = serializers.CharField(
        required=True,
        error_messages={
            'required': '닉네임은 필수 항목입니다.',
            'unique': '이미 사용 중인 닉네임입니다.'
        }
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'nickname')
        extra_kwargs = {
            'username': {
                'required': True,
                'error_messages': {
                    'required': '사용자명은 필수 항목입니다.',
                    'unique': '이미 사용 중인 사용자명입니다.'
                }
            }
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 존재하는 이메일입니다.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 존재하는 사용자명입니다.")
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        return data
    
    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 존재하는 닉네임입니다.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')  # password_confirm 제거
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname']
        )
        return user

# 로그인용 시리얼라이저
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# 사용자 정보 조회용 시리얼라이저
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_image', 'nickname')
        read_only_fields = ('id', 'username', 'email')
# UserFinancialProduct 시리얼라이저
class UserFinancialProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFinancialProduct
        fields = '__all__'
        read_only_fields = ('user',)  # user 필드는 읽기 전용으로 설정


# User 프로필 수정용 시리얼라이저
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': '이메일은 필수 항목입니다.',
            'invalid': '올바른 이메일 형식이 아닙니다.'
        }
    )
    nickname = serializers.CharField(
        required=True,
        error_messages={
            'required': '닉네임은 필수 항목입니다.'
        }
    )
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('email', 'nickname', 'current_password', 'new_password', 'profile_image')

    def validate_nickname(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(nickname=value).exists():
            raise serializers.ValidationError("이미 존재하는 닉네임입니다.")
        return value

    def update(self, instance, validated_data):
        if 'current_password' in validated_data:
            if not instance.check_password(validated_data['current_password']):
                raise serializers.ValidationError({"current_password": "현재 비밀번호가 일치하지 않습니다."})
            if 'new_password' in validated_data:
                instance.set_password(validated_data['new_password'])

        if 'email' in validated_data:
            instance.email = validated_data['email']
        
        if 'nickname' in validated_data:
            instance.nickname = validated_data['nickname']
            
        if 'profile_image' in validated_data:
            instance.profile_image = validated_data['profile_image']

        instance.save()
        return instance
