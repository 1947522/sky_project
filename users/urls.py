from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('home/', views.home_view, name='home'),
    path('departmentleader/', views.department_hub_view, name='departmentleader'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/new/', views.department_create, name='department_create'),


]
