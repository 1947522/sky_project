from django import forms
from .models import Employee, Department, Vote, VotingSession

#vinicius and Shoaibs work
class EmployeeSignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    #uses widget to hide password in the text box
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        # builtin django method for validation
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        #check if passwords match
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
#https://docs.djangoproject.com/en/5.0/ref/models/options/
#https://stackoverflow.com/questions/74925082/what-does-class-meta-do-in-django-and-django-rest-framework
#vinicius and Shoaibs work
class AdminUserCreationForm(forms.ModelForm):
    class Meta:
        #shows which model this form will be using
        model = Employee
        #all the fields fdrom that model
        fields = ['name', 'email', 'teamnumber', 'departmentnumber', 'role']
#Anes's work
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['departmentName']
# Sheroz's work
# This form is used for submitting votes on health cards.
class VoteForm(forms.ModelForm):
    class Meta:
        # Specifies the model that this form is based on
        model = Vote
        # Specifies the fields from the model to include in the form
        fields = ['traffic_light', 'progress', 'comment']
        # Customizes the widgets for the form fields
        widgets = {
            'traffic_light': forms.RadioSelect,  # Displays traffic_light as radio buttons
            'progress': forms.Select,  # Displays progress as a dropdown menu
            'comment': forms.Textarea(attrs={
                'rows': 2,  # Sets the number of rows for the textarea
                'placeholder': 'Optional comment...'  # Adds a placeholder text for the comment field
            })
        }
#vinicius work
class VotingSessionForm(forms.ModelForm):
    class Meta:
        #shows which model this form will be using
        model = VotingSession
        fields = ['name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.SelectDateWidget(),
            'end_date': forms.SelectDateWidget(),
        }