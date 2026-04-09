from django.db import models
from django.contrib.auth.models import User
import os

class Resume(models.Model):
    """Model to store uploaded resume files and extracted data"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    original_filename = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='resumes/')
    file_type = models.CharField(max_length=10, choices=[('pdf', 'PDF'), ('docx', 'DOCX')])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Extracted content
    raw_text = models.TextField(blank=True)
    cleaned_text = models.TextField(blank=True)

    # Metadata
    word_count = models.IntegerField(default=0)
    character_count = models.IntegerField(default=0)
    page_count = models.IntegerField(default=0)

    # Analysis scores
    ats_score = models.IntegerField(default=0)
    readability_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.original_filename} - {self.uploaded_at}"

    def get_file_size_mb(self):
        """Return file size in MB"""
        try:
            return round(os.path.getsize(self.file_path.path) / (1024 * 1024), 2)
        except:
            return 0

class ResumeAnalysis(models.Model):
    """Model to store detailed analysis results"""
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='analysis')
    created_at = models.DateTimeField(auto_now_add=True)

    # Text statistics
    total_words = models.IntegerField(default=0)
    unique_words = models.IntegerField(default=0)
    avg_word_length = models.FloatField(default=0)

    # Content analysis
    has_contact_info = models.BooleanField(default=False)
    has_summary = models.BooleanField(default=False)
    has_experience = models.BooleanField(default=False)
    has_education = models.BooleanField(default=False)
    has_skills = models.BooleanField(default=False)

    # Keyword analysis
    top_keywords = models.JSONField(default=list)  # List of top keywords with frequencies
    skill_keywords = models.JSONField(default=list)  # Technical skills found
    soft_skills = models.JSONField(default=list)  # Soft skills identified

    # Readability metrics
    flesch_score = models.FloatField(default=0)
    grade_level = models.FloatField(default=0)

    # ATS compatibility
    ats_friendly_score = models.IntegerField(default=0)
    formatting_issues = models.JSONField(default=list)

    def __str__(self):
        return f"Analysis for {self.resume.original_filename}"

class JobDescription(models.Model):
    """Model to store job descriptions for matching"""
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Extracted keywords
    required_skills = models.JSONField(default=list)
    preferred_skills = models.JSONField(default=list)
    keywords = models.JSONField(default=list)

    def __str__(self):
        return f"{self.title} at {self.company}"

class ResumeJobMatch(models.Model):
    """Model to store resume-job matching results"""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_description = models.TextField(blank=True, null=True)  # Store job description text directly
    created_at = models.DateTimeField(auto_now_add=True)

    # Match scores
    match_score = models.FloatField(default=0)

    # Matched elements
    matched_keywords = models.JSONField(default=list)
    missing_keywords = models.JSONField(default=list)

    # Recommendations
    suggestions = models.JSONField(default=list)

    # User feedback
    helpful_suggestions = models.JSONField(default=list, blank=True)
    feedback_text = models.TextField(blank=True)

    def __str__(self):
        return f"Match: {self.resume.original_filename} - Score: {self.match_score}%"

class Feedback(models.Model):
    """Model to store user feedback on analysis results"""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Feedback content
    rating = models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')])
    comments = models.TextField(blank=True)
    
    # Analysis feedback
    analysis_helpful = models.BooleanField(default=True)
    suggestions_useful = models.BooleanField(default=True)
    would_recommend = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Feedback for {self.resume.original_filename} - {self.rating}/5"

