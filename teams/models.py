from django.db import models

# Create your models here.
# Create your models here.
class Department(models.Model):
    DepartmentID = models.AutoField(primary_key=True)  # ID for Department
    DepartmentName = models.CharField(max_length=255, unique=True, null=False)  # Unique name for Department

    def __str__(self):
        return self.DepartmentName


class Team(models.Model):
    TeamID = models.AutoField(primary_key=True)  # ID for a team
    TeamName = models.CharField(max_length=255, unique=True, null=False)  # Unique name for a Team

    def __str__(self):
        return self.TeamName


class DepartmentLeader(models.Model):
    UserID = models.AutoField(primary_key=True)  # Unique ID for DepartmentLeader
    Name = models.CharField(max_length=255, null=False)  # Full name of DepartmentLeader
    Username = models.CharField(max_length=255, unique=True, null=False)  # Unique Username
    Email = models.EmailField(unique=True, null=False)  # Unique email
    Password = models.CharField(max_length=255, null=False)  # Hashed Password
    Role = models.CharField(max_length=255, null=False)  # Role of DepartmentLeader
    # LoginID = models.ForeignKey(
    #     'Login', on_delete=models.SET_NULL, null=True, blank=True
    # )  # Foreign key to Login
    TeamID = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True
    )  # Foreign key to Team
    DepartmentID = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )  # Foreign key to Department

    def __str__(self):
        return self.Name