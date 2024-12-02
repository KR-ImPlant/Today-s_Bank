from django.urls import path
from . import views

urlpatterns = [
    path('exchange/rates/', views.exchange_rates, name='exchange-rates'),
    path('exchange/rates/history/', views.exchange_rates_history, name='exchange-rates-history'),
    path('exchange/rates/chart/', views.exchange_rate_chart, name='exchange-rate-chart'),
]