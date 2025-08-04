from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe


class SelectOrCreateWidget(forms.Select):
    """Widget qui permet de sélectionner dans une liste ou d'ajouter une nouvelle entrée"""
    
    def __init__(self, model_class, create_url_name, *args, **kwargs):
        self.model_class = model_class
        self.create_url_name = create_url_name
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        attrs['class'] = attrs.get('class', '') + ' select-or-create'
        attrs['data-create-url'] = reverse_lazy(self.create_url_name)
        
        # Ajouter une option pour créer une nouvelle entrée
        choices = [('', '--- Sélectionner ou créer ---')] + list(self.choices)
        if hasattr(self, 'queryset'):
            choices = [('', '--- Sélectionner ou créer ---')] + [
                (obj.pk, str(obj)) for obj in self.queryset
            ]
        
        # Widget select standard
        select_html = super().render(name, value, attrs, renderer)
        
        # Bouton pour ajouter une nouvelle entrée
        add_button_html = f'''
        <button type="button" class="btn btn-sm btn-outline-primary add-new-btn" 
                data-field-name="{name}" 
                data-model-name="{self.model_class._meta.verbose_name}">
            + Ajouter un.e nouvel.le {self.model_class._meta.verbose_name.lower()}
        </button>
        '''
        
        return mark_safe(f'<div class="select-or-create-wrapper">{select_html}{add_button_html}</div>')


class SelectMultipleOrCreateWidget(forms.SelectMultiple):
    """Widget qui permet de sélectionner plusieurs éléments dans une liste ou d'ajouter de nouvelles entrées"""
    
    def __init__(self, model_class, create_url_name, *args, **kwargs):
        self.model_class = model_class
        self.create_url_name = create_url_name
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        attrs['class'] = attrs.get('class', '') + ' select-multiple-or-create'
        attrs['data-create-url'] = reverse_lazy(self.create_url_name)
        attrs['multiple'] = True
        
        # Widget select multiple standard
        select_html = super().render(name, value, attrs, renderer)
        
        # Bouton pour ajouter une nouvelle entrée
        add_button_html = f'''
        <button type="button" class="btn btn-sm btn-outline-primary add-new-multiple-btn" 
                data-field-name="{name}" 
                data-model-name="{self.model_class._meta.verbose_name}">
            + Ajouter un.e nouvel.le {self.model_class._meta.verbose_name.lower()}
        </button>
        '''
        
        return mark_safe(f'<div class="select-multiple-or-create-wrapper">{select_html}{add_button_html}</div>')


class TagWidget(forms.TextInput):
    """Widget pour les mots-clés avec auto-complétion"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'class': 'form-control keyword-input',
            'data-autocomplete-url': reverse_lazy('artworks:keyword_autocomplete'),
            'data-create-url':       reverse_lazy('artworks:keyword_create_ajax'),
            'placeholder': 'Commencez à taper pour voir les suggestions...'
        })
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        # Si value est une liste d'objets (ManyToMany), convertir en chaîne
        if hasattr(value, 'all'):
            value = ', '.join([kw.name for kw in value.all()])
        elif isinstance(value, list):
            value = ', '.join([str(v) for v in value])
        
        attrs.update(self.attrs)
        
        input_html = super().render(name, value, attrs, renderer)
        
        # Container pour les suggestions
        suggestions_html = '''
        <div class="keyword-suggestions" style="display: none;">
            <ul class="list-group position-absolute w-100" style="z-index: 1000;"></ul>
        </div>
        '''
        
        return mark_safe(f'<div class="keyword-input-wrapper position-relative">{input_html}{suggestions_html}</div>') 