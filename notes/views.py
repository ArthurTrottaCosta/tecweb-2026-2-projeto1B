from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .forms import NoteForm
from .models import Note, Tag


@require_http_methods(['GET', 'POST'])
def index(request):
    form = NoteForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('index')
    return render(request, 'notes/index.html', {
        'notes': Note.objects.prefetch_related('tags'),
        'form': form,
    })


@require_http_methods(['GET', 'POST'])
def edit_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    form = NoteForm(
        request.POST if request.method == 'POST' else None,
        initial={
            'titulo': note.title,
            'detalhes': note.content,
            'tags': ', '.join(note.tags.values_list('name', flat=True)),
        },
    )
    if request.method == 'POST' and form.is_valid():
        form.save(note)
        return redirect('index')
    return render(request, 'notes/edit.html', {'note': note, 'form': form})


@require_http_methods(['GET', 'POST'])
def delete_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    if request.method == 'POST':
        note.delete()
        return redirect('index')
    return render(request, 'notes/delete.html', {'note': note})


@require_safe
def tag_list(request):
    return render(request, 'notes/tags.html', {'tags': Tag.objects.all()})


@require_safe
def tag_detail(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    return render(request, 'notes/tag_detail.html', {
        'tag': tag,
        'notes': tag.notes.prefetch_related('tags'),
    })
