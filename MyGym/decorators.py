from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages


def ratelimited_view(rate='5/m'):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            from django_ratelimit.decorators import ratelimit
            decorated = ratelimit(key='ip', rate=rate, method='POST', block=False)(func)
            response = decorated(request, *args, **kwargs)
            if getattr(request, 'limited', False):
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'Too many requests. Try again later.'}, status=429)
                messages.error(request, 'Too many requests. Please wait.')
                return redirect('home')
            return response
        return wrapper
    return decorator