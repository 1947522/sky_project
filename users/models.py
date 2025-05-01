from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
#https://docs.djangoproject.com/en/3.0/topics/db/models/
#https://docs.djangoproject.com/en/5.1/ref/contrib/auth/
#https://stackoverflow.com/questions/2432489/django-overwrite-form-clean-method
#vinicius and Shoaibs work
class Employee(models.Model):
    roles = [
        #creates all the fields in the table called employee
        ('engineer', 'Engineer'),
        ('teamleader', 'Team Leader'),
        ('departmentleader', 'Department Leader'),
        ('seniormanager', 'Senior Manager'),
        ('admin', 'Admin'),
    ]
#different attributes
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    teamnumber = models.CharField(max_length=50)
    departmentnumber = models.CharField(max_length=50)
    registered = models.BooleanField(default=False)
    password = models.CharField(max_length=128, blank=True)
    role = models.CharField(max_length=20, choices=roles, default='engineer')


    def clean(self):
        #validation error for ending with @sky.net
        if not self.email.endswith('@sky.net'):
            raise ValidationError('Email must end with @sky.net')
        #calls parent class clean
        super().clean()

    def set_password(self, raw_password):
        #hashingf of plain text password. sotred in models
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        #returns tryue if hashed and unhashed are the same
        return check_password(raw_password, self.password)

    def __str__(self):
        #object is then represented as a string. makes it readable/legible
        return self.email
# Sheroz's work    
class Department(models.Model):
    # Auto-incrementing primary key for the department
    departmentId = models.AutoField(primary_key=True)
    # Name of the department, limited to 100 characters
    departmentName = models.CharField(max_length=100)

    # String representation of the Department object
    def __str__(self):
        # Returns the department name when the object is converted to a string
        return self.departmentName

    # Method to retrieve department details as a dictionary
    def get_department_details(self):
        return {
            'id': self.departmentId,  # Department ID
            'name': self.departmentName  # Department name
        }

    # Method to update the department name and save the changes
    def set_department_details(self, name):
        self.departmentName = name  # Update the department name
        self.save()  # Save the changes to the database

    # Method to retrieve all teams assigned to this department
    def assigned_teams(self):
        return self.team_set.all()  # Returns a queryset of all related Team objects
# Sheroz's work  
class Team(models.Model):
    teamId = models.AutoField(primary_key=True)
    teamName = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.teamName

# Sheroz's work   
class HealthCard(models.Model):
    # Card Information
    # Name of the health card, limited to 100 characters, and must be unique
    card_name = models.CharField(max_length=100, unique=True)  # e.g., "Delivering Value"

    # Relationships
    # Foreign key linking the health card to a team
    # If the team is deleted, all associated health cards will also be deleted (CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='healthcards')  # One team can have many health cards
    # Foreign key linking the health card to a department
    # If the department is deleted, all associated health cards will also be deleted (CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='healthcards')  # One department can have many health cards

    # String representation of the HealthCard object
    def __str__(self):
        # Returns the card name when the object is converted to a string
        return self.card_name
#Anes's work   
class Question(models.Model):
    healthcard = models.ForeignKey('HealthCard', on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()  # The question itself

    # Traffic light descriptions for each question
    red_description = models.TextField()
    yellow_description = models.TextField()
    green_description = models.TextField()

    def __str__(self):

        return f"Question for {self.healthcard.card_name}: {self.text[:50]}..."

class Answer(models.Model):
    TRAFFIC_LIGHT_CHOICES = [
        ('Red', '🔴 Red'),
        ('Yellow', '🟡 Yellow'),
        ('Green', '🟢 Green'),
    ]

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    traffic_light = models.CharField(max_length=6, choices=TRAFFIC_LIGHT_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('employee', 'question')  # Each employee can answer each question only once
        
    def __str__(self):
        return f"{self.employee.name} - {self.question.healthcard.card_name} - Q: {self.question.text[:30]}... - {self.traffic_light}"

# Sheroz's work
class Vote(models.Model):
    # Choices for the traffic light field
    TRAFFIC_LIGHT_CHOICES = [
        ('Red', '🔴 Red'),  # Red indicates a critical issue
        ('Yellow', '🟡 Yellow'),  # Yellow indicates a warning
        ('Green', '🟢 Green'),  # Green indicates everything is fine
    ]

    # Choices for the progress field
    PROGRESS_CHOICES = [
        ('Stable', 'Stable'),  # Indicates no change in the situation
        ('Improving', 'Improving'),  # Indicates the situation is getting better
        ('Getting worse', 'Getting worse'),  # Indicates the situation is deteriorating
    ]

    # Foreign key linking the vote to an employee
    # If the employee is deleted, all associated votes will also be deleted (CASCADE)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='votes')
    # Foreign key linking the vote to a health card
    # If the health card is deleted, all associated votes will also be deleted (CASCADE)
    healthcard = models.ForeignKey('HealthCard', on_delete=models.CASCADE, related_name='votes')
    # Foreign key linking the vote to a specific question
    # If the question is deleted, all associated votes will also be deleted (CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='votes')

    # Field to store the traffic light choice
    traffic_light = models.CharField(max_length=6, choices=TRAFFIC_LIGHT_CHOICES)
    # Field to store the progress choice (optional)
    progress = models.CharField(max_length=20, choices=PROGRESS_CHOICES, blank=True, null=True)
    # Field to store the user's comment (optional)
    comment = models.TextField(blank=True)
    # Field to store actions the team can take (optional)
    actions = models.TextField(blank=True)
    # Field to store the proposed solution (optional)
    solution = models.TextField(blank=True)
    # Field to store the timestamp when the vote was created
    created_at = models.DateTimeField(default=timezone.now)

    # String representation of the Vote object
    def __str__(self):
        # Returns a formatted string with employee name, health card name, question text, and traffic light choice
        return f"{self.employee.name} - {self.healthcard.card_name} - Q: {self.question.text[:30]} - {self.traffic_light}"

#vinicius and Shoaibs work
class VotingSession(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    #automatically sets to current time stamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #controls how votingsession is to be displayed
        return f"{self.name} ({self.start_date} - {self.end_date})"

# Sheroz's work
class HealthCardTermsAcceptance(models.Model):
    # Foreign key linking the acceptance record to an employee
    # If the employee is deleted, all associated acceptance records will also be deleted (CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    # Foreign key linking the acceptance record to a health card
    # If the health card is deleted, all associated acceptance records will also be deleted (CASCADE)
    healthcard = models.ForeignKey(HealthCard, on_delete=models.CASCADE)
    # Boolean field indicating whether the terms of the health card have been accepted
    accepted = models.BooleanField(default=False)

    class Meta:
        # Ensures that each employee can only accept the terms for a specific health card once
        unique_together = ('employee', 'healthcard')