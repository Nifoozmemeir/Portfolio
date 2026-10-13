from django import forms
from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    message = forms.CharField(max_length=3000, widget=forms.Textarea) # Tope para que no llenen la base con textos gigantes
    website = forms.CharField(required=False) # Honeypot: invisible para personas, los bots lo llenan
    token = forms.CharField(required=False) # Momento firmado en que se cargó la página (trampa de tiempo)

    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')
