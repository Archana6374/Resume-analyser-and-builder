from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='builder_resumes', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True, default='')
    portfolio = models.URLField(blank=True, default='')
    summary = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    activities = models.TextField(blank=True, default='')
    certifications = models.TextField(blank=True, default='')
    projects = models.TextField(blank=True, default='')
    template = models.CharField(max_length=50, blank=True, default='classic')

    experience = models.JSONField(default=list)
    education = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
