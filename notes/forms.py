from django import forms


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
