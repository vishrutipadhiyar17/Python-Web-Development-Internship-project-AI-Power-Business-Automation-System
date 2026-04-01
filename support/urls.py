from django.urls import path
from .views import (
    ticket_list_create_view,
    ticket_detail_view,
    update_ticket_view,
    reply_ticket_view,
    mark_in_progress_view,
    mark_resolved_view,
    support_dashboard_view,
    support_orders_view,
)

urlpatterns = [
    path("dashboard/", support_dashboard_view, name="support_dashboard"),
    path("tickets/", ticket_list_create_view, name="ticket_list_create"),
    path("tickets/<int:ticket_id>/", ticket_detail_view, name="ticket_detail"),
    path("tickets/<int:ticket_id>/update/", update_ticket_view, name="ticket_update"),
    path("tickets/<int:ticket_id>/reply/", reply_ticket_view, name="ticket_reply"),
    path("tickets/<int:ticket_id>/mark-in-progress/", mark_in_progress_view, name="ticket_mark_in_progress"),
    path("tickets/<int:ticket_id>/mark-resolved/", mark_resolved_view, name="ticket_mark_resolved"),
    path("orders/", support_orders_view, name="support_orders"),
]