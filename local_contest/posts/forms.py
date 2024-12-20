# forms.py
from django import forms
from.models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('description', 'image')
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control mb-3 post-input', 'placeholder': 'Que voulez-vous partager?'}),
            'image': forms.FileInput(attrs={'class': 'form-control image-upload d-none', 'accept': 'image/*', 'id': 'image-upload'}),
        }