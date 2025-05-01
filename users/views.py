from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import EmployeeSignupForm, AdminUserCreationForm, DepartmentForm, VotingSessionForm
from .models import Employee, HealthCardTermsAcceptance, Team, Department, HealthCard, VotingSession


#vinicius and Shoaibs work
def signup(request):
    #We are using a form, so we are using post
    if request.method == 'POST':
        #Using form from the forms page
        form = EmployeeSignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']

            # Check if email ends with @sky.net. Uses built in checks
            if not email.endswith('@sky.net'):
                #Displays error if the email  given by user doesnt end with @sky.net
                form.add_error('email', 'Email must end with @sky.net.')
                return render(request, 'signup.html', {'form': form})

            try:
                #gets the email from models
                employee = Employee.objects.get(email=email)
                #checks boolean for registered
                if employee.registered:
                    #if registered is true, it sends a message saying log in
                    form.add_error(None, 'You have already registered. Please log in.')
                    return render(request, 'signup.html', {'form': form})


                employee.name = name
                #gets the passwords that is going to be hashed in forms
                employee.set_password(password)
                #sets the boolean for registered to true
                #commits changes to the database
                employee.save()
                #sends a success message on screen
                messages.success(request, 'Registration successful. You can now log in.')
                return redirect('login')
            #buit in check
            except Employee.DoesNotExist:
                form.add_error(None, 'No employee account with this email. Contact your admin.')
                return render(request, 'signup.html', {'form': form})

        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeSignupForm()

    return render(request, 'signup.html', {'form': form})

#vinicius and Shoaibs work
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            employee = Employee.objects.get(email=email)
            if employee.check_password(password):
                request.session['logged_in_email'] = employee.email
                request.session['employee_id'] = employee.id #Added By Sheroz to  Ensure employee ID is stored in session otherwise user could not vote
                request.session['role'] = employee.role
                messages.success(request, 'Login successful.')
                return redirect('home')
            else:
                messages.error(request, 'Incorrect password.')
        except Employee.DoesNotExist:
            messages.error(request, 'No employee found with that email.')

    return render(request, 'login.html')

#vinicius work
def logout_view(request):
    request.session.flush() #logout of the user and clears the session
    list(get_messages(request)) #clear any stored messages
    return redirect('login')

#Shoaibs work
def admin_page(request):
    if request.method == 'POST':
        #gets form from forms
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            #for creating a temporary version of the employee saved in the database. can modify the object still.
            employee = form.save(commit=False)
            #the registered boolean is set to false
            employee.registered = False
            #now the employee is saved
            employee.save()
            messages.success(request, 'User created successfully, you can now signup.')
            return redirect('signup')
    else:
        #form from forms
        form = AdminUserCreationForm()

    return render(request, 'adminpage.html', {'form': form})

#Shoaibs work
def home_view(request):
    email = request.session.get('logged_in_email')

    if not email:
        return redirect('login')

    employee = Employee.objects.get(email=email)

    return render(request, 'home.html', {
        #these are used in home.html to create a dynamic webpage
            'name': employee.name,
            'role': employee.role,
        })
# Sheroz's work
# This view is for the department hub, where department leaders can manage their teams and departments.
def department_hub_view(request):
    # Retrieve the logged-in user's email from the session
    email = request.session.get('logged_in_email')
    if not email:
        # Redirect to login if no email is found in the session
        return redirect('login')

    try:
        # Fetch the employee object using the email
        employee = Employee.objects.get(email=email)

        # Check if the logged-in user is a department leader
        if employee.role.lower() != 'departmentleader':
            # If not a department leader, deny access and redirect to login
            messages.error(request, 'Access denied: not a Department Leader.')
            return redirect('login')

        # Get the department number of the logged-in user
        user_department_id = employee.departmentnumber
        # Fetch all departments from the database
        departments = Department.objects.all()

        # Initialize variables for selected department, team, and teams list
        selected_department = None
        selected_team = None
        teams = []
        show_teams = False  # Flag to indicate if teams should be shown

        # Handle POST requests (e.g., when a department or team is selected)
        if request.method == 'POST':
            # Get the selected department and team IDs from the POST data
            department_id = request.POST.get('departmentId')
            team_id = request.POST.get('teamId')

            if department_id:
                # Fetch the selected department based on the department ID
                selected_department = Department.objects.filter(departmentId=department_id).first()

                # Show teams only if the selected department matches the user's department
                if str(selected_department.departmentId) == str(user_department_id):
                    # Fetch teams belonging to the selected department
                    teams = Team.objects.filter(department=selected_department)
                    show_teams = True

            if team_id and show_teams:
                # Fetch the selected team based on the team ID
                selected_team = Team.objects.filter(teamId=team_id).first()

        # Render the department hub template with the required context
        return render(request, 'department_hub.html', {
            'departments': departments,  # List of all departments
            'teams': teams,  # List of teams in the selected department
            'selected_department': selected_department,  # Currently selected department
            'selected_team': selected_team,  # Currently selected team
            'show_teams': show_teams  # Flag to indicate if teams should be displayed
        })

    except Employee.DoesNotExist:
        # Handle case where the logged-in user is not found in the database
        messages.error(request, 'User not found.')
        return redirect('login')


