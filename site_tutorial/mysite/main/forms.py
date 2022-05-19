from django import forms
from .models import Profile, Friend_Request
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

        def save(self, commit=True):
            user = super(NewUserForm, self).save(commit=False)
            user.email = self.cleaned_data["email"]
            if commit:
                user.save()
            return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('spotify_username',)


class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend_Request
        fields = ['from_user', 'to_user']
