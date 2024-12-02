from rest_framework import serializers
from .models import Article, Comment

class ArticleListSerializer(serializers.ModelSerializer):
    """
    게시글 목록 조회를 위한 시리얼라이저
    - 목록에서 필요한 기본 정보만 포함 (id, 제목, 작성자, 작성일)
    """
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    
    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'username',
            'nickname',
            'created_at',
        )

class CommentSerializer(serializers.ModelSerializer):
    """
    댓글 정보를 위한 시리얼라이저
    - 댓글의 모든 정보 포함
    - article과 user 필드는 읽기 전용 (서버에서 자동 설정)
    """
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    
    class Meta:
        model = Comment
        fields = (
            'id',
            'content',
            'username',
            'nickname',
            'created_at',
            'article',
            'user',
        )
        read_only_fields = ('article', 'user',)

class ArticleSerializer(serializers.ModelSerializer):
    """
    게시글 상세 정보를 위한 시리얼라이저
    - 게시글의 모든 정보 포함
    - 연관된 댓글 목록과 댓글 수 포함
    - user 필드는 읽기 전용 (서버에서 자동 설정)
    """
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True, source='comments.count')

    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'content',
            'image',
            'created_at',
            'user',
            'username',
            'nickname',
            'comments',
            'comment_count',
        )
        read_only_fields = ('user', 'created_at')