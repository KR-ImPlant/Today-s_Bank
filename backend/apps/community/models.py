from django.db import models
from apps.accounts.models import User
from django.conf import settings

"""
커뮤니티 모델 정의
- Article: 게시글 모델
- Comment: 댓글 모델
"""

class Article(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)