def department_list(request):
    departments = Department.objects.all()
    return render(request, "department_list.html", {"departments": departments})


def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('department-list')
    return render(request, 'department_form.html', {'form': form})

# Anes and Sheroz's work
# This view allows engineers and team leaders to vote on health cards for their team.
def vote_view(request):
    # Retrieve the logged-in user's email from the session
    email = request.session.get('logged_in_email')
    if not email:
        # Redirect to login if no email is found in the session
        return redirect('login')

    try:
        # Fetch the employee object using the email
        employee = Employee.objects.get(email=email)

        # Restrict voting to engineers and team leaders only
        if employee.role not in ['engineer', 'teamleader']:
            # Display an error message if the user doesn't have permission to vote
            messages.error(request, "You don't have permission to vote on healthcards.")
            return redirect('login')

        # Fetch the team the employee belongs to
        team = Team.objects.get(teamId=employee.teamnumber)

        # Retrieve all health cards associated with the employee's team
        team_healthcards = HealthCard.objects.filter(team__teamId=employee.teamnumber)

        if request.method == 'POST':
            # Handle form submission for voting
            for card in team_healthcards:
                # Retrieve the traffic light, progress, and comment values for each health card
                traffic_light = request.POST.get(f'traffic_light_{card.id}')
                progress = request.POST.get(f'progress_{card.id}')
                comment = request.POST.get(f'comment_{card.id}', '')

                # Ensure traffic light and progress are provided before saving the vote
                if traffic_light and progress:
                    # Create a new vote record in the database
                    Vote.objects.create(
                        employee=employee,
                        healthcard=card,
                        traffic_light=traffic_light,
                        progress=progress,
                        comment=comment
                    )

            # Display a success message after votes are submitted
            messages.success(request, "Your votes have been submitted successfully!")
            # Redirect to the health check page (update the URL name if needed)
            return redirect('healthcheck')

        # Handle GET requests — render the voting page with the default team and health cards
        return render(request, 'vote/voting.html', {
            'employee': employee,  # Pass the logged-in employee's details
            'team': team,  # Pass the team context to display the default team
            'healthcards': team_healthcards,  # Pass the health cards for the team
        })

    except Employee.DoesNotExist:
        # Handle case where the logged-in user is not found in the database
        messages.error(request, "Employee not found.")
        return redirect('login')


def healthcard_list(request):
    # Fetch all HealthCard objects from the database
    healthcards = HealthCard.objects.all()  # This will get all health cards

    # Pass the healthcards to the template
    return render(request, 'healthcards/healthcard_list.html', {
        'healthcards': healthcards
    })

def healthcard_vote(request, card_id): #sheroz work
    # Get the healthcard using the card_id
    healthcard = get_object_or_404(HealthCard, id=card_id)
    # Add your logic for voting
    return render(request, 'vote/voting.html', {'healthcard': healthcard})

#Sheroz's work
def healthcard_terms(request, card_id):
    email = request.session.get('logged_in_email')
    if not email:
        messages.error(request, 'Please log in to continue.')
        return redirect('login')

    try:
        employee = Employee.objects.get(email=email)
        healthcard = HealthCard.objects.get(id=card_id)

        if request.method == 'POST':
            # Save the acceptance in the database
            HealthCardTermsAcceptance.objects.update_or_create(
                employee=employee,
                healthcard=healthcard,
                defaults={'accepted': True}
            )
            # Redirect to the voting page
            return redirect('healthcard_vote', card_id=card_id)

        return render(request, 'vote/terms_and_condi.html', {'healthcard': healthcard})

    except (Employee.DoesNotExist, HealthCard.DoesNotExist):
        messages.error(request, 'Health card or employee not found.')
        return redirect('healthcard-list')


