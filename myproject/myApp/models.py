from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('lab', 'Lab'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    last_seen = models.DateTimeField(default=timezone.now)

    def is_online(self, minutes=5):
        return timezone.now() - self.last_seen < timedelta(minutes=minutes)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class ResearchProject(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[str(self.id)])


class ResearchPaper(models.Model):
    title = models.CharField(max_length=250)
    authors = models.CharField(max_length=250, blank=True)
    abstract = models.TextField(blank=True)
    keywords = models.CharField(max_length=250, blank=True)
    publication_year = models.PositiveIntegerField(default=2026)
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='papers')
    file = models.FileField(upload_to='papers/', blank=True, null=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('paper_detail', args=[str(self.id)])


class ResearchNote(models.Model):
    paper = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} -> {self.receiver}: {self.content[:40]}'
