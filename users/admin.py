from django.contrib import admin

from .models import Employee, VotingSession

admin.site.register(Employee)
admin.site.register(VotingSession)