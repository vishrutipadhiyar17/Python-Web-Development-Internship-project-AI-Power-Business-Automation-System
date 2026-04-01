from django.db import models
from django.conf import settings


class Candidate(models.Model):
    STATUS_CHOICES = [
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('pending_review', 'Pending Review'),
        ('selected', 'Selected'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    position = models.CharField(max_length=100)
    skills = models.TextField()
    experience_years = models.PositiveIntegerField(default=0)
    education = models.CharField(max_length=150)
    notes = models.TextField(blank=True, null=True)
    resume_text = models.TextField(blank=True, null=True)

    ai_score = models.FloatField(default=0)
    ai_matches = models.TextField(blank=True, null=True)
    ai_decision = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_review'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Interview(models.Model):
    RESULT_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interviews')
    interview_date = models.DateField()
    interview_time = models.TimeField()
    interview_type = models.CharField(max_length=50)
    interviewer_name = models.CharField(max_length=100)
    remarks = models.TextField(blank=True, null=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='scheduled')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidate.name} - {self.interview_date}"