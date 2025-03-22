# managers.py
from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

class UserProfileManager(models.Manager):
    def get_active_users(self):
        return self.filter(user__is_active=True)
    
    def get_incomplete_profiles(self):
        return self.filter(profile_completion_percentage__lt=100)
    
    def get_users_by_dosha(self, dosha_type):
        return self.filter(dosha_type=dosha_type)
    
    def get_users_needing_checkup(self, days=365):
        checkup_threshold = timezone.now().date() - timedelta(days=days)
        return self.filter(
            Q(last_checkup_date__lte=checkup_threshold) | 
            Q(last_checkup_date__isnull=True)
        )

class ChatMessageManager(models.Manager):
    def get_unreviewed_messages(self):
        return self.filter(needs_human_review=True, reviewed_by__isnull=True)
    
    def get_user_chat_history(self, user, days=None):
        queryset = self.filter(user=user)
        if days:
            date_threshold = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=date_threshold)
        return queryset.order_by('timestamp')
    
    def get_emergency_messages(self):
        return self.filter(message_type='emergency', needs_human_review=True)