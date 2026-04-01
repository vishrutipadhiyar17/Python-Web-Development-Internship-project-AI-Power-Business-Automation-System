from django.db import models
from django.conf import settings
from operations.models import Order


class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    product_name = models.CharField(max_length=150, blank=True, null=True)
    order_date = models.DateTimeField(null=True, blank=True)
    order_status = models.CharField(max_length=50, blank=True, null=True)

    category = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    response = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title