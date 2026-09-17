from django import forms
from django.db import transaction

from .models import Note, Tag


class NoteForm(forms.Form):
    titulo = forms.CharField(
        label='Título',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-card-title field-border',
            'placeholder': 'Título da anotação',
        }),
        error_messages={'required': 'Preencha o título da anotação.'},
    )
    detalhes = forms.CharField(
        label='Detalhes',
        widget=forms.Textarea(attrs={
            'class': 'autoresize field-border',
            'placeholder': 'Digite sua anotação...',
            'rows': 3,
        }),
        error_messages={'required': 'Preencha os detalhes da anotação.'},
    )
    tags = forms.CharField(
        label='Tags (opcional)',
        required=False,
        help_text='Separe por vírgulas. Exemplo: estudos, faculdade. As tags são salvas em minúsculas.',
        widget=forms.TextInput(attrs={
            'class': 'tag-input field-border',
            'placeholder': 'estudos, faculdade',
        }),
    )

    def clean_tags(self):
        names = []
        for value in self.cleaned_data['tags'].split(','):
            name = value.strip().casefold()
            if len(name) > 200:
                raise forms.ValidationError('Cada tag deve ter no máximo 200 caracteres.')
            if name and name not in names:
                names.append(name)
        return names

    @transaction.atomic
    def save(self, note=None):
        # Salva a nota antes de associar as tags, pois ela precisa de um id.
        if note is None:
            note = Note()
        note.title = self.cleaned_data['titulo']
        note.content = self.cleaned_data['detalhes']
        note.save()
        tags = [Tag.objects.get_or_create(name=name)[0] for name in self.cleaned_data['tags']]
        # Substitui as associações; uma lista vazia remove todas as tags da nota.
        note.tags.set(tags)
        return note
