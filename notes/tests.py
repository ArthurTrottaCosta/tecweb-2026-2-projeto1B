from django.test import Client, TestCase
from django.urls import reverse

from .models import Note, Tag


class NoteFlowTests(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Estudar Django', content='Rotas e views')
        self.edit_url = reverse('edit_note', args=[self.note.pk])
        self.delete_url = reverse('delete_note', args=[self.note.pk])

    def test_list_and_empty_state(self):
        self.assertContains(self.client.get('/'), self.note.title)
        self.note.delete()
        self.assertContains(self.client.get('/'), 'Nenhuma anotação por enquanto.')

    def test_create_and_refresh_does_not_duplicate(self):
        response = self.client.post('/', {'titulo': "  Receita d'água  ", 'detalhes': 'Linha 1\nLinha 2'})
        self.assertRedirects(response, '/')
        created = Note.objects.get(title="Receita d'água")
        self.assertEqual(created.content, 'Linha 1\nLinha 2')
        self.client.get('/')
        self.assertEqual(Note.objects.count(), 2)

    def test_invalid_creation_preserves_input_and_database(self):
        for data in ({}, {'titulo': '  ', 'detalhes': 'Texto preservado'},
                     {'titulo': 'Título preservado', 'detalhes': '  '},
                     {'titulo': 'x' * 201, 'detalhes': 'Texto'}):
            with self.subTest(data=data):
                response = self.client.post('/', data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)
                self.assertEqual(response.context['form'].data.dict(), data)
                self.assertEqual(Note.objects.count(), 1)

    def test_edit_prefills_and_cancel_is_get_without_write(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.context['form']['titulo'].value(), self.note.title)
        self.assertEqual(response.context['form']['detalhes'].value(), self.note.content)
        self.assertContains(response, 'href="/">Cancelar</a>')
        self.client.get('/')
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Estudar Django')

    def test_edit_saves_same_record(self):
        response = self.client.post(self.edit_url, {'titulo': 'Editada', 'detalhes': 'Novo conteúdo'})
        self.assertRedirects(response, '/')
        self.note.refresh_from_db()
        self.assertEqual((self.note.title, self.note.content), ('Editada', 'Novo conteúdo'))
        self.assertEqual(Note.objects.count(), 1)

    def test_invalid_edit_keeps_original_record(self):
        response = self.client.post(self.edit_url, {'titulo': 'Tentativa', 'detalhes': ' '})
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(response.context['form']['titulo'].value(), 'Tentativa')
        self.note.refresh_from_db()
        self.assertEqual((self.note.title, self.note.content), ('Estudar Django', 'Rotas e views'))

    def test_delete_get_only_confirms_and_cancel_preserves(self):
        self.assertContains(self.client.get(self.delete_url), 'Confirmar exclusão')
        self.client.get('/')
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_delete_post_removes_only_selected_note(self):
        other = Note.objects.create(title='Outra', content='Preservar')
        self.assertRedirects(self.client.post(self.delete_url), '/')
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
        self.assertTrue(Note.objects.filter(pk=other.pk).exists())

    def test_missing_notes_and_unknown_routes_return_404(self):
        self.note.delete()
        for url in (self.edit_url, self.delete_url, '/inexistente/'):
            for method in (self.client.get, self.client.post):
                with self.subTest(url=url, method=method.__name__):
                    self.assertEqual(method(url).status_code, 404)

    def test_unsafe_methods_are_rejected_without_mutation(self):
        for url in ('/', self.edit_url, self.delete_url):
            self.assertEqual(self.client.delete(url).status_code, 405)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_html_is_escaped(self):
        self.note.title = '<script>alert(1)</script>'
        self.note.content = '<img src=x onerror=alert(2)>\nOutra linha'
        self.note.save()
        for url in ('/', self.edit_url, self.delete_url):
            response = self.client.get(url)
            self.assertNotContains(response, '<script>alert(1)</script>')
            self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
            self.assertNotContains(response, '<img src=x onerror=alert(2)>')

    def test_forms_require_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        for url in ('/', self.edit_url, self.delete_url):
            self.assertContains(client.get(url), 'csrfmiddlewaretoken')
            self.assertEqual(client.post(url, {'titulo': 'X', 'detalhes': 'Y'}).status_code, 403)
        self.assertEqual(Note.objects.count(), 1)


class TagFlowTests(TestCase):
    def create_note(self, title, tags=''):
        response = self.client.post('/', {
            'titulo': title, 'detalhes': 'Conteúdo de ' + title, 'tags': tags,
        })
        self.assertRedirects(response, '/')
        return Note.objects.get(title=title)

    def test_create_with_zero_one_and_multiple_tags(self):
        for title, raw, expected in (
            ('Sem tags', '', []),
            ('Uma tag', 'estudos', ['estudos']),
            ('Várias tags', 'estudos, faculdade', ['estudos', 'faculdade']),
            ('Apenas separadores', ' , , ', []),
        ):
            with self.subTest(title=title):
                note = self.create_note(title, raw)
                self.assertEqual(list(note.tags.values_list('name', flat=True)), expected)

    def test_reuses_tags_across_notes_and_normalizes_input(self):
        first = self.create_note('Primeira', ' Estudos, estudos, ESTUDOS, AÇÃO, ação, ,')
        second = self.create_note('Segunda', 'estudos, ação')
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(first.tags.count(), 2)
        self.assertEqual(second.tags.count(), 2)
        self.assertEqual(Tag.objects.get(name='estudos').notes.count(), 2)

    def test_edit_prefills_adds_removes_and_clears_tags(self):
        note = self.create_note('Editar tags', 'estudos, faculdade')
        shared = self.create_note('Compartilhada', 'faculdade')
        url = reverse('edit_note', args=[note.pk])
        response = self.client.get(url)
        self.assertEqual(response.context['form']['tags'].value(), 'estudos, faculdade')
        self.assertRedirects(self.client.post(url, {
            'titulo': note.title, 'detalhes': note.content, 'tags': 'estudos, python',
        }), '/')
        self.assertEqual(list(note.tags.values_list('name', flat=True)), ['estudos', 'python'])
        self.assertTrue(shared.tags.filter(name='faculdade').exists())
        self.assertRedirects(self.client.post(url, {
            'titulo': note.title, 'detalhes': note.content, 'tags': '',
        }), '/')
        self.assertEqual(note.tags.count(), 0)
        self.assertTrue(shared.tags.filter(name='faculdade').exists())

    def test_invalid_tags_do_not_create_partial_records(self):
        response = self.client.post('/', {
            'titulo': 'Inválida', 'detalhes': 'Conteúdo', 'tags': 'válida,' + 'x' * 201,
        })
        self.assertContains(response, 'Cada tag deve ter no máximo 200 caracteres.')
        self.assertEqual(Note.objects.count(), 0)
        self.assertEqual(Tag.objects.count(), 0)

    def test_invalid_edit_preserves_note_tags_and_submitted_input(self):
        note = self.create_note('Original', 'antiga')
        url = reverse('edit_note', args=[note.pk])
        for data in (
            {'titulo': 'Tentativa', 'detalhes': ' ', 'tags': 'nova'},
            {'titulo': 'Tentativa', 'detalhes': 'Novo', 'tags': 'nova,' + 'x' * 201},
        ):
            with self.subTest(data=data):
                response = self.client.post(url, data)
                self.assertTrue(response.context['form'].errors)
                self.assertEqual(response.context['form']['tags'].value(), data['tags'])
                note.refresh_from_db()
                self.assertEqual(note.title, 'Original')
                self.assertEqual(note.content, 'Conteúdo de Original')
                self.assertEqual(list(note.tags.values_list('name', flat=True)), ['antiga'])
                self.assertEqual(Tag.objects.count(), 1)

    def test_cancel_does_not_change_tags(self):
        note = self.create_note('Cancelar', 'original')
        self.client.get(reverse('edit_note', args=[note.pk]))
        self.client.get('/')
        self.assertEqual(list(note.tags.values_list('name', flat=True)), ['original'])

    def test_tag_list_and_details_filter_notes_and_link_navigation(self):
        first = self.create_note('Receita especial', 'comida, casa')
        second = self.create_note('Lista de compras', 'comida')
        self.create_note('Outra matéria', 'estudos')
        food = Tag.objects.get(name='comida')
        url = reverse('tag_detail', args=[food.pk])
        listing = self.client.get(reverse('tag_list'))
        self.assertQuerySetEqual(listing.context['tags'], ['casa', 'comida', 'estudos'], transform=lambda tag: tag.name)
        self.assertContains(listing, f'href="{url}"')
        self.assertContains(self.client.get('/'), 'href="/tags/"')
        detail = self.client.get(url)
        self.assertQuerySetEqual(detail.context['notes'], [second, first])
        self.assertContains(detail, 'Receita especial')
        self.assertNotContains(detail, 'Outra matéria')
        self.assertContains(detail, reverse('edit_note', args=[first.pk]))
        self.assertContains(detail, reverse('delete_note', args=[first.pk]))

    def test_empty_tags_and_missing_tag(self):
        self.assertContains(self.client.get('/tags/'), 'Nenhuma tag por enquanto.')
        tag = Tag.objects.create(name='vazia')
        self.assertContains(self.client.get(reverse('tag_detail', args=[tag.pk])), 'Nenhuma anotação com esta tag.')
        self.assertEqual(self.client.get('/tags/9999/').status_code, 404)

    def test_deleting_note_preserves_shared_tag_and_other_notes(self):
        first = self.create_note('Apagar', 'compartilhada, exclusiva')
        other = self.create_note('Manter', 'compartilhada')
        self.assertRedirects(self.client.post(reverse('delete_note', args=[first.pk])), '/')
        self.assertEqual(Tag.objects.count(), 2)
        tag = Tag.objects.get(name='compartilhada')
        self.assertQuerySetEqual(tag.notes.all(), [other])
        self.assertEqual(Tag.objects.get(name='exclusiva').notes.count(), 0)

    def test_tag_names_are_escaped_and_pages_reject_mutations(self):
        note = self.create_note('HTML', '<script>alert(1)</script>')
        tag = note.tags.get()
        for url in ('/', '/tags/', reverse('tag_detail', args=[tag.pk])):
            response = self.client.get(url)
            self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
            self.assertNotContains(response, '<script>alert(1)</script>')
        for url in ('/tags/', reverse('tag_detail', args=[tag.pk])):
            self.assertEqual(self.client.post(url).status_code, 405)
