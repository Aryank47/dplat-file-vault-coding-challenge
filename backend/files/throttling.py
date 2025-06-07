from rest_framework.throttling import SimpleRateThrottle
from django.conf import settings

class UserIdRateThrottle(SimpleRateThrottle):
    scope = 'user'

    def get_cache_key(self, request, view):
        user_id = request.headers.get('UserId', 'anonymous')
        if not user_id:
            user_id = 'anonymous'
        ident = user_id
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    @property
    def rate(self):
        calls = getattr(settings, 'API_CALL_LIMIT', 2)
        period = getattr(settings, 'API_CALL_PERIOD', 1)
        return f"{calls}/{period}s"

