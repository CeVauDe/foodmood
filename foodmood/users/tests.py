from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from .views import CustomUserCreationForm, LoginForm


class CustomUserCreationFormTests(TestCase):
    """Test the custom user registration form"""

    def test_form_with_valid_data(self) -> None:
        """Test form with all valid data"""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_requires_email(self) -> None:
        """Test that email field is required"""
        form_data = {
            "username": "testuser",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
            # Missing email
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_password_mismatch(self) -> None:
        """Test form with mismatched passwords"""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "complexpassword123",
            "password2": "differentpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_invalid_email(self) -> None:
        """Test form with invalid email format"""
        form_data = {
            "username": "testuser",
            "email": "not-an-email",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_username_too_long(self) -> None:
        """Test form with username longer than 35 characters"""
        long_username = "a" * 36  # 36 characters, exceeds the 35 limit
        form_data = {
            "username": long_username,
            "email": "test@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        # Check that the error message mentions the character limit
        username_errors = form.errors["username"]
        self.assertTrue(any("35" in str(error) for error in username_errors))

    def test_form_username_max_length_valid(self) -> None:
        """Test form with username at exactly 35 characters (should be valid)"""
        max_length_username = "a" * 35  # Exactly 35 characters
        form_data = {
            "username": max_length_username,
            "email": "test@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_saves_user_with_email(self) -> None:
        """Test that form saves user with email"""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("complexpassword123"))


class LoginFormTests(TestCase):
    """Test the login form"""

    def test_form_with_valid_data(self) -> None:
        """Test form with valid username and password"""
        form_data = {"username": "testuser", "password": "testpassword123"}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_requires_username(self) -> None:
        """Test that username field is required"""
        form_data = {
            "password": "testpassword123"
            # Missing username
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_form_requires_password(self) -> None:
        """Test that password field is required"""
        form_data = {
            "username": "testuser"
            # Missing password
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)


class UserRegistrationViewTests(TestCase):
    """Test the user registration view"""

    def setUp(self) -> None:
        self.client = Client()
        self.register_url = reverse("users:register")

    def test_registration_view_get(self) -> None:
        """Test GET request to registration page"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")
        self.assertContains(response, "username")
        self.assertContains(response, "email")
        self.assertContains(response, "password1")
        self.assertContains(response, "password2")

    def test_successful_registration(self) -> None:
        """Test successful user registration"""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        response = self.client.post(self.register_url, form_data)

        # Check user was created
        self.assertTrue(User.objects.filter(username="newuser").exists())
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")

        # Check user is logged in
        self.assertTrue("_auth_user_id" in self.client.session)

        # Check redirect to home
        self.assertRedirects(response, reverse("index"))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Account created for newuser", str(messages[0]))

    def test_registration_with_existing_username(self) -> None:
        """Test registration with already existing username"""
        # Create existing user
        User.objects.create_user(username="existinguser", email="existing@example.com")

        form_data = {
            "username": "existinguser",  # Same username
            "email": "different@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        response = self.client.post(self.register_url, form_data)

        # Should not create new user
        self.assertEqual(User.objects.filter(username="existinguser").count(), 1)

        # Should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists")

    def test_registration_with_invalid_data(self) -> None:
        """Test registration with invalid form data"""
        form_data = {
            "username": "testuser",
            "email": "invalid-email",  # Invalid email
            "password1": "complexpassword123",
            "password2": "differentpassword123",  # Mismatched password
        }
        response = self.client.post(self.register_url, form_data)

        # Should not create user
        self.assertFalse(User.objects.filter(username="testuser").exists())

        # Should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")


class UserLoginViewTests(TestCase):
    """Test the user login view"""

    def setUp(self) -> None:
        self.client = Client()
        self.login_url = reverse("users:login")
        # Create test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )

    def test_login_view_get(self) -> None:
        """Test GET request to login page"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome Back")
        self.assertContains(response, "username")
        self.assertContains(response, "password")

    def test_successful_login(self) -> None:
        """Test successful user login"""
        form_data = {"username": "testuser", "password": "testpassword123"}
        response = self.client.post(self.login_url, form_data)

        # Check user is logged in
        self.assertTrue("_auth_user_id" in self.client.session)

        # Check redirect to home
        self.assertRedirects(response, reverse("index"))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Welcome back, testuser", str(messages[0]))

    def test_login_with_invalid_credentials(self) -> None:
        """Test login with wrong password"""
        form_data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, form_data)

        # Should not be logged in
        self.assertFalse("_auth_user_id" in self.client.session)

        # Should show login form again
        self.assertEqual(response.status_code, 200)

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Invalid username or password", str(messages[0]))

    def test_login_with_nonexistent_user(self) -> None:
        """Test login with non-existent username"""
        form_data = {"username": "nonexistent", "password": "somepassword"}
        response = self.client.post(self.login_url, form_data)

        # Should not be logged in
        self.assertFalse("_auth_user_id" in self.client.session)

        # Should show error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Invalid username or password", str(messages[0]))


class UserLogoutViewTests(TestCase):
    """Test the user logout view"""

    def setUp(self) -> None:
        self.client = Client()
        self.logout_url = reverse("users:logout")
        # Create and login test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )
        self.client.login(username="testuser", password="testpassword123")

    def test_logout_logged_in_user(self) -> None:
        """Test logout for logged in user"""
        # Verify user is logged in
        self.assertTrue("_auth_user_id" in self.client.session)

        response = self.client.get(self.logout_url)

        # Check user is logged out
        self.assertFalse("_auth_user_id" in self.client.session)

        # Check redirect to home
        self.assertRedirects(response, reverse("index"))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("You have been successfully logged out", str(messages[0]))

    def test_logout_anonymous_user(self) -> None:
        """Test logout for anonymous user"""
        # Logout first
        self.client.logout()

        response = self.client.get(self.logout_url)

        # Should still redirect to home
        self.assertRedirects(response, reverse("index"))

        # Should still show success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("You have been successfully logged out", str(messages[0]))


class NavigationIntegrationTests(TestCase):
    """Test navigation and template integration"""

    def setUp(self) -> None:
        self.client = Client()
        self.home_url = reverse("index")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )

    def test_anonymous_user_navigation(self) -> None:
        """Test navigation for anonymous users"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

        # Should show login and register buttons
        self.assertContains(response, "Login")
        self.assertContains(response, "Register")

        # Should not show profile dropdown
        self.assertNotContains(response, "bi-person-fill")

    def test_authenticated_user_navigation(self) -> None:
        """Test navigation for authenticated users"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

        # Should show profile icon
        self.assertContains(response, "bi-person-fill")
        self.assertContains(response, "testuser")

        # Should not show login/register buttons
        self.assertNotContains(response, "Login")
        self.assertNotContains(response, "Register")

    def test_complete_user_flow(self) -> None:
        """Test complete user registration -> login -> logout flow"""
        # 1. Register new user
        register_data = {
            "username": "flowuser",
            "email": "flow@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        response = self.client.post(reverse("users:register"), register_data)

        # Should be redirected and logged in
        self.assertRedirects(response, self.home_url)
        self.assertTrue("_auth_user_id" in self.client.session)

        # 2. Check home page shows authenticated state
        response = self.client.get(self.home_url)
        self.assertContains(response, "flowuser")

        # 3. Logout
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(response, self.home_url)
        self.assertFalse("_auth_user_id" in self.client.session)

        # 4. Check home page shows anonymous state
        response = self.client.get(self.home_url)
        self.assertContains(response, "Login")
        self.assertContains(response, "Register")
