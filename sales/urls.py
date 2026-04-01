from django.urls import path
from .views import (
    lead_list_create_view,
    lead_detail_view,
    update_lead_view,
    send_to_operations_view,
    sales_dashboard_view,
)

urlpatterns = [
    path("dashboard/", sales_dashboard_view, name="sales_dashboard"),
    path("leads/", lead_list_create_view, name="lead_list_create"),
    path("leads/<int:lead_id>/", lead_detail_view, name="lead_detail"),
    path("leads/<int:lead_id>/update/", update_lead_view, name="update_lead"),
    path("leads/<int:lead_id>/send-to-operations/", send_to_operations_view, name="send_to_operations"),
]