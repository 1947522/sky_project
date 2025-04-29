from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

from django.views.generic import RedirectView  
from . import views
from users.views import department_list

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_page/', views.admin_page, name='admin_page'),

    path('departmentleader/', views.department_hub_view, name='departmentleader'),
    path('departments/', views.department_list, name='department-list'),
    path('departments/create/', views.department_create, name='department-create'),
    path('vote/', views.vote_view, name='vote'),
    # path('healthcheck/', views.vote_view, name='healthcheck'),
    path('', RedirectView.as_view(url='home/')),  
    path('engineer/', views.engineer_hub_view, name='engineer'),
    path('healthcheck/', views.healthcard_list, name='healthcard-list'),
    path('healthcheck/<int:card_id>/terms/', views.healthcard_terms, name='healthcard-terms'),
    path('healthcheck/<int:card_id>/vote/', views.healthcard_vote, name='healthcard-vote'),
    path('home/', views.home_view, name='home'),  
]

