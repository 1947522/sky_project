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
