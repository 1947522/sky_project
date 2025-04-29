from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password

class Employee(models.Model):
    roles = [
        ('engineer', 'Engineer'),
        ('teamleader', 'Team Leader'),
        ('departmentleader', 'Department Leader'),
        ('seniormanager', 'Senior Manager'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    teamnumber = models.CharField(max_length=50)
    departmentnumber = models.CharField(max_length=50)
    registered = models.BooleanField(default=False)
    password = models.CharField(max_length=128, blank=True)
    role = models.CharField(max_length=20, choices=roles, default='engineer')


    def clean(self):
        if not self.email.endswith('@sky.net'):
            raise ValidationError('Email must end with @sky.net')
        super().clean()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email
    
class Department(models.Model):
    departmentId = models.AutoField(primary_key=True)
    departmentName = models.CharField(max_length=100)

    def __str__(self):
        return self.departmentName

    def get_department_details(self):
        return {
            'id': self.departmentId,
            'name': self.departmentName
        }

    def set_department_details(self, name):
        self.departmentName = name
        self.save()

    def assigned_teams(self):
        return self.team_set.all()  
class Team(models.Model):
    teamId = models.AutoField(primary_key=True)
    teamName = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.teamName
    
class HealthCard(models.Model):
    # Card Information
    card_name = models.CharField(max_length=100, unique=True)  # e.g., "Delivering Value"
    
    # Relationships
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='healthcards')  # One team can have many health cards
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='healthcards')  # One department can have many health cards

    def __str__(self):
        return self.card_name
    
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

class Vote(models.Model):
    TRAFFIC_LIGHT_CHOICES = [
        ('Red', '🔴 Red'),
        ('Yellow', '🟡 Yellow'),
        ('Green', '🟢 Green'),
    ]

    PROGRESS_CHOICES = [
        ('Stable', 'Stable'),
        ('Improving', 'Improving'),
        ('Getting worse', 'Getting worse'),
    ]

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='votes')
    healthcard = models.ForeignKey('HealthCard', on_delete=models.CASCADE, related_name='votes')
    traffic_light = models.CharField(max_length=6, choices=TRAFFIC_LIGHT_CHOICES)
    progress = models.CharField(max_length=20, choices=PROGRESS_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Add a field to track if this vote was created from question answers
    is_from_questions = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.name} - {self.healthcard.card_name} - {self.traffic_light} ({self.progress})"
