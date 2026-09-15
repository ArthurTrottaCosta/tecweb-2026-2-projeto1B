from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import NoteForm
from .models import Note


@require_http_methods(['GET', 'POST'])
def index(request):
    form = NoteForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        Note.objects.create(
            title=form.cleaned_data['titulo'],
            content=form.cleaned_data['detalhes'],
        )
        return redirect('index')
    return render(request, 'notes/index.html', {
        'notes': Note.objects.all(),
        'form': form,
    })


@require_http_methods(['GET', 'POST'])
def edit_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    form = NoteForm(
        request.POST if request.method == 'POST' else None,
        initial={'titulo': note.title, 'detalhes': note.content},
    )
    if request.method == 'POST' and form.is_valid():
        note.title = form.cleaned_data['titulo']
        note.content = form.cleaned_data['detalhes']
        note.save()
        return redirect('index')
    return render(request, 'notes/edit.html', {'note': note, 'form': form})


@require_http_methods(['GET', 'POST'])
def delete_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    if request.method == 'POST':
        note.delete()
        return redirect('index')
    return render(request, 'notes/delete.html', {'note': note})
