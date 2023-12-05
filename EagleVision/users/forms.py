from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')

class CustomUserUpdateForm(forms.ModelForm):
    GRADUATION_YEAR_CHOICES = [(r, r) for r in range(2024, 2028)]
    SCHOOL_CHOICES = [
        ('MCAS', 'MCAS'),
        ('CSOM', 'CSOM'),
        ('CSON', 'CSON'),
        ('LAW', 'LAW'),
        ('LSEHD', 'LSEHD'),
        ('SSW', 'SSW'),
        ('STM', 'STM'),
        ('WCAS', 'WCAS')
    ]

    graduation_year = forms.ChoiceField(choices=GRADUATION_YEAR_CHOICES)
    school = forms.ChoiceField(choices=SCHOOL_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['graduation_year', 'school', 'major', 'minor']

    def __init__(self, *args, **kwargs):
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'user-field' 
           
