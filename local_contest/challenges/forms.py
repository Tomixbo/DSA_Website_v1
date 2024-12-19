from django import forms
from .models import DefinedFile, Level

class DefinedFileAdminForm(forms.ModelForm):
    class Meta:
        model = DefinedFile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level'].queryset = Level.objects.all()

        # Optional: Customize the level field label
        self.fields['level'].label_from_instance = lambda obj: '%s - %s' % (obj.name, obj.challenge.name)
