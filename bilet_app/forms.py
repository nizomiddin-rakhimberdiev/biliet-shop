from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from .models import Booking, Profil


class BookingForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=20,
        label='Telefon raqam',
        validators=[RegexValidator(r'^\+?\d{9,15}$', "To'g'ri format: +998901234567")],
        widget=forms.TextInput(attrs={'placeholder': '+998901234567'}),
    )
    quantity = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        label='Biletlar soni',
    )

    class Meta:
        model   = Booking
        fields  = ['quantity', 'phone']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = Profil
        fields = ['avatar']
