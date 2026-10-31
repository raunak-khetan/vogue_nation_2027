from django.urls import path
from . import views

urlpatterns = [
    # Registration routes
    path('forms/', views.registration, name='registration'),
    path('forms/success/', views.success, name='success'),
    path('glimpses/' , views.glimpses , name = 'glimpses')
]
