from django.db import models
from django.core.exceptions import ValidationError
class Employee(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    teamnumber = models.CharField(max_length=50)
    departmentnumber = models.CharField(max_length=50)
    registered = models.BooleanField(default=False)


    def clean(self):
        # Custom validation for email domain
        if not self.email.endswith('@sky.net'):
            raise ValidationError('Email must end with @sky.net')
        super().clean()  # Always call the parent's clean() method

    def __str__(self):
        return self.email

from django.db import models

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



