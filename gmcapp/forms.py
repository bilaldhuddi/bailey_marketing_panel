from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import OpenAIAPI, SerpAPI, MessageTemplate


class CustomLoginForm(AuthenticationForm):
    class CustomLoginForm(AuthenticationForm):
        error_messages = {
            'invalid_login': (
                "Invalid username or password."
            ),
            'inactive': "This account is inactive.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide labels for username and password fields
        self.fields['username'].label = False
        self.fields['password'].label = False

        # Add placeholder text for username and password fields
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

        # Add custom CSS classes to fields
        self.fields['username'].widget.attrs.update({'class': 'custom-input'})
        self.fields['password'].widget.attrs.update({'class': 'custom-input'})


class OpenAIAPIForm(forms.ModelForm):
    class Meta:
        model = OpenAIAPI
        fields = ['openai_api_key']


class SerpAPIForm(forms.ModelForm):
    class Meta:
        model = SerpAPI
        fields = ['serp_api_key']


class MessageTemplateForm(forms.ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ['message_text', 'additional_info']

    message_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 40}),  # Customize rows and cols as needed
    )

    additional_info = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),  # Customize rows and cols as needed
    )
