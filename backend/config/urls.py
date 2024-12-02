"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

"""
프로젝트 전체 URL 설정
- admin 페이지
- 각 앱별 URL 패턴 포함
- 미디어 파일 서빙 설정
"""

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # 각 앱별 URL 패턴
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/community/', include('apps.community.urls')),
    path('api/', include('apps.exchange.urls')),
    path('api/locations/', include('apps.locations.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
]

# 미디어 파일 서빙 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
