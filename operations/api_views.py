"""
Shared API Endpoints for Operations Module
Provides REST API for Products and Orders
"""

import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Product, Order


# ========== PRODUCTS API ==========

@csrf_exempt
@require_http_methods(["GET", "POST"])
def products_api(request):
    """Get all products or create new product"""
    if request.method == "GET":
        try:
            products = Product.objects.all().values(
                'id', 'name', 'sku', 'category', 'price', 'stock', 'low_threshold', 'created_at'
            ).order_by('-created_at')
            
            product_list = []
            for p in products:
                product_list.append({
                    'id': p['id'],
                    'name': p['name'],
                    'sku': p['sku'],
                    'category': p['category'],
                    'price': float(p['price']),
                    'stock': p['stock'],
                    'low_threshold': p['low_threshold'],
                    'created_at': p['created_at'].strftime('%Y-%m-%d') if p['created_at'] else ''
                })
            
            return JsonResponse({
                'success': True,
                'products': product_list,
                'count': len(product_list)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Check if product with same SKU exists
            if Product.objects.filter(sku=data.get('sku')).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Product with this SKU already exists'
                }, status=400)
            
            product = Product.objects.create(
                name=data.get('name'),
                sku=data.get('sku'),
                category=data.get('category'),
                price=Decimal(str(data.get('price', 0))),
                stock=int(data.get('stock', 0)),
                low_threshold=int(data.get('low_threshold', 5))
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Product added successfully',
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'stock': product.stock
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def product_detail_api(request, sku):
    """Get, update or delete a specific product"""
    try:
        product = Product.objects.get(sku=sku)
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    
    if request.method == "GET":
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category,
                'price': float(product.price),
                'stock': product.stock,
                'low_threshold': product.low_threshold
            }
        })
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            product.name = data.get('name', product.name)
            product.category = data.get('category', product.category)
            product.price = Decimal(str(data.get('price', product.price)))
            product.stock = int(data.get('stock', product.stock))
            product.low_threshold = int(data.get('low_threshold', product.low_threshold))
            product.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Product updated successfully',
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'stock': product.stock
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    elif request.method == "DELETE":
        product_name = product.name
        product.delete()
        return JsonResponse({
            'success': True,
            'message': f'Product {product_name} deleted successfully'
        })
