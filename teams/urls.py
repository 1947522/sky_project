from django.urls import path
from . import views 

urlpatterns = [
    path('departmentleader/', views.departmentleader, name='departmentleader'),

]