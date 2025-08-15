from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .manual_engine import process_message, extract_questions, contexts
from django.contrib.auth.models import User







def home(request):
    return render(request, 'chat/home.html')

# Chat view

class ChatView(View):
    def get(self, request):
        # For GET requests, provide possible questions
        # First get the general questions from the knowledge base
        general_questions = extract_questions()

        # Add specific ulcer-related questions
        ulcer_questions = [
            "What should I eat if I have an ulcer?",
            "What foods should I avoid with an ulcer?",
            "What are the symptoms of a stomach ulcer?",
            "How are ulcers treated?",
            "What causes ulcers?",
            "How can I prevent ulcers?",
            "What is the difference between gastric and duodenal ulcers?",
            "How long does it take for an ulcer to heal?"
        ]

        

        # Combine the questions, prioritizing ulcer-related ones
        questions = ulcer_questions + general_questions

        return render(request, 'chat/chat.html', {'questions': questions})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        user_message = request.POST.get('message', '')
        session_id = request.session.session_key or request.session.create()

        # Process the message using the manual engine
        response, is_structured_form = process_message(user_message, session_id, contexts)

        return JsonResponse({
            'response': response,
            'is_structured_form': is_structured_form
        })

# Create an instance of the view
chat_view = ChatView.as_view()

# Alternative function-based view for simpler debugging
@require_http_methods(["POST"])
def chat_post(request):
    user_message = request.POST.get('message', '')
    session_id = request.session.session_key or request.session.create()

    # Process the message using the manual engine
    response, is_structured_form = process_message(user_message, session_id, contexts)

    return JsonResponse({
        'response': response,
        'is_structured_form': is_structured_form
    })


# Dashboard view
@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


# Registration view
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')
        email = request.POST.get('email')
        confirm_password = request.POST.get('password2')
        
        # Basic validation
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'dashboard/registration/signup.html')
            
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'dashboard/registration/signup.html')
            
        # Create user (In a real app, you would use Django's UserCreationForm)
        # For simplicity, we're using authenticate which requires existing users
        # In a real app, you would create the user first

        user = User.objects.create_user(username=username, password=password, email = email)
        user.save()
        
        auth_user = authenticate(username=username, password=password)
        
        if auth_user is not None:
            # User exists, log them in
            login(request, auth_user)
            return redirect('dashboard')
        else:
            # User doesn't exist, create them
            # This is a simplified version - in production, use Django's built-in authentication
            messages.error(request, 'Registration failed. User may already exist.')
            return render(request, 'dashboard/registration/signup.html')
    
    return render(request, 'dashboard/registration/signup.html')


# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'registration/login.html')
    
    return render(request, 'dashboard/registration/login.html')


# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# History view
@login_required
def history_view(request):
    return render(request, 'chat/history.html')



