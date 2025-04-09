from django.shortcuts import render, redirect
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

        # Create an Employee instance
        employee = Employee(email=email, name=name, teamnumber=teamnumber, departmentnumber=departmentnumber)

        try:
            employee.clean()
            employee.registered = True
            # Save the employee if validation is successful
            employee.save()
            messages.success(request, 'You have successfully signed up.')
            return redirect('home')  # Redirect to a home or success page

        except ValidationError as e:
            messages.error(request, e.message)  # Display the validation error

    return render(request, 'signup.html')


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
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                return redirect('home')  # Redirect to a home or success page
            else:
                # If authentication fails
                messages.error(request, 'Invalid username or password')
        else:
            # If form is not valid
            messages.error(request, 'Invalid username or password')

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def home_view(request):
    return render(request, 'home.html')