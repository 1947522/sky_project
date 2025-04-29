from django.urls import path
from django.contrib.auth import views as auth_views
<<<<<<< HEAD

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
    path('vote/', views.vote_view, name='vote'),
    # path('healthcheck/', views.vote_view, name='healthcheck'),
    path('', RedirectView.as_view(url='home/')),  
    path('engineer/', views.engineer_hub_view, name='engineer'),
    path('healthcheck/', views.healthcard_list, name='healthcard-list'),
    path('healthcheck/<int:card_id>/terms/', views.healthcard_terms, name='healthcard-terms'),
    path('healthcheck/<int:card_id>/vote/', views.healthcard_vote, name='healthcard-vote'),
    path('home/', views.home_view, name='home'),  
]

=======
from django.views.generic import RedirectView  
from . import views
# from users.views import department_list # Import specific views if needed, avoid importing the whole module if possible

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("admin_page/", views.admin_page, name="admin_page"),

    path("departmentleader/", views.department_hub_view, name="departmentleader"),
    path("departments/", views.department_list, name="department-list"),
    path("departments/create/", views.department_create, name="department-create"),
    # path("vote/", views.vote_view, name="vote"), # Commented out as vote_view seems deprecated/removed
    path("", RedirectView.as_view(url="home/")),  
    path("engineer/", views.engineer_hub_view, name="engineer"),
    path("healthcheck/", views.healthcard_list, name="healthcard-list"),
    path("healthcheck/<int:healthcard_id>/terms/", views.healthcard_terms, name="healthcard-terms"),
    # path("healthcheck/<int:card_id>/vote/", views.healthcard_vote, name="healthcard-vote"), # This now redirects to questions view
    path("healthcheck/<int:healthcard_id>/questions/", views.healthcard_questions_vote, name="healthcard_questions_vote"),
    path("thank-you/", views.thank_you_page, name="thank_you_page"),
    path("home/", views.home_view, name="home"),  
]
>>>>>>> 258c6958b635ef4433de90537cf2e114713c8e91
