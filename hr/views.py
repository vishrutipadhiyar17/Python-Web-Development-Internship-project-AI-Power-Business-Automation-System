import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Candidate, Interview


# ========== SHARED API ENDPOINTS ==========

@csrf_exempt
@require_http_methods(["GET", "POST"])
def candidates_api(request):
    """Get all candidates or create new candidate"""
    if request.method == "GET":
        try:
            candidates = Candidate.objects.all().values(
                'id', 'name', 'email', 'phone', 'position', 'experience_years',
                'skills', 'ai_score', 'status', 'created_at'
            ).order_by('-created_at')
            
            candidate_list = []
            for c in candidates:
                candidate_list.append({
                    'id': c['id'],
                    'name': c['name'],
                    'email': c['email'],
                    'phone': c['phone'],
                    'position': c['position'],
                    'experience': f"{c['experience_years']} years",
                    'skills': c['skills'],
                    'aiScore': int(c['ai_score']) if c['ai_score'] else 0,
                    'status': c['status'],
                    'appliedDate': c['created_at'].strftime('%Y-%m-%d') if c['created_at'] else '',
                })
            
            return JsonResponse({
                'success': True,
                'candidates': candidate_list,
                'count': len(candidate_list)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            candidate = Candidate.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone'),
                position=data.get('position'),
                skills=data.get('skills', ''),
                experience_years=int(data.get('experience_years', 0)),
                education=data.get('education', ''),
                resume_text=data.get('resume', ''),
                notes=data.get('notes', ''),
                ai_score=int(data.get('aiScore', 0)),
                status=data.get('status', 'pending_review'),
                ai_decision=data.get('aiDecision', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Candidate added successfully',
                'candidate': {
                    'id': candidate.id,
                    'name': candidate.name,
                    'email': candidate.email,
                    'position': candidate.position,
                    'status': candidate.status
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def candidate_detail_api(request, candidate_id):
    """Get, update or delete a specific candidate"""
    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Candidate not found'
        }, status=404)
    
    if request.method == "GET":
        return JsonResponse({
            'success': True,
            'candidate': {
                'id': candidate.id,
                'name': candidate.name,
                'email': candidate.email,
                'phone': candidate.phone,
                'position': candidate.position,
                'experience': f"{candidate.experience_years} years",
                'skills': candidate.skills,
                'aiScore': int(candidate.ai_score),
                'status': candidate.status,
            }
        })
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            candidate.name = data.get('name', candidate.name)
            candidate.email = data.get('email', candidate.email)
            candidate.phone = data.get('phone', candidate.phone)
            candidate.position = data.get('position', candidate.position)
            candidate.skills = data.get('skills', candidate.skills)
            candidate.status = data.get('status', candidate.status)
            candidate.ai_score = int(data.get('aiScore', candidate.ai_score))
            candidate.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Candidate updated successfully',
                'candidate': {
                    'id': candidate.id,
                    'name': candidate.name,
                    'status': candidate.status
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    elif request.method == "DELETE":
        candidate_name = candidate.name
        candidate.delete()
        return JsonResponse({
            'success': True,
            'message': f'Candidate {candidate_name} deleted successfully'
        })


def calculate_ai_score(skills, experience_years, position, education, resume_text=""):
    score = 0
    matches = []

    skill_keywords = ['python', 'django', 'javascript', 'html', 'css', 'mysql', 'react']
    text_to_check = f"{skills} {resume_text}".lower()

    for keyword in skill_keywords:
        if keyword in text_to_check:
            score += 10
            matches.append(keyword)

    score += min(experience_years * 5, 20)

    if education:
        score += 10

    if score >= 70:
        decision = "Shortlisted"
        status = "shortlisted"
    elif score <= 45:
        decision = "Rejected"
        status = "rejected"
    else:
        decision = "Pending Review"
        status = "pending_review"

    return score, ", ".join(matches), decision, status


@csrf_exempt
def candidate_list_create_view(request):
    if request.method == 'GET':
        candidates = Candidate.objects.all().order_by('-created_at')
        data = []

        for candidate in candidates:
            data.append({
                'id': candidate.id,
                'name': candidate.name,
                'email': candidate.email,
                'phone': candidate.phone,
                'position': candidate.position,
                'skills': candidate.skills,
                'experience_years': candidate.experience_years,
                'education': candidate.education,
                'notes': candidate.notes,
                'resume_text': candidate.resume_text,
                'ai_score': candidate.ai_score,
                'ai_matches': candidate.ai_matches,
                'ai_decision': candidate.ai_decision,
                'status': candidate.status,
                'created_at': candidate.created_at,
            })

        return JsonResponse({'success': True, 'candidates': data})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)

            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            position = data.get('position')
            skills = data.get('skills', '')
            experience_years = int(data.get('experience_years', 0))
            education = data.get('education', '')
            notes = data.get('notes', '')
            resume_text = data.get('resume_text', '')

            ai_score, ai_matches, ai_decision, status = calculate_ai_score(
                skills, experience_years, position, education, resume_text
            )

            candidate = Candidate.objects.create(
                name=name,
                email=email,
                phone=phone,
                position=position,
                skills=skills,
                experience_years=experience_years,
                education=education,
                notes=notes,
                resume_text=resume_text,
                ai_score=ai_score,
                ai_matches=ai_matches,
                ai_decision=ai_decision,
                status=status,
                created_by=request.user if request.user.is_authenticated else None
            )

            return JsonResponse({
                'success': True,
                'message': 'Candidate added successfully',
                'candidate': {
                    'id': candidate.id,
                    'name': candidate.name,
                    'status': candidate.status,
                    'ai_score': candidate.ai_score,
                    'ai_decision': candidate.ai_decision
                }
            }, status=201)

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


def candidate_detail_view(request, candidate_id):
    try:
        candidate = Candidate.objects.get(id=candidate_id)

        data = {
            'id': candidate.id,
            'name': candidate.name,
            'email': candidate.email,
            'phone': candidate.phone,
            'position': candidate.position,
            'skills': candidate.skills,
            'experience_years': candidate.experience_years,
            'education': candidate.education,
            'notes': candidate.notes,
            'resume_text': candidate.resume_text,
            'ai_score': candidate.ai_score,
            'ai_matches': candidate.ai_matches,
            'ai_decision': candidate.ai_decision,
            'status': candidate.status,
        }

        return JsonResponse({'success': True, 'candidate': data})

    except Candidate.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Candidate not found'}, status=404)


@csrf_exempt
def mark_selected_view(request, candidate_id):
    if request.method == 'POST':
        try:
            candidate = Candidate.objects.get(id=candidate_id)
            candidate.status = 'selected'
            candidate.save()

            return JsonResponse({'success': True, 'message': 'Candidate marked as selected'})
        except Candidate.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Candidate not found'}, status=404)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def mark_rejected_view(request, candidate_id):
    if request.method == 'POST':
        try:
            candidate = Candidate.objects.get(id=candidate_id)
            candidate.status = 'rejected'
            candidate.save()

            return JsonResponse({'success': True, 'message': 'Candidate marked as rejected'})
        except Candidate.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Candidate not found'}, status=404)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def schedule_interview_view(request, candidate_id):
    if request.method == 'POST':
        try:
            candidate = Candidate.objects.get(id=candidate_id)
            data = json.loads(request.body)

            interview = Interview.objects.create(
                candidate=candidate,
                interview_date=data.get('interview_date'),
                interview_time=data.get('interview_time'),
                interview_type=data.get('interview_type'),
                interviewer_name=data.get('interviewer_name'),
                remarks=data.get('remarks', ''),
                result='scheduled'
            )

            return JsonResponse({
                'success': True,
                'message': 'Interview scheduled successfully',
                'interview_id': interview.id
            }, status=201)

        except Candidate.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Candidate not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


def hr_dashboard_view(request):
    total_candidates = Candidate.objects.count()
    shortlisted = Candidate.objects.filter(status='shortlisted').count()
    rejected = Candidate.objects.filter(status='rejected').count()
    selected = Candidate.objects.filter(status='selected').count()
    interviews = Interview.objects.count()

    return JsonResponse({
        'success': True,
        'dashboard': {
            'total_candidates': total_candidates,
            'shortlisted': shortlisted,
            'rejected': rejected,
            'selected': selected,
            'interviews_scheduled': interviews
        }
    })