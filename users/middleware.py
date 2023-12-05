from django.shortcuts import render
from .models import SystemState
from django.urls import resolve, reverse
from django.contrib.auth import logout

class SystemStateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_url = resolve(request.path_info).url_name
        bypass_urls = ['admin_dash', 'toggle_system_state']

        # Check if the request path starts with the Django admin URL
        if request.path.startswith(reverse('admin:index')) or current_url in bypass_urls:
            return self.get_response(request)

        state = SystemState.objects.first()
        if state and not state.is_open and hasattr(request.user, 'is_student') and request.user.is_student:
            logout(request)  # End the student's session
            return render(request, 'SiteUnavailable.html')

        return self.get_response(request)