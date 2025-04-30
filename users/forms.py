from django import forms
from .models import Employee, Department, Vote, VotingSession


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

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['departmentName']

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['traffic_light', 'progress', 'comment']
        widgets = {
            'traffic_light': forms.RadioSelect,
            'progress': forms.Select,
            'comment': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional comment...'})
        }

class VotingSessionForm(forms.ModelForm):
    class Meta:
        model = VotingSession
        fields = ['name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.SelectDateWidget(),
            'end_date': forms.SelectDateWidget(),
        }