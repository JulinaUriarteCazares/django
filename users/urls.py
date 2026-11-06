from django.urls import path

from .views import RegisterUserView, UserView

urlpatterns = [
    path('auth/me/', UserView.as_view(), name='auth-me'),
    path('auth/register/', RegisterUserView.as_view(), name='auth-register'),
]
