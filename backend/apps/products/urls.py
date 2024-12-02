# products/urls.py
from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    # 예금 관련 URL
    path('deposits/top-rate/', views.deposit_top_rate, name='deposit_top_rate'),
    path('deposits/', views.deposit_products_list, name='deposit_products_list'),
    path('deposits/<str:fin_prdt_cd>/', views.deposit_product_detail, name='deposit_product_detail'),


    # 적금 관련 URL
    path('savings/top-rate/', views.saving_top_rate, name='saving_top_rate'),
    path('savings/', views.saving_products_list, name='saving_products_list'),
    path('savings/<str:fin_prdt_cd>/', views.saving_product_detail, name='saving_product_detail'),
    
    # 데이터 저장 URL
    path('save-deposit-products/', views.save_deposit_products, name='save_deposit_products'),
    path('save-saving-products/', views.save_saving_products, name='save_saving_products'),
    path('save-bank-list/', views.saving_bank_list, name='saving_bank_list'),
    
    # 은행 관련 URL
    path('bank-list/', views.bank_list, name='bank_list'),

    # 사용자 금융상품 관련 URL
    path('user-products/', views.user_financial_products, name='user_financial_products'),
        # 일괄 조회 API 추가
    path('user-products/all/', views.user_products_all, name='user_products_all'),

    path('user-subscribed-products/', views.user_subscribed_products, name='user_subscribed_products'),
    path('user-products/unsubscribe/', views.unsubscribe_product, name='unsubscribe_product'),
]