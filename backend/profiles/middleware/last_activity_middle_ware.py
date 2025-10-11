from django.utils import timezone

from .models.profile import Profile


class LastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            Profile.objects.filter(user=user).update(last_activity=timezone.now())
        return response
