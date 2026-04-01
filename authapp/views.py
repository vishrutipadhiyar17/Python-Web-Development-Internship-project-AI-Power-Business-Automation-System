import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q


User = get_user_model()


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            full_name = data.get('full_name')
            username = data.get('username')
            email = data.get('email')
            phone = data.get('phone')
            password = data.get('password')
            role = data.get('role').lower().replace(" ", "_")

            VALID_ROLES = ["hr_staff", "operations_staff", "support_staff", "sales_staff"]

            if role not in VALID_ROLES:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid role selected'
                }, status=400)


            if not full_name or not username or not email or not password or not role:
                return JsonResponse({
                    'success': False,
                    'message': 'All required fields must be filled'
                }, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Username already exists'
                }, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Email already exists'
                }, status=400)

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                phone=phone,
                role=role
            )

            return JsonResponse({
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role
                }
            }, status=201)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            username_input = data.get('username')
            password = data.get('password')

            if not username_input or not password:
                return JsonResponse({
                    'success': False,
                    'message': 'Username/email and password required'
                }, status=400)

            # 🔥 CHECK: email OR username
            user_obj = None

            if '@' in username_input:
                try:
                    user_obj = User.objects.get(email=username_input)
                    username = user_obj.username
                except User.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'User not found'
                    }, status=404)
            else:
                username = username_input

            user = authenticate(request, username=username, password=password)

            if user is not None:
               return JsonResponse({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role
                    }
            })
            else:
                
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid credentials'
                }, status=401)

        except Exception as e:
            print("LOGIN ERROR:", str(e))
              # 🔥 IMPORTANT DEBUG
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)




@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful'
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


def session_view(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'full_name': request.user.full_name,
                'email': request.user.email,
                'role': request.user.role
            }
        })

    return JsonResponse({
        'authenticated': False
    })