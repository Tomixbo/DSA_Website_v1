from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms 
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm





User=get_user_model()

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(max_length=50, widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    graduation_field = forms.ChoiceField(required=True,
        widget=forms.Select(attrs={'class':'mx-3'}),
        choices=CustomUser.GRADUATION_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'graduation_field', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = "form-control"
        self.fields['password1'].widget.attrs['class'] = "form-control"
        self.fields['password2'].widget.attrs['class'] = "form-control"
    
    def as_p_no_errors(self):
        output = []
        for name, field in self.fields.items():
            bf = self[name]
            output.append(f'<p>{bf.label_tag()}{bf}</p>')
        return '\n'.join(output)

    def save(self, commit=True):
        user = super(RegisterUserForm, self).save(commit=False)
        user.username = user.username.lower()
        if commit:
            user.save()
        return user
    

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize CSS classes for form fields
        self.fields['old_password'].widget.attrs['class'] = 'form-control custom-old-password mt-2'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control custom-new-password1 mt-2'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control custom-new-password2 mt-2'

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize CSS classes for form fields
        self.fields['email'].widget.attrs['class'] = 'form-control custom-old-password mt-2'

class CustomPasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize CSS classes for form fields
        self.fields['new_password1'].widget.attrs['class'] = 'form-control custom-new-password1 mt-2'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control custom-new-password2 mt-2' 