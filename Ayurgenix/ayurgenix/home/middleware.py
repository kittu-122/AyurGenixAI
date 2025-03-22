# middleware.py
from django.http import JsonResponse
from django.conf import settings
import logging
import time
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Uncaught exception: {str(e)}", exc_info=True)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Internal server error'}, status=500)
            raise  # Re-raise the exception for non-AJAX requests

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        logger.info(
            f"Path: {request.path} | Method: {request.method} | "
            f"Status: {response.status_code} | Duration: {duration:.2f}s"
        )
        return response

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            user_ip = request.META.get('REMOTE_ADDR')
            cache_key = f'rate_limit_{user_ip}'
            requests = cache.get(cache_key, 0)
            
            if requests >= settings.RATE_LIMIT_MAX_REQUESTS:
                logger.warning(f"Rate limit exceeded for IP: {user_ip}")
                raise PermissionDenied("Rate limit exceeded")
            
            cache.set(cache_key, requests + 1, settings.RATE_LIMIT_WINDOW)
        
        return self.get_response(request)
