from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

from .models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['user']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-10 mb-0'),
                Column('is_favorite', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            'content',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )

