from django.urls import path

from . import views


app_name = 'userauth'

urlpatterns = [
    path('register/', views.user_register_view, name='register'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
]
