# Get-it — Projeto 1B

Projeto individual de Tecnologias Web, Insper 2026/2. Aplicação de anotações em Django 6.0 e Python 3.12 ou superior.

## Etapa 1: CRUD em Django

- Criar e listar anotações com título e conteúdo.
- Editar ou cancelar sem salvar alterações.
- Excluir somente após confirmação por POST.
- Validar campos obrigatórios e título com até 200 caracteres.
- Armazenar as notas no SQLite usando o ORM e as migrações do Django.
- Interface Get-it com templates, CSS e JavaScript.

## Etapa 2: Tags

- Uma anotação pode ter zero, uma ou várias tags; uma tag pode estar em várias anotações (many-to-many).
- No campo Tags, digite os nomes separados por vírgula, por exemplo: `estudos, faculdade`.
- Os nomes são salvos em minúsculas, sem espaços nas extremidades. Valores vazios e repetidos são ignorados; cada nome aceita até 200 caracteres.
- A edição mostra as tags atuais. Substitua o texto para adicionar/remover tags ou apague o campo para remover todas as associações daquela nota.
- `/tags/` lista os nomes das tags com links; `/tags/<tag_id>/` mostra as anotações daquela tag.
- Remover uma tag de uma nota ou excluir a nota preserva a tag e suas associações com outras notas. Tags sem notas continuam disponíveis na listagem.

Ao atualizar a partir da etapa 1, execute `python manage.py migrate`. A migração adiciona as tabelas de tags e associações e preserva as notas existentes.

## Executar localmente (PowerShell)

Dentro da pasta deste repositório:

```powershell
py -3.12 -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Acesse http://localhost:8000/. Em execuções posteriores, basta ativar o ambiente e iniciar o servidor. O banco `db.sqlite3` guarda os dados locais e não é versionado.

## Verificar

```powershell
python manage.py check
python manage.py test
```

Os testes usam um banco separado, sem alterar suas anotações locais. No navegador, confira também os botões Cancelar, os formulários e a confirmação de exclusão.

Opcionalmente, execute `python manage.py createsuperuser` para usar o Django Admin em `/admin/`.

## Próxima etapa

3. PostgreSQL em Docker, publicação e inclusão do endereço público neste README.

Esta etapa funciona localmente; a aplicação ainda não foi publicada.

Enunciado: https://barbaratieko.github.io/tecweb/projetos/projeto1/projeto1b/
