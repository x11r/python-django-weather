from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact_us, name='contact'),
    path('about/', views.about_us, name='about'),
    path('weather/', views.weather_top, name='weather_top'),
]