from django.urls import path
from . import views

urlpatterns = [
    # -- Master / Teammates --
    path('forms/', views.registration, name='registration'),
    path('forms/success/', views.success, name='success'),
]
