from django import forms
from .models import Employee


class EmployeeSignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")


class AdminUserCreationForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'teamnumber', 'departmentnumber', 'role']
