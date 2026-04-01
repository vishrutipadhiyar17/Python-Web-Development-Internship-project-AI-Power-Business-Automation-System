from django.urls import path
from .views import (
    candidate_list_create_view,
    candidate_detail_view,
    mark_selected_view,
    mark_rejected_view,
    schedule_interview_view,
    hr_dashboard_view,
    candidates_api,
    candidate_detail_api,
)

urlpatterns = [
    path('dashboard/', hr_dashboard_view, name='hr_dashboard'),
    path('candidates/', candidate_list_create_view, name='candidate_list_create'),
    path('candidates/<int:candidate_id>/', candidate_detail_view, name='candidate_detail'),
    path('candidates/<int:candidate_id>/mark-selected/', mark_selected_view, name='mark_selected'),
    path('candidates/<int:candidate_id>/mark-rejected/', mark_rejected_view, name='mark_rejected'),
    path('candidates/<int:candidate_id>/schedule-interview/', schedule_interview_view, name='schedule_interview'),
    
    # === SHARED API ENDPOINTS ===
    path('api/candidates/', candidates_api, name='candidates_api'),
    path('api/candidates/<int:candidate_id>/', candidate_detail_api, name='candidate_detail_api'),
]