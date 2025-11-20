# diabetes_app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('predict/', views.predict_view, name='predict'),
    path('predict/submit/', views.handle_prediction, name='handle_prediction'),
    path('results/', views.results, name='results'),
    path('api/predict/', views.predict_api, name='predict_api'),
    path('api/health/', views.health_check, name='health_check'),
# --- ADD THESE NEW PATHS ---
    path('register/', views.register, name='register'),
    path('history/', views.prediction_history, name='history'),
    # Use Django's built-in login view
    path('login/', auth_views.LoginView.as_view(template_name='diabetes_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='diabetes_app/logout.html'), name='logout'),
# Authentication URLs

]