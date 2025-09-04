from django import forms
from .models import Event, MobilePost, Comment
from django.contrib.auth import get_user_model
from django.utils import timezone

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date'] # Add other fields you want to be editable
    def clean_date(self):
            date = self.cleaned_data.get('date')
            if date and date < timezone.now():
                raise forms.ValidationError("Event date cannot be in the past.")
            return date

User = get_user_model()

class ModeratorEditForm(forms.Form):
    # User fields
    username = forms.CharField(max_length=150, disabled=True) # Username should not be changed
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    mobile = forms.CharField(max_length=11, required=False) # Assuming mobile is optional

    def __init__(self, *args, **kwargs):
        # Accept user instance
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)

        # Initialize form with instance data
        if self.user_instance:
            self.fields['username'].initial = self.user_instance.username
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial = self.user_instance.last_name
            self.fields['email'].initial = self.user_instance.email
            self.fields['mobile'].initial = self.user_instance.mobile

    def save(self):
        # Save data to user instance
        if self.user_instance:
            self.user_instance.first_name = self.cleaned_data['first_name']
            self.user_instance.last_name = self.cleaned_data['last_name']
            self.user_instance.email = self.cleaned_data['email']
            self.user_instance.mobile = self.cleaned_data.get('mobile')
            self.user_instance.save()

        return self.user_instance # Return the saved instance

class AdminEditForm(forms.Form):
    # User fields
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    mobile = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Password fields
    current_password = forms.CharField(
        max_length=128, 
        required=False, 
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter current password to change password', 'class': 'form-control'})
    )
    password = forms.CharField(
        max_length=128, 
        required=False, 
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password', 'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        max_length=128, 
        required=False, 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)

        if self.user_instance:
            self.fields['username'].initial = self.user_instance.username
            self.fields['email'].initial = self.user_instance.email
            self.fields['mobile'].initial = self.user_instance.mobile

    def clean_username(self):
        username = self.cleaned_data['username']
        # Check if username is unique (excluding current user)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(username=username).exclude(pk=self.user_instance.pk if self.user_instance else None).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # If user wants to change password, they must provide current password
        if new_password and new_password.strip():
            if not current_password:
                raise forms.ValidationError("You must enter your current password to set a new password.")
            
            # Verify current password is correct
            if self.user_instance and not self.user_instance.check_password(current_password):
                raise forms.ValidationError("Current password is incorrect.")
            
            # Validate new password strength
            if len(new_password) < 8:
                raise forms.ValidationError("New password must be at least 8 characters long.")
            
            # Check for at least one digit, one uppercase, one lowercase
            import re
            if not re.search(r'[0-9]', new_password):
                raise forms.ValidationError("New password must contain at least one number.")
            if not re.search(r'[A-Z]', new_password):
                raise forms.ValidationError("New password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', new_password):
                raise forms.ValidationError("New password must contain at least one lowercase letter.")
            
            # Check if new password and confirm password match
            if not confirm_password:
                raise forms.ValidationError("Please confirm your new password.")
            
            if new_password != confirm_password:
                raise forms.ValidationError("New password and confirm password do not match.")
        
        # If confirm password is provided but new password is not
        elif confirm_password and confirm_password.strip():
            raise forms.ValidationError("Please enter a new password to confirm.")
        
        # If current password is provided without new password
        elif current_password and current_password.strip():
            if not new_password or not new_password.strip():
                raise forms.ValidationError("Please enter a new password.")
        
        return cleaned_data

    def save(self):
        if self.user_instance:
            self.user_instance.username = self.cleaned_data['username']
            self.user_instance.email = self.cleaned_data['email']
            self.user_instance.mobile = self.cleaned_data.get('mobile')
            
            # Handle password change if provided
            password = self.cleaned_data.get('password')
            if password and password.strip():
                self.user_instance.set_password(password)
            
            self.user_instance.save()
        return self.user_instance 
    

class MobilePostForm(forms.ModelForm):
    class Meta:
        model = MobilePost
        fields = ['title', 'content']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'}),
        }