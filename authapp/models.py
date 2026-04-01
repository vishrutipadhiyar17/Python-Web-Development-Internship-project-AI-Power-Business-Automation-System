from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('hr_staff', 'HR Staff'),
        ('operations_staff', 'Operations Staff'),
        ('support_staff', 'Support Staff'),
        ('sales_staff', 'Sales Staff'),
    ]

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='hr_staff')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username