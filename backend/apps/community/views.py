from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleSerializer, CommentSerializer

@api_view(['GET', 'POST'])
def article_list(request):
    """
    게시글 목록 관련 API
    GET: 전체 게시글 목록 조회 (최신순)
    POST: 새 게시글 작성 (로그인 필요)
    """
    if request.method == 'GET':
        try:
            articles = Article.objects.all().order_by('-created_at')
            serializer = ArticleListSerializer(articles, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(
                {'error': '로그인이 필요합니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            print('요청 데이터:', request.data)
            serializer = ArticleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    user=request.user,
                    image=request.FILES.get('image')
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print('에러 발생:', str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
@api_view(['GET', 'PUT', 'DELETE'])
def article_detail(request, article_pk):
    """
    개별 게시글 관련 API
    GET: 게시글 상세 정보 조회
    PUT: 게시글 수정 (작성자만 가능)
    DELETE: 게시글 삭제 (작성자만 가능)
    """
    article = get_object_or_404(Article, pk=article_pk)
    
    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    
    # GET 요청이 아닌 경우에만 인증 확인
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # 작성자 본인만 수정/삭제 가능
    if request.user != article.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT':
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    elif request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, article_pk):
    """
    댓글 작성 API
    POST: 특정 게시글에 새 댓글 작성
    """
    article = get_object_or_404(Article, pk=article_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(
            article=article,
            user=request.user
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail(request, comment_pk):
    """
    개별 댓글 관련 API
    PUT: 댓글 수정 (작성자만 가능)
    DELETE: 댓글 삭제 (작성자만 가능)
    """
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    # 작성자 본인만 수정/삭제 가능
    if request.user != comment.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
