from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf import settings
import os
import mimetypes

# Correct path calculation: urls.py is in backend/backend/, need to go up 2 levels to reach project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
PAGES_DIR = os.path.join(PROJECT_ROOT, 'pages')

def serve_file(request, file_path):
    """Serve static files (HTML, CSS, JS, images)"""
    file_path = file_path.lstrip('/')
    
    # Security: prevent directory traversal
    if '..' in file_path or file_path.startswith('/'):
        return HttpResponse('Access denied', status=403)
    
    # Try to find the file
    possible_locations = []
    
    # If path starts with 'pages/', it's in the pages directory
    if file_path.startswith('pages/'):
        # Remove 'pages/' prefix and look in PAGES_DIR
        pages_file = file_path[6:]  # Remove 'pages/' prefix
        possible_locations.append(os.path.join(PAGES_DIR, pages_file))
    # If path starts with 'frontend/', it's in the frontend directory
    elif file_path.startswith('frontend/'):
        # Remove 'frontend/' prefix and look in FRONTEND_DIR
        frontend_file = file_path[9:]  # Remove 'frontend/' prefix
        possible_locations.append(os.path.join(FRONTEND_DIR, frontend_file))
    else:
        # Try frontend first for root level files
        possible_locations.append(os.path.join(FRONTEND_DIR, file_path))
    
    # Also try both directories as fallback
    possible_locations.append(os.path.join(FRONTEND_DIR, file_path))
    possible_locations.append(os.path.join(PAGES_DIR, file_path))
    
    for full_path in possible_locations:
        full_path = os.path.normpath(full_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                mime_type, _ = mimetypes.guess_type(full_path)
                if mime_type is None:
                    mime_type = 'text/html'
                
                with open(full_path, 'rb') as f:
                    return HttpResponse(f.read(), content_type=mime_type)
            except Exception as e:
                return HttpResponse(f'Error reading file: {str(e)}', status=500)
    
    return HttpResponse(f'File not found: {file_path}', status=404)

def index(request):
    """Serve the index.html login page"""
    index_path = os.path.join(FRONTEND_DIR, 'index.html')
    index_path = os.path.normpath(index_path)
    
    if os.path.exists(index_path) and os.path.isfile(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='text/html')
        except Exception as e:
            return HttpResponse(f'Error: Could not load index.html - {str(e)}', status=500)
    
    return HttpResponse('index.html not found', status=404)

urlpatterns = [
    # Root and login page
    path('', index, name='home'),
    path('index.html', index),
    
    # Catch-all for all static files (HTML, CSS, JS, images)
    re_path(r'^(?P<file_path>.+\.(html|css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot))$', serve_file),
    
    # Django admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('authapp.urls')),
    path('api/hr/', include('hr.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/operations/', include('operations.urls')),
    path('api/support/', include('support.urls')),
]