from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

from django.views.generic import RedirectView  
from . import views
from users.views import department_list

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('admin_page/', views.admin_page, name='admin_page'),

    path('departmentleader/', views.department_hub_view, name='departmentleader'),
    path('departments/', views.department_list, name='department-list'),
    path('departments/create/', views.department_create, name='department-create'),
    

    path('', RedirectView.as_view(url='home/')),  
    

    path('home/', views.home_view, name='home'),  
]

