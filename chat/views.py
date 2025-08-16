from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .manual_engine import process_message, extract_questions, contexts
from django.contrib.auth.models import User
from .models import Report
import csv
import json
from .models import *






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
    reports = Report.objects.filter(user = request.user)
    context = {
        'reports': reports
    }
    return render(request, 'dashboard/dashboard.html', context)


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
            messages.success(request, "Profile updated successfully")
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


# Reports view
@login_required
def reports_view(request):
    # Get all reports for the current user
    user_reports = Report.objects.filter(user=request.user)
    
    # Format reports for table display
    formatted_reports = []
    for report in user_reports:
        formatted_reports.append({
            'id': report.id,
            'title': report.title,
            'created_at': report.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'symptoms_summary': report.symptoms[:100] + '...' if report.symptoms and len(report.symptoms) > 100 else report.symptoms or 'N/A',
            'diagnosis_summary': report.diagnosis[:100] + '...' if report.diagnosis and len(report.diagnosis) > 100 else report.diagnosis or 'N/A',
            'has_recommendations': bool(report.recommendations)
        })
    
    return render(request, 'dashboard/reports.html', {
        'reports': user_reports,
        'formatted_reports': formatted_reports
    })


# Generate PDF report
@login_required
def export_report_pdf(request, report_id):
    report = get_object_or_404(Report, id=report_id, user=request.user)
    
    try:
        # Try to import ReportLab for PDF generation
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Create the PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report.title.replace(" ", "_")}.pdf"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=10, textColor=colors.darkblue)
        body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=10, spaceAfter=10)
        
        # Add title
        story.append(Paragraph(report.title, title_style))
        story.append(Spacer(1, 12))
        
        # Add date
        date_text = f"<b>Date:</b> {report.created_at.strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(date_text, body_style))
        story.append(Spacer(1, 20))
        
        # Add symptoms section if available
        if report.symptoms:
            story.append(Paragraph("<b>Symptoms:</b>", heading_style))
            symptoms_text = report.symptoms.replace('\n', '<br/>')
            story.append(Paragraph(symptoms_text, body_style))
            story.append(Spacer(1, 20))
        
        # Add diagnosis section if available
        if report.diagnosis:
            story.append(Paragraph("<b>Diagnosis:</b>", heading_style))
            diagnosis_text = report.diagnosis.replace('\n', '<br/>')
            story.append(Paragraph(diagnosis_text, body_style))
            story.append(Spacer(1, 20))
        
        # Add recommendations section if available
        if report.recommendations:
            story.append(Paragraph("<b>Recommendations:</b>", heading_style))
            recommendations_text = report.recommendations.replace('\n', '<br/>')
            story.append(Paragraph(recommendations_text, body_style))
            story.append(Spacer(1, 20))
        
        # Add conversation section
        story.append(Paragraph("<b>Full Conversation:</b>", heading_style))
        
        # Format conversation for display in table
        conversation_lines = report.content.split('\n')
        conversation_data = []
        
        for line in conversation_lines:
            if line.strip():
                if line.startswith('User:'):
                    conversation_data.append([line, ''])
                elif line.startswith('System:'):
                    conversation_data.append(['', line])
                else:
                    conversation_data.append([line, ''])
        
        # Create table for conversation
        if conversation_data:
            col_widths = [3*inch, 4*inch]
            table = Table(conversation_data, colWidths=col_widths)
            
            # Style the table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            
            table.setStyle(style)
            story.append(table)
        
        # Build PDF
        doc.build(story)
        return response
        
    except ImportError:
        # If ReportLab is not installed, return an error
        return HttpResponse('PDF generation requires ReportLab to be installed.', status=500)
    except Exception as e:
        # Handle any other errors
        return HttpResponse(f'Error generating PDF: {str(e)}', status=500)


