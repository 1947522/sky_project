from django.shortcuts import render, redirect
from .forms import EmployeeForm
from .models import Employee
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login



def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        teamnumber = request.POST.get('teamnumber')
        departmentnumber = request.POST.get('departmentnumber')
        form = EmployeeForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                employee = Employee.objects.get(email=email)

                if employee.registered:
                    messages.error(request, 'Email already registered')
                    return redirect('signup')
                else:
                    employee.registered = True
                    employee.save()
                    messages.success(request, 'Email successfully registered')
                    return redirect('login')

            except Employee.DoesNotExist:
                # Create an Employee instance
                employee = Employee(
                    email=email,
                    name=name,
                    teamnumber=teamnumber,
                    departmentnumber=departmentnumber,
                    registered=True
                )
                employee.save()
                messages.success(request, 'Email successfully registered')
                return redirect('login')
        else:
            print(form.errors)
            messages.error(request, 'Employee already registered')
    else:
        form = EmployeeForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            # If the form is valid, authenticate the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # If the user is authenticated, log the user in
                try:
                    employee = Employee.objects.get(email=user.email)
                    if employee.registered:
                        login(request, user)
                        messages.success(request, 'You have successfully logged in.')
                        return redirect('home')  # Redirect to a home or success page
                    else:
                        messages.error(request, 'Employee is not registered yet.')
                        return redirect('login')
                except Employee.DoesNotExist:
                    messages.error(request, 'Employee does not exist')
                    return redirect('login')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'dbnjghdjnda')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def home_view(request):
    return render(request, 'home.html')