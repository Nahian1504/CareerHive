from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def preserve_get_params(default_redirect=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            if hasattr(response, 'url') and request.GET:
                separator = '&' if '?' in response.url else '?'
                response.url += separator + request.GET.urlencode()
            return response
        return _wrapped_view
    return decorator
