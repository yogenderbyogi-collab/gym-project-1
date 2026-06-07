from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps


def ratelimited(key='ip', rate='5/m', block=False, method='POST'):
    """
    Simple rate limiting decorator.
    - key: 'ip' or 'user'
    - rate: requests per time unit (e.g., '5/m', '10/h', '100/d')
    - block: if True, returns 403; if False, allows but doesn't protect
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            parts = rate.split('/')
            max_requests = int(parts[0])
            time_unit = parts[1] if len(parts) > 1 else 'm'
            
            time_windows = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
            window = time_windows.get(time_unit, 60)
            
            ident = request.META.get('REMOTE_ADDR', 'unknown') if key == 'ip' else str(request.user.id)
            cache_key = f"ratelimit:{ident}:{request.path}:{method}"
            
            count = cache.get(cache_key, 0)
            request.is_ratelimited = count >= max_requests
            
            if request.is_ratelimited and block:
                return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
            
            if request.method == method.upper():
                try:
                    cache.incr(cache_key)
                except ValueError:
                    cache.set(cache_key, 1, window)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator