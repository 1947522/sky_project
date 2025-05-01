from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib import messages

from .forms import VotingSessionForm
from .models import Employee, Department, Team, HealthCard, Question, Answer, Vote, VotingSession
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError

#MEHDI WORK
class ModelTests(TestCase):
    def test_employee_creation(self):
        employee = Employee.objects.create(
            email="test@sky.net",
            name="Test User",
            role="engineer",
            teamnumber="1",
            departmentnumber="1",
            registered=True
        )
        employee.set_password("testpass123")
        employee.save()

        self.assertEqual(employee.__str__(), "test@sky.net")
        self.assertTrue(employee.check_password("testpass123"))
        self.assertFalse(employee.check_password("wrongpass"))

    def test_employee_email_validation(self):
        with self.assertRaises(ValidationError):
            employee = Employee(email="invalid@gmail.com", name="Test")
            employee.full_clean()

class SignupViewTests(TestCase):
    def setUp(self):
        # Create test users with all required fields
        self.unregistered_user = Employee.objects.create(
            email='unregistered@sky.net',
            name='Temp User',
            role='engineer',
            teamnumber='T001',
            departmentnumber='D001',
            registered=False
        )

        self.registered_user = Employee.objects.create(
            email='registered@sky.net',
            name='Registered User',
            role='teamleader',
            teamnumber='T002',
            departmentnumber='D002',
            registered=True
        )

        self.signup_url = reverse('signup')

    def test_signup_page_loads(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
        self.assertTemplateUsed(response, 'signup.html')

    def test_successful_signup(self):
        data = {
            'name': 'New User',
            'email': 'unregistered@sky.net',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }

        response = self.client.post(self.signup_url, data, follow=True)

        # Check redirect and messages
        self.assertRedirects(response, reverse('login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Registration successful' in str(m) for m in messages))

        # Verify database updates
        user = Employee.objects.get(email='unregistered@sky.net')
        self.assertTrue(user.registered)
        self.assertEqual(user.name, 'New User')

    def test_invalid_email_domain(self):
        """Test registration with non-@sky.net email"""
        data = {
            'name': 'Invalid User',
            'email': 'invalid@gmail.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }

        response = self.client.post(self.signup_url, data)

        # Check form errors in context
        form = response.context['form']
        self.assertTrue(form.has_error('email'))
        self.assertIn('Email must end with @sky.net.', form.errors['email'])

    def test_already_registered_user(self):
        data = {
            'name': 'Duplicate User',
            'email': 'registered@sky.net',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }

        response = self.client.post(self.signup_url, data)
        # Check form non-field errors
        form = response.context['form']
        self.assertTrue(form.non_field_errors())
        self.assertIn('You have already registered. Please log in.', form.non_field_errors())

    def test_unregistered_employee(self):
        data = {
            'name': 'Unknown User',
            'email': 'unknown@sky.net',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }

        response = self.client.post(self.signup_url, data)
        # Check form non-field errors
        form = response.context['form']
        self.assertTrue(form.non_field_errors())
        self.assertIn('No employee account with this email. Contact your admin.', form.non_field_errors())

    def test_missing_required_fields(self):
        invalid_data = [
            {'name': '', 'email': 'test@sky.net', 'password': 'pass', 'confirm_password': 'pass'},
            {'name': 'Test', 'email': '', 'password': 'pass', 'confirm_password': 'pass'},
            {'name': 'Test', 'email': 'test@sky.net', 'password': '', 'confirm_password': ''},
        ]

        for data in invalid_data:
            response = self.client.post(self.signup_url, data)
            # Check messages framework for generic error
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any('Please correct the errors below' in str(m) for m in messages))

    def test_password_mismatch(self):
        data = {
            'name': 'New User',
            'email': 'unregistered@sky.net',
            'password': 'securepass123',
            'confirm_password': 'differentpass'
        }

        response = self.client.post(self.signup_url, data)

        # Check form errors in context
        form = response.context['form']

        # Verify confirm_password field has error
        self.assertIn('confirm_password', form.errors)
        self.assertIn('Passwords do not match', str(form.errors['confirm_password']))

        # Also check messages framework
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Please correct the errors below' in str(m) for m in messages))



class AuthViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Employee.objects.create(
            email="user@sky.net",
            name="Test User",
            role="engineer",
            registered=True
        )
        self.user.set_password("testpass123")
        self.user.save()

    def test_successful_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'user@sky.net',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.client.session['logged_in_email'], 'user@sky.net')

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'user@sky.net',
            'password': 'wrongpass'
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Incorrect password.')

    def test_invalid_email_domain(self):
        """Test login with email that doesn't match @sky.net domain"""
        # Create a test user with invalid email but bypass validation
        invalid_user = Employee.objects.create(
            email='hacker@gmail.com',  # Invalid domain
            name='Hacker',
            role='engineer',
            registered=True
        )
        # Bypass model validation to save invalid email
        Employee.objects.filter(pk=invalid_user.pk).update(email='hacker@gmail.com')

        response = self.client.post(reverse('login'), {
            'username': 'hacker@gmail.com',
            'password': 'anypassword'
        }, follow=True)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Invalid email domain.')

        # Check session wasn't created
        self.assertNotIn('logged_in_email', self.client.session)




class AdminViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Employee.objects.create(
            email="admin@sky.net",
            name="Admin",
            role="admin",
            registered=True
        )
        self.admin.set_password("adminpass123")
        self.admin.save()
        self.client.login(email='admin@sky.net', password='adminpass123')

    def test_user_deletion(self):
        user_to_delete = Employee.objects.create(email="delete@sky.net")
        response = self.client.post(reverse('delete_users_admin'), {'email': 'delete@sky.net'})
        self.assertFalse(Employee.objects.filter(email='delete@sky.net').exists())




class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create user with all required fields
        self.user = Employee.objects.create(
            email="user@sky.net",
            name="Test User",
            role="engineer",
            teamnumber="T001",
            departmentnumber="D001",
            registered=True
        )
        self.user.set_password("testpass123")
        self.user.save()

        # Authenticate properly through your login view
        self.client.post(reverse('login'), {
            'username': 'user@sky.net',
            'password': 'testpass123'
        })

    def test_profile_access(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User")
        self.assertContains(response, "user@sky.net")

    def test_password_display(self):
        response = self.client.get(reverse('profile'))
        self.assertContains(response, "********")


class PasswordRecoveryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@sky.net',
            password='testpassword123'
        )
        self.recovery_request_url = reverse('password_recovery_request')
        self.recovery_confirm_url = reverse('password_recovery_confirm')
        self.login_url = reverse('login')

    def test_password_recovery_request_get(self):
        response = self.client.get(self.recovery_request_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_recovery_request.html')
        self.assertContains(response, 'Account Recovery')

    def test_invalid_email_submission(self):
        response = self.client.post(self.recovery_request_url, {
            'email': 'wrong@sky.net'
        }, follow=True)

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'No account found with that email address')
        self.assertNotIn('recovery_email', self.client.session)

    def test_password_confirm_get_without_session(self):
        response = self.client.get(self.recovery_confirm_url)
        self.assertRedirects(response, self.recovery_request_url)

    def test_password_confirm_get_with_session(self):
        session = self.client.session
        session['recovery_email'] = 'test@sky.net'
        session.save()


        response = self.client.get(self.recovery_confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_recovery_confirm.html')


class CreateSessionTests(TestCase):
    def test_get_request_renders_form(self):

        response = self.client.get(reverse('create_session'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_session.html')
        self.assertIsInstance(response.context['form'], VotingSessionForm)
        self.assertContains(response, 'Create a Voting Session')

    def test_valid_post_creates_session_and_redirects(self):
        data = {
            'name': 'Annual Voting',
            'start_date': '2024-01-01',
            'end_date': '2024-01-07'
        }
        response = self.client.post(reverse('create_session'), data, follow=True)

        self.assertEqual(VotingSession.objects.count(), 1)
        self.assertRedirects(response, reverse('create_session'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Voting session created successfully.')

    def test_invalid_post_shows_error(self):
        data = {
            'name': '',
            'start_date': '2024-01-01',
            'end_date': '2024-01-07'
        }
        response = self.client.post(reverse('create_session'), data, follow=True)
        self.assertEqual(VotingSession.objects.count(), 0)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'There was an error in the form submission.')
class DeleteSessionTests(TestCase):
    def setUp(self):
        self.session = VotingSession.objects.create(
            name='Test Session',
            start_date='2024-01-01',
            end_date='2024-01-07'
        )

    def test_get_request_lists_sessions(self):
        response = self.client.get(reverse('delete_session'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_session.html')
        self.assertContains(response, self.session.name)
        self.assertIn(self.session, response.context['sessions'])

    def test_post_deletes_session_and_shows_success(self):
        response = self.client.post(
            reverse('delete_session'),
            {'name': self.session.name},
            follow=True
        )

        self.assertEqual(VotingSession.objects.count(), 0)
        self.assertRedirects(response, reverse('delete_session'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Voting session deleted successfully.')

    def test_post_invalid_name_shows_error(self):
        response = self.client.post(
            reverse('delete_session'),
            {'name': 'Non-existent Session'},
            follow=True
        )

        self.assertEqual(VotingSession.objects.count(), 1)  # Session still exists

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'No voting session found with that name.')

    def test_post_missing_name_shows_error(self):
        response = self.client.post(reverse('delete_session'), follow=True)
        self.assertEqual(VotingSession.objects.count(), 1)  # Session still exists

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'No name provided.')

class VotingTests(TestCase):
    def setUp(self):
        # Create a test employee and health card
        self.employee = Employee.objects.create(
            email="voter@sky.net",
            name="Voter User",
            role="engineer",
            registered=True
        )
        self.employee.set_password("voterpass123")
        self.employee.save()

        self.healthcard = HealthCard.objects.create(
            card_name="Voting Health Card",
            department=Department.objects.create(departmentName="Voting Department"),
            team=Team.objects.create(teamName="Voting Team")
        )

        # Log in the test employee
        self.client.login(username=self.employee.email, password="voterpass123")

    def test_voting_submission(self):
        # Simulate submitting a vote
        response = self.client.post(reverse('healthcard_vote', args=[self.healthcard.id]), {
            'traffic_light_1': 'Green',
            'progress_1': 'Stable',
            'comment_1': 'Everything is fine.'
        })

        # Check if the vote was successfully submitted
        self.assertEqual(response.status_code, 302)  # Redirect after submission
        self.assertRedirects(response, reverse('healthcard-list'))
        self.assertEqual(Vote.objects.count(), 1)

class HealthCardListTests(TestCase):
    def setUp(self):
        # Create test health cards
        self.healthcard1 = HealthCard.objects.create(card_name="Health Card 1")
        self.healthcard2 = HealthCard.objects.create(card_name="Health Card 2")

    def test_healthcard_list_view(self):
        response = self.client.get(reverse('healthcard-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'healthcards/healthcard_list.html')
        self.assertContains(response, "Health Card 1")
        self.assertContains(response, "Health Card 2")

class HealthCardTermsTests(TestCase):
    def setUp(self):
        # Create a test employee and health card
        self.employee = Employee.objects.create(
            email="test@sky.net",
            name="Test User",
            role="engineer",
            registered=True
        )
        self.employee.set_password("testpass123")
        self.employee.save()

        self.healthcard = HealthCard.objects.create(card_name="Test Health Card")

        # Log in the test employee
        self.client.login(username=self.employee.email, password="testpass123")

    def test_redirect_to_terms_page(self):
        response = self.client.get(reverse('healthcard_terms', args=[self.healthcard.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vote/terms_and_condi.html')
        self.assertContains(response, self.healthcard.card_name)