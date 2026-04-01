import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order
from sales.models import Lead


def serialize_order(order):
    return {
        "id": order.id,
        "source": order.source,
        "lead_reference": order.lead_reference,
        "customer_name": order.customer_name,
        "company_name": order.company_name,
        "email": order.email,
        "phone": order.phone,
        "product_name": order.product_name,
        "product_sku": order.product_sku,
        "quantity": order.quantity,
        "unit_price": float(order.unit_price),
        "total": float(order.total),
        "status": order.status,
        "delivery_status": order.delivery_status,
        "issue_status": order.issue_status,
        "created_at": order.created_at,
    }


def serialize_product(product):
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category": product.category,
        "price": float(product.price),
        "stock": product.stock,
        "low_threshold": product.low_threshold,
        "created_at": product.created_at,
    }


@csrf_exempt
def product_list_create_view(request):
    if request.method == "GET":
        products = Product.objects.all().order_by("-created_at")
        return JsonResponse({"success": True, "products": [serialize_product(p) for p in products]})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            product = Product.objects.create(
                name=data.get("name"),
                sku=data.get("sku"),
                category=data.get("category"),
                price=Decimal(str(data.get("price", 0))),
                stock=int(data.get("stock", 0)),
                low_threshold=int(data.get("low_threshold", 5)),
            )

            return JsonResponse({
                "success": True,
                "message": "Product added successfully",
                "product": serialize_product(product)
            }, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt
def product_update_view(request, sku):
    if request.method == "PUT":
        try:
            product = Product.objects.get(sku=sku)
            data = json.loads(request.body)

            product.name = data.get("name", product.name)
            product.category = data.get("category", product.category)
            product.price = Decimal(str(data.get("price", product.price)))
            product.stock = int(data.get("stock", product.stock))
            product.low_threshold = int(data.get("low_threshold", product.low_threshold))
            product.save()

            return JsonResponse({"success": True, "message": "Product updated successfully"})
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "Product not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt
def product_delete_view(request, sku):
    if request.method == "DELETE":
        try:
            product = Product.objects.get(sku=sku)
            product.delete()
            return JsonResponse({"success": True, "message": "Product deleted successfully"})
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "Product not found"}, status=404)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt
def restock_product_view(request, sku):
    if request.method == "POST":
        try:
            product = Product.objects.get(sku=sku)
            data = json.loads(request.body)
            add_stock = int(data.get("add_stock", 0))

            product.stock += add_stock
            product.save()

            return JsonResponse({
                "success": True,
                "message": "Product restocked successfully",
                "new_stock": product.stock
            })
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "Product not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt
def order_list_create_view(request):
    if request.method == "GET":
        orders = Order.objects.all().order_by("-created_at")
        return JsonResponse({"success": True, "orders": [serialize_order(o) for o in orders]})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            order = Order.objects.create(
                source="operations",
                customer_name=data.get("customer_name"),
                company_name=data.get("company_name"),
                email=data.get("email"),
                phone=data.get("phone"),
                product_name=data.get("product_name"),
                product_sku=data.get("product_sku"),
                quantity=int(data.get("quantity", 1)),
                unit_price=Decimal(str(data.get("unit_price", 0))),
                status=data.get("status", "pending"),
                delivery_status=data.get("delivery_status", "pending"),
                created_by=request.user if request.user.is_authenticated else None
            )

            if order.product_sku:
                try:
                    product = Product.objects.get(sku=order.product_sku)
                    if product.stock >= order.quantity:
                        product.stock -= order.quantity
                        product.save()
                except Product.DoesNotExist:
                    pass

            return JsonResponse({
                "success": True,
                "message": "Order created successfully",
                "order": serialize_order(order)
            }, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)



@csrf_exempt
def update_order_status_view(request, order_id):
    if request.method == "PATCH":
        try:
            order = Order.objects.get(id=order_id)
            data = json.loads(request.body)

            new_status = data.get("status", order.status)
            order.status = new_status
            order.delivery_status = new_status

            if new_status == "cancelled":
                order.issue_status = "raised"

                from support.models import Ticket

                existing_ticket = Ticket.objects.filter(order=order, category="Order Cancelled").first()

                if not existing_ticket:
                    Ticket.objects.create(
                        order=order,
                        title="Order cancelled issue",
                        customer_name=order.customer_name,
                        customer_email=order.email or "noemail@example.com",
                        product_name=order.product_name,
                        order_date=order.created_at,
                        order_status=order.status,
                        category="Order Cancelled",
                        description=f"Order #{order.id} was cancelled and needs support follow-up.",
                        priority="high",
                        status="open",
                        created_by=request.user if request.user.is_authenticated else None
                    )

            order.save()

            return JsonResponse({
                "success": True,
                "message": "Order status updated successfully",
                "order": serialize_order(order)
            })
        except Order.DoesNotExist:
            return JsonResponse({"success": False, "message": "Order not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def operations_dashboard_view(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    low_stock_count = Product.objects.filter(stock__lte=5).count()

    pending = Order.objects.filter(status="pending").count()
    processing = Order.objects.filter(status="processing").count()
    shipped = Order.objects.filter(status="shipped").count()
    delivered = Order.objects.filter(status="delivered").count()
    cancelled = Order.objects.filter(status="cancelled").count()

    stock_value = sum([p.stock * float(p.price) for p in Product.objects.all()])

    return JsonResponse({
        "success": True,
        "dashboard": {
            "total_products": total_products,
            "total_orders": total_orders,
            "low_stock_count": low_stock_count,
            "stock_value": stock_value,
            "pending": pending,
            "processing": processing,
            "shipped": shipped,
            "delivered": delivered,
            "cancelled": cancelled,
        }
    })


def low_stock_alerts_view(request):
    products = Product.objects.filter(stock__lte=5).order_by("stock")
    return JsonResponse({
        "success": True,
        "alerts": [serialize_product(p) for p in products]
    })


@csrf_exempt
def import_sales_lead_to_order_view(request, lead_id):
    if request.method == "POST":
        try:
            lead = Lead.objects.get(id=lead_id)

            if lead.stage != "purchase_confirmed":
                return JsonResponse({
                    "success": False,
                    "message": "Only Purchase Confirmed leads can be converted to order"
                }, status=400)

            existing = Order.objects.filter(source="sales", lead_reference=lead.id).first()
            if existing:
                return JsonResponse({
                    "success": False,
                    "message": "Order already created for this lead"
                }, status=400)

            order = Order.objects.create(
                source="sales",
                lead_reference=lead.id,
                customer_name=lead.lead_name,
                company_name=lead.company_name,
                email=lead.email,
                phone=lead.phone,
                product_name=lead.product_name,
                quantity=1,
                unit_price=Decimal("0.00"),
                status="pending",
                delivery_status="pending",
                created_by=request.user if request.user.is_authenticated else None
            )

            lead.sent_to_operations = True
            lead.save()

            return JsonResponse({
                "success": True,
                "message": "Sales lead imported to operations order successfully",
                "order": serialize_order(order)
            }, status=201)

        except Lead.DoesNotExist:
            return JsonResponse({"success": False, "message": "Lead not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)