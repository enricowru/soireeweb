from django import forms
from .models import Event, Moderator
from django.contrib.auth import get_user_model

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date'] # Add other fields you want to be editable

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
    username = forms.CharField(max_length=150, disabled=True) # Username should not be changed
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    mobile = forms.CharField(max_length=11, required=False)

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)

        if self.user_instance:
            self.fields['username'].initial = self.user_instance.username
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial = self.user_instance.last_name
            self.fields['email'].initial = self.user_instance.email
            self.fields['mobile'].initial = self.user_instance.mobile

    def save(self):
        if self.user_instance:
            self.user_instance.first_name = self.cleaned_data['first_name']
            self.user_instance.last_name = self.cleaned_data['last_name']
            self.user_instance.email = self.cleaned_data['email']
            self.user_instance.mobile = self.cleaned_data.get('mobile')
            self.user_instance.save()
        return self.user_instance 