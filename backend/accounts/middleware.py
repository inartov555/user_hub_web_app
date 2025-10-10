from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

class LastSeenMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            user.last_seen = timezone.now()
            user.save(update_fields=['last_seen'])
        return None
