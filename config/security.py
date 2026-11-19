class ContentSecurityPolicyMiddleware:
    """CSP estricta para templates y assets servidos por la aplicación."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
            "form-action 'self'; script-src 'self' https://unpkg.com; "
            "style-src 'self' https://unpkg.com; font-src 'self'; "
            "img-src 'self' data: https://unpkg.com https://*.tile.openstreetmap.org; "
            "connect-src 'self' https://*.tile.openstreetmap.org https://nominatim.openstreetmap.org; "
            "frame-src https://www.openstreetmap.org"
        )
        return response
