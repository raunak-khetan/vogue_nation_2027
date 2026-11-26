from django.urls import path, re_path
from . import views

urlpatterns = [
    # Registration routes
    path('forms/', views.registration, name='registration'),
    path('forms/success/', views.success, name='success'),
    path('', views.landing, name='landing'),
    re_path(r'^video/(?P<filename>[^/]+)/?$', views.video_stream, name='video_stream'),
]
