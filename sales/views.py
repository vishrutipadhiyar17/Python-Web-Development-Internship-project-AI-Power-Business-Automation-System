import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Lead


def calculate_lead_score(source, interest_level, demo_requested, notes=""):
    score = 0

    source = (source or "").lower()
    interest_level = (interest_level or "").lower()
    notes = (notes or "").lower()

    if source in ["website", "referral", "linkedin"]:
        score += 25
    elif source in ["instagram", "facebook", "email"]:
        score += 15
    else:
        score += 10

    if interest_level in ["high", "very high"]:
        score += 35
    elif interest_level == "medium":
        score += 20
    else:
        score += 10

    if demo_requested:
        score += 25

    if "urgent" in notes or "immediately" in notes or "asap" in notes:
        score += 15

    if score >= 70:
        classification = "hot"
    elif score >= 40:
        classification = "warm"
    else:
        classification = "cold"

    return score, classification


@csrf_exempt
def lead_list_create_view(request):
    if request.method == "GET":
        leads = Lead.objects.all().order_by("-created_at")
        data = []

        for lead in leads:
            data.append({
                "id": lead.id,
                "lead_name": lead.lead_name,
                "company_name": lead.company_name,
                "email": lead.email,
                "phone": lead.phone,
                "product_name": lead.product_name,
                "source": lead.source,
                "interest_level": lead.interest_level,
                "demo_requested": lead.demo_requested,
                "stage": lead.stage,
                "notes": lead.notes,
                "score": lead.score,
                "classification": lead.classification,
                "sent_to_operations": lead.sent_to_operations,
                "created_at": lead.created_at,
            })

        return JsonResponse({"success": True, "leads": data})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            lead_name = data.get("lead_name")
            company_name = data.get("company_name")
            email = data.get("email")
            phone = data.get("phone")
            product_name = data.get("product_name")
            source = data.get("source", "")
            interest_level = data.get("interest_level", "")
            demo_requested = bool(data.get("demo_requested", False))
            stage = data.get("stage", "new")
            notes = data.get("notes", "")

            score, classification = calculate_lead_score(
                source, interest_level, demo_requested, notes
            )

            lead = Lead.objects.create(
                lead_name=lead_name,
                company_name=company_name,
                email=email,
                phone=phone,
                product_name=product_name,
                source=source,
                interest_level=interest_level,
                demo_requested=demo_requested,
                stage=stage,
                notes=notes,
                score=score,
                classification=classification,
                created_by=request.user if request.user.is_authenticated else None
            )

            return JsonResponse({
                "success": True,
                "message": "Lead added successfully",
                "lead": {
                    "id": lead.id,
                    "lead_name": lead.lead_name,
                    "score": lead.score,
                    "classification": lead.classification,
                    "stage": lead.stage
                }
            }, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


def lead_detail_view(request, lead_id):
    try:
        lead = Lead.objects.get(id=lead_id)

        return JsonResponse({
            "success": True,
            "lead": {
                "id": lead.id,
                "lead_name": lead.lead_name,
                "company_name": lead.company_name,
                "email": lead.email,
                "phone": lead.phone,
                "product_name": lead.product_name,
                "source": lead.source,
                "interest_level": lead.interest_level,
                "demo_requested": lead.demo_requested,
                "stage": lead.stage,
                "notes": lead.notes,
                "score": lead.score,
                "classification": lead.classification,
                "sent_to_operations": lead.sent_to_operations,
            }
        })
    except Lead.DoesNotExist:
        return JsonResponse({"success": False, "message": "Lead not found"}, status=404)


@csrf_exempt
def update_lead_view(request, lead_id):
    if request.method == "PUT":
        try:
            lead = Lead.objects.get(id=lead_id)
            data = json.loads(request.body)

            lead.lead_name = data.get("lead_name", lead.lead_name)
            lead.company_name = data.get("company_name", lead.company_name)
            lead.email = data.get("email", lead.email)
            lead.phone = data.get("phone", lead.phone)
            lead.product_name = data.get("product_name", lead.product_name)
            lead.source = data.get("source", lead.source)
            lead.interest_level = data.get("interest_level", lead.interest_level)
            lead.demo_requested = data.get("demo_requested", lead.demo_requested)
            lead.stage = data.get("stage", lead.stage)
            lead.notes = data.get("notes", lead.notes)

            score, classification = calculate_lead_score(
                lead.source, lead.interest_level, lead.demo_requested, lead.notes
            )
            lead.score = score
            lead.classification = classification
            lead.save()

            return JsonResponse({"success": True, "message": "Lead updated successfully"})
        except Lead.DoesNotExist:
            return JsonResponse({"success": False, "message": "Lead not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt
def send_to_operations_view(request, lead_id):
    if request.method == "POST":
        try:
            lead = Lead.objects.get(id=lead_id)

            if lead.stage != "purchase_confirmed":
                return JsonResponse({
                    "success": False,
                    "message": "Only Purchase Confirmed leads can be sent to Operations"
                }, status=400)

            lead.sent_to_operations = True
            lead.save()

            return JsonResponse({
                "success": True,
                "message": "Lead sent to Operations successfully"
            })
        except Lead.DoesNotExist:
            return JsonResponse({"success": False, "message": "Lead not found"}, status=404)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


def sales_dashboard_view(request):
    total_leads = Lead.objects.count()
    hot = Lead.objects.filter(classification="hot").count()
    warm = Lead.objects.filter(classification="warm").count()
    cold = Lead.objects.filter(classification="cold").count()
    purchase_confirmed = Lead.objects.filter(stage="purchase_confirmed").count()

    return JsonResponse({
        "success": True,
        "dashboard": {
            "total_leads": total_leads,
            "hot": hot,
            "warm": warm,
            "cold": cold,
            "purchase_confirmed": purchase_confirmed
        }
    })