# Create report view
@login_required
def create_report_view(request):
    if request.method == 'POST':
        # Check if the request is from JavaScript (AJAX)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Parse JSON data from request body
                data = json.loads(request.body)
                
                # Extract information from the data
                conversation = data.get('conversation', '')
                symptoms = data.get('symptoms', '')
                diagnosis = data.get('diagnosis', '')
                recommendations = data.get('recommendations', '')
                
                # Create the report
                title = f"Medical Report - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                
                report = Report(
                    user=request.user,
                    title=title,
                    content=conversation,
                    symptoms=symptoms,
                    diagnosis=diagnosis,
                    recommendations=recommendations
                )
                report.save()
                
                # Return success response
                return JsonResponse({'success': True, 'report_id': report.id})
            except Exception as e:
                # Return error response
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
        # Handle regular POST request (from the web interface)
        # Get the last conversation from the session
        session_id = request.session.session_key
        if session_id and session_id in contexts:
            context = contexts[session_id]
            
            # Extract information from the conversation
            title = f"Medical Report - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Try to extract symptoms, diagnosis, and recommendations from the conversation
            symptoms = ""
            diagnosis = ""
            recommendations = ""
            
            # Get the last few exchanges
            recent_exchanges = context.get_recent_context(num_messages=10)
            
            # Build content from conversation history
            content = ""
            for user_msg, system_response in recent_exchanges:
                content += f"User: {user_msg}\nSystem: {system_response}\n\n"
                
                # Try to extract structured information
                if "symptom" in user_msg.lower() or "pain" in user_msg.lower() or "feel" in user_msg.lower():
                    symptoms += f"{user_msg}\n"
                
                if "diagnosis" in system_response.lower() or "you may have" in system_response.lower():
                    diagnosis += f"{system_response}\n"
                
                if "recommend" in system_response.lower() or "should" in system_response.lower() or "treatment" in system_response.lower():
                    recommendations += f"{system_response}\n"
            
            # Create the report
            report = Report(
                user=request.user,
                title=title,
                content=content,
                symptoms=symptoms,
                diagnosis=diagnosis,
                recommendations=recommendations
            )
            report.save()
            
            messages.success(request, "Report created successfully!")
            return redirect('reports')
        else:
            messages.error(request, "No conversation history found. Please start a chat first.")
            return redirect('chat')
    
    return render(request, 'dashboard/create_report.html')


# Export report to CSV
@login_required
def export_report_csv(request, report_id):
    report = get_object_or_404(Report, id=report_id, user=request.user)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.title.replace(" ", "_")}.csv"'
    
    writer = csv.writer(response)
    
    # Write the header
    writer.writerow(['Report Title', report.title])
    writer.writerow(['Created Date', report.created_at.strftime('%Y-%m-%d %H:%M')])
    writer.writerow([])  # Empty row
    
    # Write sections
    if report.symptoms:
        writer.writerow(['Symptoms'])
        writer.writerow([report.symptoms])
        writer.writerow([])  # Empty row
    
    if report.diagnosis:
        writer.writerow(['Diagnosis'])
        writer.writerow([report.diagnosis])
        writer.writerow([])  # Empty row
    
    if report.recommendations:
        writer.writerow(['Recommendations'])
        writer.writerow([report.recommendations])
        writer.writerow([])  # Empty row
    
    writer.writerow(['Full Conversation'])
    # Split content by lines and write each line
    for line in report.content.split('\n'):
        writer.writerow([line])
    
    return response


# Export all reports to CSV
@login_required
def export_all_reports_csv(request):
    reports = Report.objects.filter(user=request.user)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_reports.csv"'
    
    writer = csv.writer(response)
    
    # Write the header
    writer.writerow(['Title', 'Created Date', 'Symptoms', 'Diagnosis', 'Recommendations'])
    
    # Write report data
    for report in reports:
        # Clean up text for CSV (remove newlines and limit length)
        symptoms = report.symptoms.replace('\n', ' ')[:100] if report.symptoms else ''
        diagnosis = report.diagnosis.replace('\n', ' ')[:100] if report.diagnosis else ''
        recommendations = report.recommendations.replace('\n', ' ')[:100] if report.recommendations else ''
        
        writer.writerow([
            report.title,
            report.created_at.strftime('%Y-%m-%d %H:%M'),
            symptoms,
            diagnosis,
            recommendations
        ])
    
    return response


# View single report
@login_required
def view_report(request, report_id):
    report = get_object_or_404(Report, id=report_id, user=request.user)
    return render(request, 'dashboard/view_report.html', {'report': report})





@login_required
def profile_update(request):
    """Update user profile"""
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        user = request.user
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully")
        return redirect("profile_update")

    return render(request, "dashboard/profile.html", {"user": request.user})