import logging

from django.contrib.auth import logout
from django.contrib.messages import get_messages
from django.db import transaction
from django.shortcuts import render, redirect,get_object_or_404
from django.utils import timezone

from .forms import EmployeeSignupForm, AdminUserCreationForm, DepartmentForm, VotingSessionForm
from .models import Employee, Team, Department, Vote, HealthCard, Question, VotingSession, Answer
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
                return redirect('home')

            if employee.role.lower() == 'admin':
                return redirect('admin_page')

            else:
                messages.error(request, 'Incorrect password.')
                return redirect('login')

        except Employee.DoesNotExist:
            messages.error(request, 'No employee found with that email.')
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush() #logout of the user and clears the session
    list(get_messages(request)) #clear any stored messages
    return redirect('login')


def admin_page(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.registered = False
            employee.save()
            messages.success(request, 'User created successfully, you can now signup.')
            return redirect('signup')
    else:
        form = AdminUserCreationForm()

    return render(request, 'adminpage.html', {'form': form})

def home_view(request):
    email = request.session.get('logged_in_email')

    if not email:
        return redirect('login')

    employee = Employee.objects.get(email=email)

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
    return render(request, "department_list.html", {"departments": departments})


def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('department-list')
    return render(request, 'department_form.html', {'form': form})


def vote_view(request):
    email = request.session.get('logged_in_email')
    if not email:
        return redirect('login')  # Redirect to login if no session email

    try:
        # Get logged-in employee
        employee = Employee.objects.get(email=email)

        # Allow only engineers and teamleaders to vote
        if employee.role not in ['engineer', 'teamleader']:
            messages.error(request, "You don't have permission to vote on healthcards.")
            return redirect('login')

        # Get the team the employee belongs to (this will be their default team)
        team = Team.objects.get(teamId=employee.teamnumber)

        # Get relevant healthcards for the team
        team_healthcards = HealthCard.objects.filter(team__teamId=employee.teamnumber)

        if request.method == 'POST':
            for card in team_healthcards:
                traffic_light = request.POST.get(f'traffic_light_{card.id}')
                progress = request.POST.get(f'progress_{card.id}')
                comment = request.POST.get(f'comment_{card.id}', '')

                if traffic_light and progress:
                    Vote.objects.create(
                        employee=employee,
                        healthcard=card,
                        traffic_light=traffic_light,
                        progress=progress,
                        comment=comment
                    )

            messages.success(request, "Your votes have been submitted successfully!")
            return redirect('healthcheck')  # Use correct name from urls.py

        # GET request — render voting page with the default team displayed
        return render(request, 'vote/voting.html', {
            'employee': employee,
            'team': team,  # Pass the team context to display the default team
            'healthcards': team_healthcards,
        })

    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect('login')



def healthcard_list(request):
    employee_id = request.session.get("employee_id")
    try:
        employee = Employee.objects.get(id=employee_id)
        team_healthcards = HealthCard.objects.filter(team__teamId=employee.teamnumber)
        return render(request, "healthcards/healthcard_list.html", {
            "healthcards": team_healthcards,
            "employee": employee
        })
    except Employee.DoesNotExist:
         logger.error(f"Session error: Employee ID {employee_id} not found in healthcard_list.")
         messages.error(request, "Employee not found.")
         request.session.flush()
         return redirect("login")
    except Team.DoesNotExist:
         logger.error(f"Data error: Team ID {employee.teamnumber} not found for employee {employee_id}.")
         messages.error(request, "Team not found for this employee.")
         return redirect("home")
    except Exception as e:
        logger.exception(f"Unexpected error in healthcard_list for employee {employee_id}: {e}")
        messages.error(request, f"An error occurred: {e}")
        return redirect("home")

@login_required
def healthcheck_page(request):
    # Get the current question number from the query parameter
    question_number = int(request.GET.get('q', 1))  # Default to question 1
    healthcard = HealthCard.objects.first()  # This could be dynamically set if needed

    # Get all questions for this healthcard
    questions = healthcard.questions.all()
    total_questions = questions.count()

    # Ensure the question number is within bounds
    if question_number < 1:
        question_number = 1
    elif question_number > total_questions:
        question_number = total_questions

    # Get the current question based on question_number
    question = questions[question_number - 1]
    
    # Fetch any existing vote for the user on this question
    existing_vote = Vote.objects.filter(employee=request.user, healthcard=healthcard, question=question).first()

    # If it's the last question and the request method is POST
    if question_number == total_questions and request.method == 'POST':
        # Get the user's input
        traffic_light = request.POST.get('traffic_light')
        comment = request.POST.get('comment')

        # Save or update the vote
        if existing_vote:
            existing_vote.traffic_light = traffic_light
            existing_vote.comment = comment
            existing_vote.save()
        else:
            Vote.objects.create(
                employee=request.user,
                healthcard=healthcard,
                question=question,
                traffic_light=traffic_light,
                comment=comment
            )

        # Redirect to a thank you page after the last question
        return redirect('thank_you_page')

    # If it's not the last question, simply allow navigation to the next question
    if question_number < total_questions and request.method == 'POST':
        # Redirect to the next question after submitting the vote
        return redirect(f"?q={question_number + 1}")

    return render(request, 'healthcheck_page.html', {
        'healthcard': healthcard,
        'question': question,
        'question_number': question_number,
        'total_questions': total_questions,
        'existing_vote': existing_vote,
        'is_last_question': question_number == total_questions  # This helps in the template
    })


def healthcard_vote(request, healthcard_id):
    return redirect("healthcard_questions_vote", healthcard_id=healthcard_id)

logger = logging.getLogger(__name__)



def healthcard_terms(request, healthcard_id):
    try:
        healthcard = get_object_or_404(HealthCard, id=healthcard_id)
        question_count = Question.objects.filter(healthcard=healthcard).count()

        if question_count == 0:
            messages.warning(request,
                             f"There are no questions available for {healthcard.card_name}. Please contact an administrator.")
            return redirect("healthcard-list")

        context = {
            "healthcard": healthcard,
            "user_has_accepted_terms": False
        }
        return render(request, "vote/terms_and_condi.html", context)
    except Exception as e:
        logger.exception(f"Error in healthcard_terms view: {e}")
        raise


def healthcard_questions_vote(request, healthcard_id): #anes work
    employee_id = request.session.get("employee_id")
    logger.info(f"Entering healthcard_questions_vote for employee {employee_id}, healthcard {healthcard_id}")

    employee = get_object_or_404(Employee, id=employee_id)
    healthcard = get_object_or_404(HealthCard, id=healthcard_id)
    questions = Question.objects.filter(healthcard=healthcard).order_by("id")

    # Role check
    if employee.role not in ["engineer", "teamleader"]:
        messages.error(request, "You don't have permission to vote.")
        return redirect("healthcard-list")

    # Team match check
    if healthcard.team.teamId != employee.teamnumber:
        messages.error(request, "You can only vote on healthcards for your team.")
        return redirect("healthcard-list")

    # Already voted check
    existing_answers = Answer.objects.filter(employee=employee, question__healthcard=healthcard)
    if existing_answers.exists():
        messages.info(request, f"You have already submitted answers for {healthcard.card_name}.")
        return redirect("healthcard-list")

    if request.method == "POST":
        # Terms acceptance check
        if not request.POST.get("accept_terms"):
            messages.error(request, "You must accept the terms and conditions before proceeding.")
            return render(request, "vote/question_vote.html", {
                "healthcard": healthcard,
                "questions": questions,
                "employee": employee,
                "submitted_data": request.POST
            })

        answers_data = {}
        valid_submission = True

        # Optional: prepare question map to avoid multiple DB hits
        question_map = {q.id: q for q in questions}

        for question in questions:
            answer_key = f"answer_q_{question.id}"
            answer_value = request.POST.get(answer_key)

            if not answer_value or answer_value not in dict(Answer.TRAFFIC_LIGHT_CHOICES):
                valid_submission = False
                messages.error(
                    request,
                    f"Please select an answer for all questions. Missing or invalid answer for: '{question.text[:50]}...'"
                )
                break

            answers_data[question.id] = answer_value

        if valid_submission:
            try:
                with transaction.atomic():
                    for question_id, traffic_light_value in answers_data.items():
                        question = question_map.get(question_id)
                        Answer.objects.create(
                            employee=employee,
                            question=question,
                            traffic_light=traffic_light_value,
                            created_at=timezone.now()
                        )
                messages.success(
                    request,
                    f"Your answers for '{healthcard.card_name}' have been submitted successfully!"
                )
                return redirect("healthcard-list")
            except Exception as e:
                logger.exception(f"Error saving answers for employee {employee.id} on healthcard {healthcard.id}: {e}")
                messages.error(
                    request,
                    "An unexpected error occurred while saving your answers. Please try again later."
                )
                raise

        # Form had errors; re-render with submitted data
        return render(request, "vote/question_vote.html", {
            "healthcard": healthcard,
            "questions": questions,
            "employee": employee,
            "submitted_data": request.POST
        })

    # GET request: show form
    return render(request, "vote/question_vote.html", {
        "healthcard": healthcard,
        "questions": questions,
        "employee": employee
    })

def thank_you_page(request):
    return render(request, "vote/thank_you.html")


def healthcheck_voting_view(request):
    email = request.session.get('logged_in_email')

    if not email:
        messages.error(request, 'Please log in to continue.')
        return redirect('login')

    try:
        # Get the logged-in employee
        employee = Employee.objects.get(email=email)

        # Fetch the voting sessions
        sessions = VotingSession.objects.all().order_by('-start_date')

        selected_session = None
        selected_session_id = request.GET.get('session_id')

        if selected_session_id:
            request.session['selected_session_id'] = selected_session_id
            selected_session = VotingSession.objects.get(id=selected_session_id)

            return redirect('healthcard-list')

        return render(request, 'healthcheck_voting.html', {
            'role': employee.role,
            'sessions': sessions,
            'selected_session': selected_session,
        })

    except Employee.DoesNotExist:
        messages.error(request, 'Employee not found.')
        return redirect('login')


def create_session(request):
    #added due to error to get to form
    form = VotingSessionForm()

    if request.method == 'POST':
        form = VotingSessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voting session created successfully.')
            return redirect('create_session')  # Redirect to the session creation page after success
        else:
            messages.error(request, 'There was an error in the form submission.')

    return render(request, 'create_session.html', {'form': form})

def delete_session(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        print(f"Session name received: {name}")
        if name:
            try:
                session = VotingSession.objects.get(name=name)
                session.delete()
                messages.success(request, 'Voting session deleted successfully.')
            except VotingSession.DoesNotExist:
                messages.error(request, 'No voting session found with that name.')
        else:
            messages.error(request, 'No name provided.')

        # Refresh the page after deletion
        return redirect('delete_session')

    # display all sessions
    sessions = VotingSession.objects.all()
    return render(request, 'delete_session.html', {'sessions': sessions})

def delete_users_admin(request):
    if request.method == 'POST':
        # Get the email of the user to be deleted
        email = request.POST.get('email')
        #print(f"Received email: {email}")  # add in case of error for debugging purposes
        if email:
            try:
                # find the employee and email
                employee = Employee.objects.get(email=email)
                employee.delete()  # Delete the employee
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


# views.py
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
