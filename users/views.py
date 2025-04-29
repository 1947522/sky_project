<<<<<<< HEAD
from django.shortcuts import render, redirect,get_object_or_404
from .forms import EmployeeSignupForm, AdminUserCreationForm,DepartmentForm
from .models import Employee,Team, Department,Vote,HealthCard, Question
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
=======
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from functools import wraps
import logging
import traceback

from .forms import EmployeeSignupForm, AdminUserCreationForm, DepartmentForm
from .models import Employee, Team, Department, Vote, HealthCard, Question, Answer
from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger(__name__)

# --- Custom Decorator for Authentication ---

def employee_login_required(view_func):
    """
    Decorator for views that checks if an employee is logged in via session,
    redirects to the login page if not.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get("employee_id"):
            logger.warning(f"Authentication required for {request.path}. Redirecting to login.")
            return redirect(settings.LOGIN_URL + f"?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- Authentication & User Management Views ---

def signup(request):
    if request.method == "POST":
        form = EmployeeSignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            name = form.cleaned_data["name"]
            password = form.cleaned_data["password"]

            if not email.endswith("@sky.net"):
                form.add_error("email", "Email must end with @sky.net.")
                return render(request, "signup.html", {"form": form})
>>>>>>> 258c6958b635ef4433de90537cf2e114713c8e91

            try:
                employee = Employee.objects.get(email=email)

                if employee.registered:
<<<<<<< HEAD
                    form.add_error(None, 'You have already registered. Please log in.')
                    return render(request, 'signup.html', {'form': form})

=======
                    form.add_error(None, "You have already registered. Please log in.")
                    return render(request, "signup.html", {"form": form})
>>>>>>> 258c6958b635ef4433de90537cf2e114713c8e91

                employee.name = name
                employee.set_password(password)
                employee.registered = True
                employee.save()

<<<<<<< HEAD
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
=======
                messages.success(request, "Registration successful. You can now log in.")
                return redirect("login")

            except Employee.DoesNotExist:
                form.add_error(None, "No employee account with this email. Contact your admin.")
                return render(request, "signup.html", {"form": form})

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmployeeSignupForm()

    return render(request, "signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")
>>>>>>> 258c6958b635ef4433de90537cf2e114713c8e91

        try:
            employee = Employee.objects.get(email=email)

<<<<<<< HEAD
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
                    return redirect('healthcheck')  # adjust if needed
                elif role == 'seniormanager':
                    return redirect('org_summary')   # adjust if needed
                elif role == 'engineer':
                    return redirect('engineer')   # adjust if needed
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


=======
            if not employee.email.endswith("@sky.net"):
                messages.error(request, "Invalid email domain.")
                return redirect("login")

            if not employee.registered:
                messages.error(request, "Employee is not registered yet.")
                return redirect("login")

            if employee.check_password(password):
                # Set session variables upon successful login
                request.session["logged_in_email"] = employee.email
                request.session["role"] = employee.role
                request.session["employee_id"] = employee.id # Store employee ID in session
                logger.info(f"Employee {employee.id} logged in successfully.")
                messages.success(request, "Login successful.")

                # Redirect to the next page if specified, otherwise to home
                next_url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
                logger.info(f"Redirecting logged in user to: {next_url}")
                return redirect(next_url)

            else:
                logger.warning(f"Incorrect password attempt for email: {email}")
                messages.error(request, "Incorrect password.")
                return redirect("login")

        except Employee.DoesNotExist:
            logger.warning(f"Login attempt for non-existent email: {email}")
            messages.error(request, "No employee found with that email.")
            return redirect("login")

    return render(request, "login.html")

# --- Core Application Views ---

@employee_login_required
def home_view(request):
    employee_id = request.session.get("employee_id")
    try:
        employee = Employee.objects.get(id=employee_id)
        return render(request, "home.html", {
            "name": employee.name,
            "role": employee.role,
        })
    except Employee.DoesNotExist:
        logger.error(f"Session error: Employee ID {employee_id} not found in home_view.")
        messages.error(request, "Session error. Please log in again.")
        request.session.flush()
        return redirect("login")

@employee_login_required
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

@employee_login_required
def healthcard_questions_vote(request, healthcard_id):
    """
    View for displaying and processing questions for a specific HealthCard.
    This view has been modified to expose errors rather than silently redirecting.
    """
    employee_id = request.session.get("employee_id")
    logger.info(f"Entering healthcard_questions_vote for employee {employee_id}, healthcard {healthcard_id}")
    
    # Get the employee
    employee = get_object_or_404(Employee, id=employee_id)
    logger.info(f"Found employee: {employee.email}")
    
    # Get the healthcard
    healthcard = get_object_or_404(HealthCard, id=healthcard_id)
    logger.info(f"Found healthcard: {healthcard.card_name}")
    
    # Get questions for this healthcard
    questions = Question.objects.filter(healthcard=healthcard).order_by("id")
    logger.info(f"Found {questions.count()} questions for healthcard {healthcard_id}")
    
    # Check if employee has permission to vote
    if employee.role not in ["engineer", "teamleader"]:
        logger.warning(f"Permission denied for employee {employee_id} (role: {employee.role}) to vote on healthcard {healthcard_id}")
        messages.error(request, "You don't have permission to vote.")
        return redirect("healthcard-list")

    # Check if employee is in the correct team
    if str(healthcard.team.teamId) != str(employee.teamnumber):
        logger.warning(f"Team mismatch: Employee {employee_id} (team: {employee.teamnumber}) cannot vote on healthcard {healthcard_id} (team: {healthcard.team.teamId})")
        messages.error(request, "You can only vote on healthcards for your team.")
        return redirect("healthcard-list")

    # Check if employee has already answered questions for this healthcard
    existing_answers = Answer.objects.filter(employee=employee, question__healthcard=healthcard)
    if existing_answers.exists():
        logger.info(f"Employee {employee_id} already answered questions for healthcard {healthcard_id}. Redirecting.")
        messages.info(request, f"You have already submitted answers for {healthcard.card_name}.")
        return redirect("healthcard-list")

    # Process form submission
    if request.method == "POST":
        logger.info(f"Processing POST request for healthcard {healthcard_id} from employee {employee_id}")
        answers_data = {}
        valid_submission = True
        
        for question in questions:
            answer_key = f"answer_q_{question.id}"
            answer_value = request.POST.get(answer_key)
            
            if not answer_value or answer_value not in dict(Answer.TRAFFIC_LIGHT_CHOICES):
                logger.warning(f"Invalid or missing answer for question {question.id} from employee {employee_id}")
                valid_submission = False
                messages.error(request, f"Please select an answer for all questions. Missing or invalid answer for: '{question.text[:50]}...'")
                break
                
            answers_data[question.id] = answer_value

        if valid_submission:
            logger.info(f"Submission is valid for healthcard {healthcard_id} from employee {employee_id}. Saving answers.")
            try:
                with transaction.atomic():
                    for question_id, traffic_light_value in answers_data.items():
                        question = Question.objects.get(id=question_id)
                        Answer.objects.create(
                            employee=employee,
                            question=question,
                            traffic_light=traffic_light_value,
                            created_at=timezone.now()
                        )
                logger.info(f"Successfully saved answers for healthcard {healthcard_id} from employee {employee_id}")
                messages.success(request, f"Your answers for '{healthcard.card_name}' have been submitted successfully!")
                return redirect("healthcard-list")
            except Exception as e:
                logger.exception(f"Error saving answers for healthcard {healthcard_id} from employee {employee_id}: {e}")
                messages.error(request, f"An error occurred while saving your answers: {e}")
                # Let the error propagate to show the actual error page instead of redirecting
                raise
        
        # Re-render form if validation failed
        logger.warning(f"Invalid submission for healthcard {healthcard_id} from employee {employee_id}. Re-rendering form.")
        return render(request, "vote/question_vote.html", {
            "healthcard": healthcard,
            "questions": questions,
            "employee": employee,
            "submitted_data": request.POST
        })

    # GET request - render the form
    logger.info(f"Rendering questions page for healthcard {healthcard_id} for employee {employee_id}")
    
    # IMPORTANT: Let any errors propagate to show the actual error page
    # This will help diagnose the issue instead of silently redirecting
    return render(request, "vote/question_vote.html", {
        "healthcard": healthcard,
        "questions": questions,
        "employee": employee
    })

# --- Admin & Department Views ---

@employee_login_required
def admin_page(request):
    employee_id = request.session.get("employee_id")
    try:
        employee = Employee.objects.get(id=employee_id)
        if employee.role != "admin":
            messages.error(request, "Access Denied.")
            return redirect("home")
    except Employee.DoesNotExist:
        logger.error(f"Session error: Employee ID {employee_id} not found in admin_page.")
        messages.error(request, "Authentication error.")
        request.session.flush()
        return redirect("login")
        
    if request.method == "POST":
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            new_employee = form.save(commit=False)
            new_employee.registered = False
            new_employee.save()
            messages.success(request, "User created successfully. They need to register.")
            return redirect("admin_page")
    else:
        form = AdminUserCreationForm()
    
    employees = Employee.objects.all()
    return render(request, "adminpage.html", {"form": form, "employees": employees})

@employee_login_required
def department_hub_view(request):
    messages.info(request, "Department Hub view is under construction.")
    return redirect("home")

@employee_login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, "department_list.html", {"departments": departments})

@employee_login_required
>>>>>>> 258c6958b635ef4433de90537cf2e114713c8e91
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
<<<<<<< HEAD
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


def engineer_hub_view(request):
    return render(request, 'engineer.html')


def healthcard_list(request):
    # Fetch all HealthCard objects from the database
    healthcards = HealthCard.objects.all()  # This will get all health cards

    # Pass the healthcards to the template
    return render(request, 'healthcards/healthcard_list.html', {
        'healthcards': healthcards
    })
# @login_required
# def vote_on_healthcard(request, healthcard_id):
#     # Fetch the health card by its ID
#     healthcard = get_object_or_404(HealthCard, id=healthcard_id)
    
#     # Fetch all the questions related to this health card
#     questions = Question.objects.filter(healthcard=healthcard)
    
#     # Ensure the user has permission to vote (e.g., Engineer or Team Leader)
#     if request.user.role not in ['engineer', 'teamleader']:
#         return redirect('unauthorized')  # Redirect to an unauthorized page if they can't vote

#     # If the request is POST (the user is submitting their vote)
#     if request.method == 'POST':
#         # Handle form submission
#         for question in questions:
#             selected_answer = request.POST.get(f'card{healthcard_id}-q{question.id}')
#             if selected_answer:
#                 # Avoid duplicate votes from the same user
#                 if not Vote.objects.filter(question=question, user=request.user).exists():
#                     Vote.objects.create(question=question, value=selected_answer, user=request.user)

#         return render(request, 'thank_you.html')

#     # If it's a GET request, display the voting form
#     return render(request, 'vote/voting.html', {'healthcard': healthcard, 'questions': questions})

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

def healthcard_vote(request, card_id):
    healthcard = get_object_or_404(HealthCard, id=card_id)
    return render(request, 'vote/voting.html', {'healthcard': healthcard})

def healthcard_terms(request, card_id):
    healthcard = get_object_or_404(HealthCard, id=card_id)
    context = {
        'healthcard': healthcard,
        'user_has_accepted_terms': False  # Always false initially
    }
    return render(request, 'vote/terms_and_condi.html', context)
=======
        return redirect("department-list")
    return render(request, "department_form.html", {"form": form})

@employee_login_required
def engineer_hub_view(request):
    messages.info(request, "Engineer Hub view is under construction.")
    return redirect("home")

# --- Old/Potentially Redundant Views ---

@employee_login_required
def healthcard_vote(request, healthcard_id):
    # This view is now just a redirect to the questions view
    return redirect("healthcard_questions_vote", healthcard_id=healthcard_id)

@employee_login_required
def healthcard_terms(request, healthcard_id):
    try:
        healthcard = get_object_or_404(HealthCard, id=healthcard_id)
        logger.info(f"Rendering terms page for healthcard {healthcard_id}, name: {healthcard.card_name}")
        
        # Check if there are questions for this healthcard
        question_count = Question.objects.filter(healthcard=healthcard).count()
        logger.info(f"Healthcard {healthcard_id} has {question_count} questions")
        
        if question_count == 0:
            logger.warning(f"No questions found for healthcard {healthcard_id}")
            messages.warning(request, f"There are no questions available for {healthcard.card_name}. Please contact an administrator.")
            return redirect("healthcard-list")
            
        context = {
            "healthcard": healthcard,
            "user_has_accepted_terms": False
        }
        return render(request, "vote/terms_and_condi.html", context)
    except Exception as e:
        logger.exception(f"Error in healthcard_terms view: {e}")
        # Let the error propagate to show the actual error page
        raise

# --- Helper/Utility Views ---

@employee_login_required
def thank_you_page(request):
    return render(request, "vote/thank_you.html")
>>>>>>> 258c6958b635ef4433de90537cf2e114713c8e91
