from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile, ChatMessage, HealthMetric, AyurvedicRecommendation

admin.site.register(UserProfile)
admin.site.register(ChatMessage)
admin.site.register(HealthMetric)
admin.site.register(AyurvedicRecommendation)