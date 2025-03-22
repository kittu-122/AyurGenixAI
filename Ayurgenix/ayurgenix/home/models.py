from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Personal Information
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True, null=True
    )
    birth_date = models.DateField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Medical Information
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)
    family_medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)

    # Lifestyle Information
    PHYSICAL_ACTIVITY_CHOICES = [
        ('Sedentary', 'Less than 2 hours/week'),
        ('Lightly Active', '2-4 hours/week'),
        ('Active', '4-7 hours/week'),
        ('Very Active', 'More than 7 hours/week'),
    ]
    physical_activity_level = models.CharField(max_length=50, choices=PHYSICAL_ACTIVITY_CHOICES, blank=True, null=True)

    DIET_TYPE_CHOICES = [
        ('Vegetarian', 'Vegetarian'), ('Vegan', 'Vegan'),
        ('Non-Vegetarian', 'Non-Vegetarian'), ('Pescatarian', 'Pescatarian'),
    ]
    diet_type = models.CharField(max_length=50, choices=DIET_TYPE_CHOICES, blank=True, null=True)

    SLEEP_PATTERN_CHOICES = [
        ('Regular', '7-9 hours'), ('Irregular', 'Varying hours'),
        ('Less than 6 hours', 'Less than 6 hours'), ('More than 9 hours', 'More than 9 hours'),
    ]
    sleep_pattern = models.CharField(max_length=50, choices=SLEEP_PATTERN_CHOICES, blank=True, null=True)

    # Ayurvedic Information
    DOSHA_CHOICES = [
        ('Vata', 'Vata'), ('Pitta', 'Pitta'), ('Kapha', 'Kapha'),
        ('Vata-Pitta', 'Vata-Pitta'), ('Pitta-Kapha', 'Pitta-Kapha'),
        ('Vata-Kapha', 'Vata-Kapha'), ('Tridosha', 'Tridosha'),
    ]
    dosha_type = models.CharField(max_length=20, choices=DOSHA_CHOICES, blank=True, null=True)
    prakriti = models.CharField(max_length=100, blank=True, null=True)
    vikruti = models.CharField(max_length=100, blank=True, null=True)

    # Health Metrics
    height = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(300)])
    weight = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(500)])
    bmi = models.FloatField(blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    pulse_rate = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(250)])
    blood_pressure = models.CharField(max_length=15, blank=True, null=True)

    last_checkup_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Profile Tracking
    profile_completion_percentage = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} - {self.user.username}"

    def calculate_age(self):
        """Calculate user's age based on birth date."""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def calculate_bmi(self):
        """Calculate and update BMI if height and weight are provided."""
        if self.height and self.weight:
            return round(self.weight / ((self.height / 100) ** 2), 2)
        return None

    def is_profile_complete(self):
        """Check if the user's profile is complete."""
        required_fields = ['first_name', 'last_name', 'birth_date', 'gender', 'height', 'weight']
        for field in required_fields:
            if not getattr(self, field):
                return False  # Profile is incomplete
        return True  # Profile is complete

    def save(self, *args, **kwargs):
        """Auto-calculate BMI and update profile completion percentage before saving."""
        if self.height and self.weight:
            self.bmi = self.calculate_bmi()

        # Calculate profile completion percentage
        filled_fields = sum(1 for field in self._meta.fields if getattr(self, field.name) not in [None, ''])
        total_fields = len(self._meta.fields)
        self.profile_completion_percentage = int((filled_fields / total_fields) * 100)

        super(UserProfile, self).save(*args, **kwargs)



class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_ai = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # New fields for enhanced chat functionality
    message_type = models.CharField(max_length=50, choices=[
        ('general', 'General Question'),
        ('diagnosis', 'Diagnosis'),
        ('treatment', 'Treatment'),
        ('follow_up', 'Follow Up'),
        ('emergency', 'Emergency'),
    ], default='general')
    
    related_symptoms = models.TextField(blank=True, null=True)
    ai_confidence_score = models.FloatField(null=True, blank=True)
    needs_human_review = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_messages')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class HealthMetric(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    # Daily health metrics
    weight = models.FloatField(null=True, blank=True)
    blood_pressure = models.CharField(max_length=15, null=True, blank=True)
    pulse_rate = models.IntegerField(null=True, blank=True)
    sleep_hours = models.FloatField(null=True, blank=True)
    stress_level = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.user.username} - {self.date}"

class AyurvedicRecommendation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Recommendation details
    title = models.CharField(max_length=200)
    description = models.TextField()
    herbs = models.TextField(blank=True, null=True)
    dietary_suggestions = models.TextField(blank=True, null=True)
    lifestyle_changes = models.TextField(blank=True, null=True)
    yoga_practices = models.TextField(blank=True, null=True)
    
    # Tracking
    is_followed = models.BooleanField(default=False)
    effectiveness_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    user_feedback = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.user.user.username} - {self.title}"