from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, Div, HTML

from .models import Artwork, Artist, Collection, Exhibition, ArtworkPhoto, WishlistItem, ArtType, Support, Technique, Keyword
from .widgets import SelectOrCreateWidget, SelectMultipleOrCreateWidget, TagWidget


class ArtworkForm(forms.ModelForm):
    # Champ personnalisé pour les mots-clés
    keywords_text = forms.CharField(
        required=False,
        widget=TagWidget(),
        label="Mots-clés",
        help_text="Tapez pour voir les suggestions ou créer de nouveaux mots-clés"
    )
    
    class Meta:
        model = Artwork
        exclude = ['user', 'id', 'created_at', 'updated_at', 'keywords']
        widgets = {
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
            'last_exhibited': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'contextual_references': forms.Textarea(attrs={'rows': 3}),
            'provenance': forms.Textarea(attrs={'rows': 3}),
            'artists': SelectMultipleOrCreateWidget(Artist, 'artworks:artist_create_ajax'),
            'art_type': SelectOrCreateWidget(ArtType, 'artworks:arttype_create_ajax'),
            'support': SelectOrCreateWidget(Support, 'artworks:support_create_ajax'),
            'technique': SelectOrCreateWidget(Technique, 'artworks:technique_create_ajax'),
            'collections': SelectMultipleOrCreateWidget(Collection, 'artworks:collection_create_ajax'),
            'exhibitions': SelectMultipleOrCreateWidget(Exhibition, 'artworks:exhibition_create_ajax'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['collections'].queryset = Collection.objects.filter(user=user)
            self.fields['exhibitions'].queryset = Exhibition.objects.filter(user=user)
        
        # Peupler le champ keywords_text avec les mots-clés existants
        if self.instance and self.instance.pk:
            keywords = self.instance.keywords.all()
            self.fields['keywords_text'].initial = ', '.join([kw.name for kw in keywords])
        
        # Définir les querysets pour les widgets SelectOrCreate
        self.fields['artists'].queryset = Artist.objects.all()
        self.fields['art_type'].queryset = ArtType.objects.all()
        self.fields['support'].queryset = Support.objects.all()
        self.fields['technique'].queryset = Technique.objects.all()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informations générales',
                Row(
                    Column('title', css_class='form-group col-md-8 mb-0'),
                    Column('creation_year', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('artists', css_class='form-group col-md-6 mb-0'),
                    Column('origin_country', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('art_type', css_class='form-group col-md-4 mb-0'),
                    Column('support', css_class='form-group col-md-4 mb-0'),
                    Column('technique', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Dimensions et caractéristiques',
                Row(
                    Column('height', css_class='form-group col-md-3 mb-0'),
                    Column('width', css_class='form-group col-md-3 mb-0'),
                    Column('depth', css_class='form-group col-md-3 mb-0'),
                    Column('weight', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('is_signed', css_class='form-group col-md-4 mb-0'),
                    Column('is_framed', css_class='form-group col-md-4 mb-0'),
                    Column('is_acquired', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Acquisition et provenance',
                Row(
                    Column('acquisition_date', css_class='form-group col-md-4 mb-0'),
                    Column('acquisition_place', css_class='form-group col-md-4 mb-0'),
                    Column('price', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                'provenance',
                'owners',
            ),
            Fieldset(
                'Localisation et statut',
                Row(
                    Column('current_location', css_class='form-group col-md-6 mb-0'),
                    Column('is_borrowed', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('collections', css_class='form-group col-md-6 mb-0'),
                    Column('exhibitions', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'last_exhibited',
            ),
            Fieldset(
                'Informations complémentaires',
                'parent_artwork',
                'keywords_text',
                'contextual_references',
                'notes',
            ),
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        
        if commit:
            # Traiter les mots-clés
            keywords_text = self.cleaned_data.get('keywords_text', '')
            if keywords_text:
                keyword_names = [name.strip() for name in keywords_text.split(',') if name.strip()]
                keywords = []
                for name in keyword_names:
                    keyword, created = Keyword.objects.get_or_create(name=name)
                    keywords.append(keyword)
                instance.keywords.set(keywords)
            else:
                instance.keywords.clear()
        
        return instance

class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = '__all__'
        widgets = {
            'biography': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('birth_year', css_class='form-group col-md-6 mb-0'),
                Column('death_year', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'nationality',
            'biography',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        exclude = ['user']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )

class ExhibitionForm(forms.ModelForm):
    class Meta:
        model = Exhibition
        exclude = ['user']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'location',
            Row(
                Column('start_date', css_class='form-group col-md-6 mb-0'),
                Column('end_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )

class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        exclude = ['user']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            Row(
                Column('artist_name', css_class='form-group col-md-6 mb-0'),
                Column('estimated_price', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('priority', css_class='form-group col-md-6 mb-0'),
                Column('source_url', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'notes',
            Submit('submit', 'Ajouter', css_class='btn btn-primary')
        )

# Formset pour les photos
ArtworkPhotoFormSet = inlineformset_factory(
    Artwork, ArtworkPhoto,
    fields=['image', 'caption', 'is_primary'],
    extra=3,
    can_delete=True
)
