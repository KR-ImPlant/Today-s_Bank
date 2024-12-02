from django.contrib import admin
from .models import UserPreference, RecommendationResult

admin.site.register(UserPreference)
admin.site.register(RecommendationResult)