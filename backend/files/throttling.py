from rest_framework.throttling import SimpleRateThrottle
from django.conf import settings

class UserIdRateThrottle(SimpleRateThrottle):
    """Throttle class enforcing request limits per custom time window."""

    scope = 'user'

    def get_cache_key(self, request, view):
        user_id = request.headers.get('UserId', 'anonymous') or 'anonymous'
        ident = user_id
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident,
        }

    @property
    def rate(self) -> str:
        """Return DRF rate string like '5/10s'."""
        calls = getattr(settings, 'API_CALL_LIMIT', 2)
        period = getattr(settings, 'API_CALL_PERIOD', 1)
        return f"{calls}/{period}s"

    def parse_rate(self, rate: str):
        """Allow numeric second-based durations (e.g. '5/10s')."""
        if rate is None:
            return (None, None)

        try:
            num, period = rate.split('/')
            num_requests = int(num)
        except ValueError:
            return (None, None)

        if period.endswith('s'):
            try:
                seconds = int(period[:-1] or '1')
            except ValueError:
                return (None, None)
            return num_requests, seconds

        return super().parse_rate(rate)

