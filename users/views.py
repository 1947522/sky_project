from django.shortcuts import render, redirect
from .forms import EmployeeSignupForm, AdminUserCreationForm,DepartmentForm
from .models import Employee,Team, Department
from django.contrib import messages




def signup(request):
    if request.method == 'POST':
        form = EmployeeSignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']

            # Email domain check
            if not email.endswith('@sky.net'):
                form.add_error('email', 'Email must end with @sky.net.')
                return render(request, 'signup.html', {'form': form})

            try:
                employee = Employee.objects.get(email=email)

                if employee.registered:
                    form.add_error(None, 'You have already registered. Please log in.')
                    return render(request, 'signup.html', {'form': form})


                employee.name = name
                employee.set_password(password)
                employee.registered = True
                employee.save()

                messages.success(request, 'Registration successful. You can now log in.')
                return redirect('login')

            except Employee.DoesNotExist:
                form.add_error(None, 'No employee account with this email. Contact your admin.')
                return render(request, 'signup.html', {'form': form})

        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeSignupForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            employee = Employee.objects.get(email=email)

            if not employee.email.endswith('@sky.net'):
                messages.error(request, 'Invalid email domain.')
                return redirect('login')

            if not employee.registered:
                messages.error(request, 'Employee is not registered yet.')
                return redirect('login')

            if employee.check_password(password):
                request.session['logged_in_email'] = employee.email
                request.session['role'] = employee.role
                messages.success(request, 'Login successful.')

                role = employee.role.lower()

                if role == 'admin':
                    return redirect('admin_page')
                elif role == 'departmentleader':
                    return redirect('departmentleader')
                elif role == 'teamleader':
                    return redirect('team_summary')  # adjust if needed
                elif role == 'seniormanager':
                    return redirect('org_summary')   # adjust if needed
                elif role == 'engineer':
                    return redirect('healthcheck')   # adjust if needed
                else:
                    return redirect('home')

            else:
                messages.error(request, 'Incorrect password.')
                return redirect('login')

        except Employee.DoesNotExist:
            messages.error(request, 'No employee found with that email.')
            return redirect('login')

    return render(request, 'login.html')

#def home_view(request):
# return render(request, 'home.html')


def admin_page(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.registered = False
            employee.save()
            messages.success(request, 'User created successfully.')
            return redirect('admin_page')
    else:
        form = AdminUserCreationForm()

    return render(request, 'adminpage.html', {'form': form})

def home_view(request):
    email = request.session.get('logged_in_email')

    if not email:
        return redirect('login')

    employee = Employee.objects.get(email=email)

    # # Redirect based on the role of the employee
    # if employee.role.lower() == 'admin':
    #     return redirect('admin_page')  # Redirect to admin page
    # elif employee.role.lower() == 'departmentleader':
    #     return redirect('departmentleader')  # Redirect to department leader page
    # elif employee.role.lower() == 'teamleader':
    #     return redirect('team_summary')  # Redirect to team summary page
    # elif employee.role.lower() == 'seniormanager':
    #     return redirect('org_summary')  # Redirect to senior manager summary page
    # elif employee.role.lower() == 'engineer':
    #     return redirect('healthcheck')  # Redirect to engineer page
    # else:
    return render(request, 'home.html', {
            'name': employee.name,
            'role': employee.role,
        })

def department_hub_view(request):
    email = request.session.get('logged_in_email')
    if not email:
        return redirect('login')

    try:
        employee = Employee.objects.get(email=email)

        if employee.role.lower() != 'departmentleader':
            messages.error(request, 'Access denied: not a Department Leader.')
            return redirect('login')

        user_department_id = employee.departmentnumber
        departments = Department.objects.all()

        selected_department = None
        selected_team = None
        teams = []
        show_teams = False  # Flag to indicate if teams should be shown

        if request.method == 'POST':
            department_id = request.POST.get('departmentId')
            team_id = request.POST.get('teamId')

            if department_id:
                selected_department = Department.objects.filter(departmentId=department_id).first()

                # Show teams only if selected department is user's own
                if str(selected_department.departmentId) == str(user_department_id):
                    teams = Team.objects.filter(department=selected_department)
                    show_teams = True

            if team_id and show_teams:
                selected_team = Team.objects.filter(teamId=team_id).first()

        return render(request, 'department_hub.html', {
            'departments': departments,
            'teams': teams,
            'selected_department': selected_department,
            'selected_team': selected_team,
            'show_teams': show_teams
        })

    except Employee.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')

def department_list(request):
    departments = Department.objects.all()
    return  render(request, 'department_list.html', {'departments': departments})


def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('department-list')

    return render(request, 'department_form.html', {'form': form})
