from django.db import models
from django.conf import settings


class Lead(models.Model):
    STAGE_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('demo_scheduled', 'Demo Scheduled'),
        ('negotiation', 'Negotiation'),
        ('purchase_confirmed', 'Purchase Confirmed'),
        ('closed_lost', 'Closed Lost'),
    ]

    CLASSIFICATION_CHOICES = [
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
    ]

    lead_name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    product_name = models.CharField(max_length=150)
    source = models.CharField(max_length=100, blank=True, null=True)
    interest_level = models.CharField(max_length=100, blank=True, null=True)
    demo_requested = models.BooleanField(default=False)
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='new')
    notes = models.TextField(blank=True, null=True)

    score = models.FloatField(default=0)
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='cold')
    sent_to_operations = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.lead_name