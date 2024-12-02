from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BankBranchViewSet

router = DefaultRouter()
router.register(r'bank-branches', BankBranchViewSet)

urlpatterns = [
    path('', include(router.urls)),
]