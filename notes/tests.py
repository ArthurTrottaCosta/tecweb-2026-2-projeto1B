from django.test import Client, TestCase
from django.urls import reverse

from .models import Note


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
