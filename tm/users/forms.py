from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации"""
    email = forms.EmailField(required=True, label="Электронная почта")
    display_name = forms.CharField(
        max_length=100,
        required=False,
        label="Отображаемое имя"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'display_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с такой почтой уже зарегистрирован.")
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(label="Имя пользователя или email")


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""
    class Meta:
        model = CustomUser
        fields = ['display_name', 'first_name', 'last_name', 'bio', 'avatar', 'phone']
        labels = {
            'display_name': 'Отображаемое имя',
            'bio': 'О себе',
            'avatar': 'Аватар',
            'phone': 'Телефон',
        }