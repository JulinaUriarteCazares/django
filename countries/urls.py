from django.urls import path

from .views import pais_soap

urlpatterns = [
    path('countries/<str:iso_code>/', pais_soap, name='soap-country'),
]
