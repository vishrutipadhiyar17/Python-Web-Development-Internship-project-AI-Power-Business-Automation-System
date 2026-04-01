import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket
from operations.models import Order


def calculate_priority(category, description):
    text = f"{category} {description}".lower()

    high_keywords = ["urgent", "failed", "error", "cancelled", "not working", "issue", "critical"]
    medium_keywords = ["billing", "payment", "refund", "delay"]

    if any(word in text for word in high_keywords):
        return "high"
    elif any(word in text for word in medium_keywords):
        return "medium"
    return "low"


def serialize_ticket(ticket):
    return {
        "id": ticket.id,
        "order": ticket.order.id if ticket.order else None,
        "title": ticket.title,
        "customer_name": ticket.customer_name,
        "customer_email": ticket.customer_email,
        "product_name": ticket.product_name,
        "order_date": ticket.order_date,
        "order_status": ticket.order_status,
        "category": ticket.category,
        "description": ticket.description,
        "priority": ticket.priority,
        "status": ticket.status,
        "response": ticket.response,
        "created_at": ticket.created_at,
    }


@csrf_exempt
def ticket_list_create_view(request):
    if request.method == "GET":
        tickets = Ticket.objects.all().order_by("-created_at")
        return JsonResponse({"success": True, "tickets": [serialize_ticket(t) for t in tickets]})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            order = None
            order_id = data.get("order_id")
            if order_id:
                order = Order.objects.filter(id=order_id).first()

            category = data.get("category", "")
            description = data.get("description", "")
            priority = calculate_priority(category, description)

            ticket = Ticket.objects.create(
                order=order,
                title=data.get("title"),
                customer_name=data.get("customer_name"),
                customer_email=data.get("customer_email"),
                product_name=data.get("product_name"),
                order_date=order.created_at if order else None,
                order_status=order.status if order else None,
                category=category,
                description=description,
                priority=priority,
                status="open",
                created_by=request.user if request.user.is_authenticated else None
            )

            return JsonResponse({
                "success": True,
                "message": "Ticket created successfully",
                "ticket": serialize_ticket(ticket)
            }, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


def ticket_detail_view(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        return JsonResponse({"success": True, "ticket": serialize_ticket(ticket)})
    except Ticket.DoesNotExist:
        return JsonResponse({"success": False, "message": "Ticket not found"}, status=404)


@csrf_exempt
def update_ticket_view(request, ticket_id):
    if request.method == "PUT":
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            data = json.loads(request.body)

            ticket.title = data.get("title", ticket.title)
            ticket.customer_name = data.get("customer_name", ticket.customer_name)
            ticket.customer_email = data.get("customer_email", ticket.customer_email)
            ticket.product_name = data.get("product_name", ticket.product_name)
            ticket.category = data.get("category", ticket.category)
            ticket.description = data.get("description", ticket.description)
            ticket.priority = calculate_priority(ticket.category, ticket.description)
            ticket.save()

            return JsonResponse({"success": True, "message": "Ticket updated successfully"})
        except Ticket.DoesNotExist:
            return JsonResponse({"success": False, "message": "Ticket not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt
def reply_ticket_view(request, ticket_id):
    if request.method == "POST":
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            data = json.loads(request.body)

            ticket.response = data.get("response", "")
            ticket.status = "in_progress"
            ticket.save()

            return JsonResponse({"success": True, "message": "Reply added successfully"})
        except Ticket.DoesNotExist:
            return JsonResponse({"success": False, "message": "Ticket not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt
def mark_in_progress_view(request, ticket_id):
    if request.method == "POST":
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.status = "in_progress"
            ticket.save()
            return JsonResponse({"success": True, "message": "Ticket marked as in progress"})
        except Ticket.DoesNotExist:
            return JsonResponse({"success": False, "message": "Ticket not found"}, status=404)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt
def mark_resolved_view(request, ticket_id):
    if request.method == "POST":
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.status = "resolved"
            ticket.save()
            return JsonResponse({"success": True, "message": "Ticket marked as resolved"})
        except Ticket.DoesNotExist:
            return JsonResponse({"success": False, "message": "Ticket not found"}, status=404)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


def support_dashboard_view(request):
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status="open").count()
    in_progress = Ticket.objects.filter(status="in_progress").count()
    resolved = Ticket.objects.filter(status="resolved").count()
    high_priority = Ticket.objects.filter(priority="high").count()

    return JsonResponse({
        "success": True,
        "dashboard": {
            "total_tickets": total_tickets,
            "open": open_tickets,
            "in_progress": in_progress,
            "resolved": resolved,
            "high_priority": high_priority,
        }
    })


def support_orders_view(request):
    orders = Order.objects.all().order_by("-created_at")
    data = []

    for order in orders:
        data.append({
            "id": order.id,
            "customer_name": order.customer_name,
            "product_name": order.product_name,
            "status": order.status,
            "email": order.email,
            "created_at": order.created_at,
        })

    return JsonResponse({"success": True, "orders": data})