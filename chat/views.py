from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from .manual_engine import process_message, extract_questions, contexts

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



