from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('save_preference/', views.save_preference, name='save-preference'),
    path('', views.get_recommendations, name='recommendations-list'),
    path('questions/next/', views.generate_next_question, name='next-question'),
    path('questions/answers/', views.save_dynamic_answer, name='save-answer'),
    path('wishlist/', views.wishlist_products, name='wishlist-products'),
] 
