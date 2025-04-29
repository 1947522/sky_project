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

            try:
                employee = Employee.objects.get(email=email)

                if employee.registered:
                    form.add_error(None, "You have already registered. Please log in.")
                    return render(request, "signup.html", {"form": form})

                employee.name = name
                employee.set_password(password)
                employee.registered = True
                employee.save()

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

        try:
            employee = Employee.objects.get(email=email)

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
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
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
