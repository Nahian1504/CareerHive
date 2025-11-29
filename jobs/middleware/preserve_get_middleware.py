class PreserveGetMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(response, 'url') and request.GET:
            separator = '&' if '?' in response.url else '?'
            response.url += separator + request.GET.urlencode()
        
        return response