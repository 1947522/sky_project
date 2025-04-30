from django.urls import path
from django.contrib.auth import views as auth_views


from . import views

from django.views.generic import RedirectView  
from . import views
from users.views import department_list, healthcheck_voting_view

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_page/', views.admin_page, name='admin_page'),

    path('departmentleader/', views.department_hub_view, name='departmentleader'),
    path('departments/', views.department_list, name='department-list'),
    path('departments/create/', views.department_create, name='department-create'),
    path('vote/', views.vote_view, name='vote'),
    path('', RedirectView.as_view(url='home/')),
    path('healthcheck/', views.healthcard_list, name='healthcard-list'),
    path('healthcheck/<int:card_id>/terms/', views.healthcard_terms, name='healthcard-terms'),
    #path('healthcheck/<int:card_id>/vote/', views.healthcard_vote, name='healthcard-vote'),
    path('home/', views.home_view, name='home'),
    path('healthcheck_voting/', views.healthcheck_voting_view, name='healthcheck_voting'),
    path("healthcheck/<int:healthcard_id>/questions/", views.healthcard_questions_vote, name="healthcard_questions_vote"),
    path("thank-you/", views.thank_you_page, name="thank_you_page"),
    path('delete_users_admin/', views.delete_users_admin, name='delete_users_admin'),
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('profile/', views.profile_view, name='profile'),
    path('reset_password/', views.reset_password_request, name='reset_password_request'),
    path('reset_password/confirm/', views.reset_password_confirm, name='reset_password_confirm'),
    path('create_session/', views.create_session, name='create_session'),
    path('delete_session/', views.delete_session, name='delete_session'),
]


