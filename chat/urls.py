from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/', views.chat_post, name='chat_api'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.history_view, name='history'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/create/', views.create_report_view, name='create_report'),
    path('reports/view/<int:report_id>/', views.view_report, name='view_report'),
    path('reports/export/<int:report_id>/', views.export_report_csv, name='export_report_csv'),
    path('reports/export/pdf/<int:report_id>/', views.export_report_pdf, name='export_report_pdf'),
    path('reports/export-all/', views.export_all_reports_csv, name='export_all_reports_csv'),
    path("profile/update/", views.profile_update, name="profile_update"),

]
