from django import forms
from .models import Employee
from django.core.exceptions import ValidationError


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'teamnumber', 'departmentnumber']

    def clean_teamnumber(self):
        teamnumber = self.cleaned_data['teamnumber']
        if not teamnumber.isdigit():
            raise ValidationError('Team number must only contain numbers.')
        return teamnumber

    def clean_departmentnumber(self):
        departmentnumber = self.cleaned_data['departmentnumber']
        if not departmentnumber.isalnum():
            raise ValidationError('Department number must only contain numbers and letters.')
        return departmentnumber