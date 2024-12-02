from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

"""
커뮤니티 관련 URL 패턴 정의
- 게시글 목록 및 생성
- 게시글 상세/수정/삭제
- 댓글 생성
- 댓글 수정/삭제
"""

app_name = 'community'

urlpatterns = [
    # 게시글 관련 URL
    path('articles/', views.article_list, name='article_list'),
    path('articles/<int:article_pk>/', views.article_detail, name='article_detail'),
    
    # 댓글 관련 URL
    path('articles/<int:article_pk>/comments/', views.comment_create, name='comment_create'),
    path('comments/<int:comment_pk>/', views.comment_detail, name='comment_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
