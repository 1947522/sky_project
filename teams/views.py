from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def departmentleader(request):
    return render(request, 'dep_leader_page.html')
