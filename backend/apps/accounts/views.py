from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import UserSerializer, SignUpSerializer, LoginSerializer, UserProfileUpdateSerializer
from rest_framework.authtoken.models import Token

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    print("Received data:", request.data)
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error creating user:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    print("Validation errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': '잘못된 인증 정보입니다.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout(request):
    if request.user.auth_token:
        request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)

# 프로필 조회 및 수정 ( 둘다 로그인이 되어야 확인가능)
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
