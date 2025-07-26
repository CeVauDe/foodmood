from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Account created for {username}! You can now log in."
            )
            login(request, user)  # Automatically log in the user after registration
            return redirect(
                "index"
            )  # Redirect to home page after successful registration
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("index")
