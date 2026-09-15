# Get-it — Projeto 1B

Projeto individual de Tecnologias Web, Insper 2026/2. Aplicação de anotações em Django 6.0 e Python 3.12 ou superior.

## Etapa 1: CRUD em Django

- Criar e listar anotações com título e conteúdo.
- Editar ou cancelar sem salvar alterações.
- Excluir somente após confirmação por POST.
- Validar campos obrigatórios e título com até 200 caracteres.
- Armazenar as notas no SQLite usando o ORM e as migrações do Django.
- Interface Get-it com templates, CSS e JavaScript.

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

## Próximas etapas

2. Tags com relacionamento many-to-many e navegação por tag.
3. PostgreSQL em Docker, publicação e inclusão do endereço público neste README.

Esta etapa funciona localmente; a aplicação ainda não foi publicada.

Enunciado: https://barbaratieko.github.io/tecweb/projetos/projeto1/projeto1b/