def thank_you_page(request): #anes work
    return render(request, "vote/thank_you.html")

#VINICIUS WORK
def healthcheck_voting_view(request):
    # Log session data for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Session data: {request.session.items()}")

    # Get the logged-in user's email and employee ID from the session
    email = request.session.get('logged_in_email')
    employee_id = request.session.get('employee_id') # Added By Sheroz : Cause user could not vore enven after login as enggineer or team leader

    # If not logged in, redirect to the login page with an error message
    if not email or not employee_id:
        messages.error(request, 'Please log in to continue.')
        return redirect('login')

    try:
        # Get the logged-in employee
        employee = Employee.objects.get(email=email)

        # Fetch the voting sessions
        sessions = VotingSession.objects.all().order_by('-start_date')

        selected_session = None
        # Check if a voting session ID was selected via GET parameter
        selected_session_id = request.GET.get('session_id')

        if selected_session_id:
            # Store the selected session ID in the session for later use
            request.session['selected_session_id'] = selected_session_id
            selected_session = VotingSession.objects.get(id=selected_session_id)

            return redirect('healthcard-list')

        # Render the voting session selection page if no session is selected
        return render(request, 'healthcheck_voting.html', {
            'role': employee.role,
            'sessions': sessions,
            'selected_session': selected_session,
        })

    except Employee.DoesNotExist:
        # If the email doesn't match any Employee, show an error and redirect
        messages.error(request, 'Employee not found.')
        return redirect('login')

#vinicius and Shoaibs work
#same code as create new user or delete new user
def create_session(request):
    #added due to error to get to form
    form = VotingSessionForm()

    if request.method == 'POST':
        form = VotingSessionForm(request.POST)
        if form.is_valid():
            #saves form to create a session with
            form.save()
            messages.success(request, 'Voting session created successfully.')
            return redirect('create_session')  # Redirects to same page if successfyul
        else:
            messages.error(request, 'There was an error in the form submission.')

    return render(request, 'create_session.html', {'form': form})

