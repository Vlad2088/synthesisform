from django import forms
from django.contrib.auth.models import User
from .models import Customer
from printerfarm.models import Order


class CustomerRegistrationForm(forms.ModelForm):
    """Форма регистрации: создаёт User + Customer."""
    username = forms.CharField(label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    email = forms.EmailField(required=False, label='Email')

    class Meta:
        model = Customer
        fields = ['name']
        labels = {
            'name': 'Название / ФИО',
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data.get('email', '')
        )
        customer = super().save(commit=False)
        customer.user = user
        if commit:
            customer.save()
        return user


class CustomerProfileForm(forms.ModelForm):
    """Форма редактирования профиля заказчика."""
    email = forms.EmailField(required=False, label='Email')

    class Meta:
        model = Customer
        fields = ['name', 'phone']
        labels = {
            'name': 'Название / ФИО',
            'phone': 'Телефон',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        customer = super().save(commit=commit)
        if 'email' in self.cleaned_data:
            customer.user.email = self.cleaned_data['email']
            customer.user.save()
        return customer


class OrderEditForm(forms.ModelForm):
    """Форма редактирования заказа — описание."""

    class Meta:
        model = Order
        fields = ['description']
        labels = {
            'description': 'Описание заказа',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите, что нужно напечатать...'}),
        }
