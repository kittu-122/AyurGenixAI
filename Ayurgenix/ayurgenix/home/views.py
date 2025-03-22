import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt

# Import models consistently from the local app
from .models import UserProfile, ChatMessage, HealthMetric, AyurvedicRecommendation
from .forms import UserProfileForm, HealthMetricForm, ProfileEditForm
from .llm_utils import LLMManager, process_user_message

from home import views


# Landing Page
def landing_page(request):
    return render(request, 'home/landing_page.html')

# About Page
def about(request):
    return render(request, 'home/about.html')

# Contact Page
def contact_view(request):
    return render(request, 'home/contact.html')

# Authentication Views
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')  # Use the redirect function
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'auth/login.html')

@login_required
def after_login_redirect(request):
    """Redirect users based on profile completion."""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if not user_profile.is_profile_complete():
        return redirect('make_profile')  # Redirect new users to complete profile

    return redirect('dashboard')  # Redirect to dashboard if profile is complete

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not password1 or not password2:
            messages.error(request, "Both password fields are required.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Create an empty UserProfile
        UserProfile.objects.create(user=user)

        # Log in the user immediately after registration
        login(request, user)

        messages.success(request, "Registration successful. Please complete your profile.")
        return redirect('make_profile')  # Redirect new user to profile completion page

    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    return redirect('landing_page')

# Profile Management
@login_required
def make_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # If profile is already complete, redirect to the dashboard
    if user_profile.is_profile_complete():
        messages.info(request, "Your profile is already complete.")
        return redirect('dashboard')  # Redirect to dashboard

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Ensure any custom fields are correctly set
            if 'email' in form.cleaned_data:
                request.user.email = form.cleaned_data['email']
                request.user.save()
                
            profile.save()

            if profile.is_profile_complete():
                messages.success(request, "Profile completed successfully!")
                return redirect('dashboard')  # Redirect to dashboard after completion
            else:
                messages.warning(request, "Profile updated, but some fields are still missing.")
                return redirect('make_profile')
        else:
            # Form is invalid, show error message
            messages.error(request, "There were errors in your profile form. Please fix them and try again.")
    else:
        # Initialize form with email from User model
        initial_data = {'email': request.user.email, 'username': request.user.username}
        form = UserProfileForm(instance=user_profile, initial=initial_data)

    return render(request, 'profile/make_profile.html', {'form': form})

@login_required
def edit_profile(request):
    """Allow users to edit their profile after creation."""
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Handle email update
            if 'email' in form.cleaned_data:
                user.email = form.cleaned_data['email']
                user.save()
                
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "There were errors in your form. Please correct them and try again.")
    else:
        # Initialize form with email from User model
        initial_data = {'email': user.email, 'username': user.username}
        form = ProfileEditForm(instance=user_profile, initial=initial_data)
    
    return render(request, 'profile/edit_profile.html', {'form': form})

@login_required
def view_profile(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    return render(request, 'profile/view_profile.html', {'profile': profile})

@login_required
def chat_page(request):
    return render(request, "home/chat_page.html")


@login_required
def chat_view(request):
    """Render the chat page."""
    # Get previous messages if you want to display chat history
    previous_messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')[:20]
    return render(request, 'chat_page.html', {'previous_messages': previous_messages})


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from home.llm_utils import process_user_message  # ✅ Ensure this is correctly imported

@login_required
def chat_api(request):
    """Handles chatbot API interaction with user profile integration."""
    if request.method == "POST":
        user_message = request.POST.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        try:
            # Get the logged-in user's profile (if exists)
            user_profile = getattr(request.user, "userprofile", None)

            # Generate AI response using the LLM model
            ai_response = process_user_message(user_message, user_profile)

            return JsonResponse({
                "status": "success",
                "user_message": user_message,
                "ai_response": ai_response
            })

        except Exception as e:
            print(f"❌ Chatbot Error: {e}")
            return JsonResponse({"error": "AI model encountered an issue. Please try again."}, status=500)

    return JsonResponse({"error": "Invalid request. Only POST allowed."}, status=400)


@csrf_exempt
@login_required
def send_message(request):
    """Handle sending messages to the LLM and receiving responses."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Save user message to database
            ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                is_ai=False,
                message_type='general'
            )
            
            # Get user profile for personalized responses
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                user_profile = None
            
            # Initialize LLM manager and generate response
            llm_manager = LLMManager()
            ai_response = llm_manager.generate_response(user_message, user_profile)
            
            # Save AI response to database
            ChatMessage.objects.create(
                user=request.user,
                message=ai_response,
                is_ai=True,
                message_type='general'
            )
            
            return JsonResponse({'response': ai_response})
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def get_chat_history(request):
    chat_messages = ChatMessage.objects.filter(user=request.user).values()
    return JsonResponse({"chat_history": list(chat_messages)})

# Health Metrics API
@login_required
def health_metrics(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)
        
    if request.method == "POST":
        form = HealthMetricForm(request.POST)
        if form.is_valid():
            health_metric = form.save(commit=False)
            health_metric.user = user_profile
            health_metric.save()
            return JsonResponse({"status": "Health metric saved!"})
        else:
            return JsonResponse({"error": form.errors}, status=400)
            
    health_data = HealthMetric.objects.filter(user=user_profile).values()
    return JsonResponse({"health_metrics": list(health_data)})

# Ayurvedic Recommendations API
@login_required
def ayurvedic_recommendations(request):
    try:
        user_profile = request.user.userprofile
        recommendations = AyurvedicRecommendation.objects.filter(user=user_profile).values()
        return JsonResponse({"recommendations": list(recommendations)})
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)

# Dashboard View
@login_required
def dashboard(request):
    # Get the logged-in user's profile
    user = request.user
    
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # Create a profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=user)
        messages.info(request, "We've created a profile for you. Please complete it.")
        return redirect('make_profile')
    
    # Fetch health metrics & recommendations for the logged-in user
    health_data = HealthMetric.objects.filter(user=user_profile).order_by('-date')[:7]
    recommendations = AyurvedicRecommendation.objects.filter(user=user_profile).order_by('-date_created')[:3]
    
    # Calculate basic health statistics for the user
    avg_sleep = health_data.aggregate(Avg('sleep_hours'))['sleep_hours__avg'] or 0
    avg_stress = health_data.aggregate(Avg('stress_level'))['stress_level__avg'] or 0
    avg_pulse = health_data.aggregate(Avg('pulse_rate'))['pulse_rate__avg'] or 0
    
    # Handle form submission for adding new health metrics
    if request.method == 'POST':
        form = HealthMetricForm(request.POST)
        if form.is_valid():
            health_metric = form.save(commit=False)
            health_metric.user = user_profile
            health_metric.save()
            messages.success(request, 'Health data added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form.')
    else:
        form = HealthMetricForm()
        # Exclude user field from the form as it will be set automatically
        if 'user' in form.fields:
            form.fields.pop('user')
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'health_data': health_data,
        'recommendations': recommendations,
        'avg_sleep': round(avg_sleep, 1) if avg_sleep else 0,
        'avg_stress': round(avg_stress, 1) if avg_stress else 0,
        'avg_pulse': round(avg_pulse, 1) if avg_pulse else 0,
        'form': form,
    }
    
    return render(request, 'dashboard/dashboard.html', context)