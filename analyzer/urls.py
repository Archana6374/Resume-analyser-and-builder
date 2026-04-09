from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('parsed/', views.parsed_resume, name='parsed_resume'),
    path('preprocessed/', views.preprocessed_resume, name='preprocessed_resume'),
    path('analysis/', views.analysis, name='analysis'),
    path('score/', views.score, name='score'),
    path('jobmatch/', views.jobmatch, name='jobmatch'),
    path('feedback/', views.feedback, name='feedback'),
    path('builder/', views.builder, name='builder'),
    path('history/', views.resume_history, name='resume_history'),

    # API endpoints
    path('api/analyze/', views.api_analyze_resume, name='api_analyze'),
    path('api/match/', views.api_match_job, name='api_match'),
    path('api/get_suggestions/', views.api_get_suggestions, name='api_suggestions'),
]