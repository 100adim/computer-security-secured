from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('customer_list/', views.customer_list, name='customer_list'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_reset_code/', views.verify_reset_code, name='verify_reset_code'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('user_list/', views.user_list, name='user_list'),

]