#vinicius and Shoaibs work
#same code as create new user or delete new user
def delete_session(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        #added for debugging purposes
        #print(f"Session name received: {name}")
        if name:
            try:
                session = VotingSession.objects.get(name=name)
                #deletes session from the database
                session.delete()
                messages.success(request, 'Voting session deleted successfully.')
            except VotingSession.DoesNotExist:
                messages.error(request, 'No voting session found with that name.')
        else:
            messages.error(request, 'No name provided.')

        # Refresh the page after deletion to show the new list of sessions
        return redirect('delete_session')

    # display all sessions
    sessions = VotingSession.objects.all()
    return render(request, 'delete_session.html', {'sessions': sessions})

#vinicius and Shoaibs work
def delete_users_admin(request):
    if request.method == 'POST':
        # Get the email of the user to be deleted
        email = request.POST.get('email')
        # add in case of error for debugging purposes
        #print(f"Received email: {email}")
        if email:
            try:
                # find the employee and email
                employee = Employee.objects.get(email=email)
                # Delete the employee
                employee.delete()
                messages.success(request, 'User deleted successfully.')
            except Employee.DoesNotExist:
                messages.error(request, 'No user found with that email.')
        else:
            messages.error(request, 'No email provided.')

        # Refresh the page after deletion
        return redirect('delete_users_admin')

    # display all users
    users = Employee.objects.all()
    return render(request, 'delete_users_admin.html', {'users': users})

#MEHDI WORK
def profile_view(request):
    email = request.session.get('logged_in_email')
    if not email:
        return redirect('login')

    try:
        user = Employee.objects.get(email=email)
    except Employee.DoesNotExist:
        messages.error(request, 'No employee found.')
        return redirect('login')

    # Get the team and department numbers directly from the user
    teamnumber = user.teamnumber
    departmentnumber = user.departmentnumber

    # You can fetch additional details if needed, but currently, we are passing team/department numbers
    return render(request, 'profile.html', {
        'user': user,
        'teamnumber': teamnumber,
        'departmentnumber': departmentnumber,
    })

#MEHDI WORK
def reset_password_request(request):
    # Check if user is logged in
    if not request.session.get('logged_in_email'):
        return redirect('login')

    if request.method == 'POST':
        entered_email = request.POST.get('email', '').strip().lower()
        logged_email = request.session['logged_in_email'].lower()

        # Verify entered email matches login email
        if entered_email != logged_email:
            messages.error(request, 'You must enter the email address you used to log in.')
            return redirect('reset_password_request')

        return redirect('reset_password_confirm')

    return render(request, 'reset_password_request.html')

#MEHDI WORK
def reset_password_confirm(request):
    if not request.session.get('logged_in_email'):
        return redirect('login')

    logged_email = request.session['logged_in_email']
    password_mismatch = request.session.pop('password_mismatch', False)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            request.session['password_mismatch'] = True
            return redirect('reset_password_confirm')

        try:
            employee = Employee.objects.get(email=logged_email)
            employee.set_password(new_password)
            employee.save()
            messages.success(request, 'Password updated successfully!')
            return redirect('home')

        except Employee.DoesNotExist:
            messages.error(request, 'Account not found.')
            return redirect('login')

    return render(request, 'reset_password_confirm.html', {
        'password_mismatch': password_mismatch
    })


#MEHDI WORK
def password_recovery_request(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = Employee.objects.get(email=email)
            request.session['recovery_email'] = email
            request.session.modified = True  # Force session save
            return redirect('password_recovery_confirm')
        except Employee.DoesNotExist:
            messages.error(request, "No account found with that email address")
            return redirect('password_recovery_request')
    return render(request, 'password_recovery_request.html')

#MEHDI WORK
def password_recovery_confirm(request):
    recovery_email = request.session.get('recovery_email')

    if not recovery_email:
        messages.error(request, "Session expired, please start over")
        return redirect('password_recovery_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'password_recovery_confirm.html')

        try:
            user = Employee.objects.get(email=recovery_email)
            user.set_password(new_password)
            user.save()
            del request.session['recovery_email']
            messages.success(request, "Password updated successfully! Please login")
            return redirect('login')  # Redirect to login page
        except Employee.DoesNotExist:
            messages.error(request, "Account not found")
            return redirect('password_recovery_request')

    return render(request, 'password_recovery_confirm.html')


@login_required
def voting_page(request, healthcard_id):
    # Fetch the health card and its related questions
    healthcard = get_object_or_404(HealthCard, id=healthcard_id)
    questions = healthcard.questions.all()

    if request.method == 'POST':
        try:
            # Call the function to store votes
            store_votes(
                employee=request.user.employee,  # Assuming Employee is linked to the logged-in user
                healthcard=healthcard,
                questions=questions,
                post_data=request.POST
            )

            # Add a success message
            messages.success(request, f"Thank you for voting on the health card: {healthcard.card_name}!")

            # Redirect to the health card list page
            return redirect('healthcard-list')  # Replace 'healthcard-list' with the actual URL name for the health card list page

        except ValueError as e:
            # Handle validation errors (e.g., missing traffic light selection)
            messages.error(request, str(e))
            return redirect('voting_page', healthcard_id=healthcard_id)

    # Render the voting page with the health card and questions
    return render(request, 'vote/voting.html', {
        'healthcard': healthcard,
        'questions': questions
    })

from .models import Vote

def store_votes(employee, healthcard, questions, post_data):
    """
    Stores votes in the database for the given employee, healthcard, and questions.

    Args:
        employee: The employee submitting the votes.
        healthcard: The health card being voted on.
        questions: The list of questions related to the health card.
        post_data: The POST data from the form submission.
    """
    for question in questions:
        traffic_light = post_data.get(f'traffic_light_{question.id}')
        comment = post_data.get(f'comment_{question.id}', '').strip()
        actions = post_data.get(f'actions_{question.id}', '').strip()
        solution = post_data.get(f'solution_{question.id}', '').strip()

        # Ensure traffic light is selected (mandatory)
        if not traffic_light:
            raise ValueError(f"Traffic light not selected for question: {question.text}")

        # Save the vote to the database
        Vote.objects.create(
            employee=employee,
            healthcard=healthcard,
            question=question,
            traffic_light=traffic_light,
            comment=comment,  # Optional
            actions=actions,  # Optional
            solution=solution  # Optional
        )

# filepath: c:\Users\shekhroz\OneDrive\Documents\GitHub\sky_project\users\urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns...
    path('healthcheck/<int:card_id>/vote/', views.healthcard_vote, name='healthcard_vote'),  # Ensure this exists
]
