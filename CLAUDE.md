# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

El archivo tiene dos partes:

1. **Estándar común**: lo que comparten TODOS los proyectos Django del usuario. Si algo del proyecto no lo cumple, es un pendiente a corregir, no una excepción.
2. **Este proyecto (Portfolio)**: lo particular de este repo.

## Reglas de trabajo

Van por encima de cualquier otra cosa en este archivo.

- **Git/GitHub lo maneja SOLO el usuario.** Nunca correr `git add`, `git commit` ni `git push` por tu cuenta. Solo cuando el usuario lo pide explícitamente, en ese momento y para ese cambio puntual. Que lo haya pedido una vez no autoriza las siguientes.
- **Migraciones las maneja SOLO el usuario.** Nunca correr `makemigrations`, `migrate` ni crear migraciones vacías por tu cuenta. Igual que con Git.
- **Los settings los toca SOLO el usuario.** No modificar `settingslocal.py` ni `settingsproduction.py` sin pedido explícito. Si un cambio los necesita, avisar y esperar confirmación.

Ante la duda: proponer el comando o el cambio y esperar el OK, no ejecutarlo.

---

# Parte 1 — Estándar común a todos los proyectos

### Convención de nombres

Siempre y en todo el código propio:

- **Python**
  - **`NombreDeClase`** (PascalCase) → clases: models, admins, AppConfig, forms, tests, storages.
  - **`nombreDeFuncion`** (camelCase) → funciones y métodos propios: views, helpers, métodos de test, métodos de model/admin que no sean overrides.
  - **`nombredevariable`** (todo minúscula, sin guiones bajos) → variables, campos de model, parámetros, atributos, claves del contexto del template. En models, la única excepción son `created_at`, `updated_at` y otros campos readonly de ese estilo, que van en snake_case.
- **JavaScript** → camelCase para variables y funciones.
- **HTML** → camelCase para `id` y nombres propios.
- **CSS** → kebab-case para clases (`.skill-card`).
- **`name` de las URLs** → minúscula si es una palabra (`home`), snake_case si son dos o más (`about_me`).
- **MAYÚSCULA** (`UPPER_CASE`) → constantes, `choices`, configs de settings, variables de `.env` y de entorno (también en bash).
- **Lo que viene de afuera se usa como viene**: imports y nombres que impone Django o una librería (`Meta`, `save()`, `has_add_permission()`, `setUpTestData()`, `urlpatterns`, `readonly_fields`, atributos `data-*`, clases de Bootstrap, etc.).

### `models.py`

- **Comentarios de un campo, siempre en la misma línea del campo**, al final. Nunca arriba ni abajo:
  ```python
  icon = models.CharField("Icon", max_length=50) # La clase de Font Awesome que se renderiza como <i class="...">
  ```
- **Constantes y `choices` se definen adentro del model sobre el que actúan, en sus primeras líneas** (antes de los campos), no sueltas a nivel módulo. Desde los métodos se usan con `self.CONSTANTE`:
  ```python
  class ProjectImage(models.Model):
      MEDIA_EXTENSIONS = ['jpg', 'png', 'mp4'] # Formatos que acepta file

      project = models.ForeignKey(...)
      file = models.FileField(..., validators=[FileExtensionValidator(MEDIA_EXTENSIONS)])
  ```

### `admin.py`

- **Cada model con su propio `ModelAdmin` y su `admin.site.register(Model, ModelAdmin)` individual**, todos juntos al final del archivo. Nada de `@admin.register` ni de inlines (por ahora).
- **Filtros siempre con `django_admin_listfilter_dropdown`**: `from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter`. En `list_filter`: `RelatedDropdownFilter` para FK/M2M, `ChoiceDropdownFilter` para campos con `choices`, `DropdownFilter` para el resto.
- **Toda FK va en `raw_id_fields`** (la lupita), y si se muestra en `list_display`, también en `list_select_related` (sin N+1).
- **Todo M2M va en `filter_horizontal`.**
- **M2M en `list_display`**: se define una función justo después del último atributo/filtro del admin, se pone en `list_display`, y el admin prefetchea la relación en `get_queryset` (sin N+1):
  ```python
  class ProjectAdmin(admin.ModelAdmin):
      list_display = ('title', 'id', 'verTechnologies')
      list_filter = (('technologies', RelatedDropdownFilter),)
      filter_horizontal = ('technologies',)

      def verTechnologies(self, obj):
          return ", ".join(t.name for t in obj.technologies.all())
      verTechnologies.short_description = 'Technologies'

      def get_queryset(self, request):
          return super().get_queryset(request).prefetch_related('technologies')
  ```

### Settings: dos archivos separados

- `settingslocal.py` (desarrollo) y `settingsproduction.py` (producción), dentro del paquete del proyecto.
- `manage.py`, `wsgi.py` y `asgi.py` apuntan por default a `settingslocal`. Producción se elige con `DJANGO_SETTINGS_MODULE=<Paquete>.settingsproduction`, nunca editando esos archivos.
- Son archivos independientes (no hay un `base.py` común): un cambio que aplica a los dos entornos (apps, middleware, templates, i18n, etc.) se hace en ambos.

### Imágenes y media → siempre AWS S3

- Tanto en local como en producción, las imágenes se suben al bucket de S3. Nunca se guardan en disco.
- Lo maneja `storagemedia.py`: una clase de storage para dev y otra para prod (mismo bucket, distinto prefijo), elegida en `STORAGES["default"]["BACKEND"]` de cada settings.
- Las imágenes van como `ImageField` en un model, que usa el storage default. No se agregan imágenes de contenido como static.

### CI/CD automatizado, siempre

- Un `git add . && git commit && git push` a `main` tiene que bastar para todo: testear, deployar al servidor de producción y dejarlo funcionando. Nada de pasos manuales en el server.
- El pipeline vive en dos archivos: `.github/workflows/deploy.yml` (GitHub Actions: job de tests y, si pasan, job de deploy por SSH) y `deploy.sh` en la raíz (lo que corre en el server).
- El push lo hace **solo el usuario**; que exista el pipeline no habilita a Claude a commitear ni pushear (ver Reglas de trabajo).
- **Cada cambio se chequea contra el pipeline.** Si el cambio necesita algo nuevo para funcionar en producción (variable de `.env`, paquete del sistema, paso de deploy, servicio), se agrega al pipeline en el mismo cambio, o se avisa si es algo que solo el usuario puede hacer (secrets de GitHub, `.env` del server).

### Tests de humo generales

- Los tests (`Core/tests.py`) son **generales**, no unitarios por vista: verifican que el sistema levanta y que nada tira 500 (todas las URLs públicas, login y home del admin, listado y alta de cada model registrado), con la base vacía.
- También corren un `collectstatic` real con estáticos versionados (manifest) en una carpeta temporal y vuelven a pedir las páginas: así un `{% static %}` o un `url(...)` de CSS que apunta a un archivo inexistente se detecta antes del deploy.
- Se descubren solos (recorren el resolver de URLs y `admin.site._registry`), así que lo nuevo queda cubierto sin escribir tests. Si un cambio agrega algo esencial que esa recorrida no alcanza (URL con parámetros, comando, integración), se suma un test general, no uno de lógica puntual.
- Corren en el CI; si fallan, no hay deploy.

### `.env` con todo lo sensible

- Todo lo que no tiene que ser visible (`SECRET_KEY`, credenciales de DB, keys de AWS, hosts, debug, etc.) va en `.env` y se lee con `config()` de `python-decouple`. Nada sensible hardcodeado en el código.
- El `.env` nunca se commitea.

### `.gitignore` completo

Tiene que cubrir como mínimo: entornos virtuales, `__pycache__`/compilados, `.env` y `.env.*`, configs de editor (`.vscode/`, `.idea/`), `.claude/`, logs, bases locales, `staticfiles/` (collectstatic) y archivos del sistema operativo. Si aparece algo nuevo generado o sensible, se agrega.

### `requirements.txt` siempre actualizado

- Siempre con versiones fijas (`paquete==x.y.z`).
- Las versiones tienen que ser **compatibles con la versión de Python del proyecto** (la del venv). Antes de agregar o subir un paquete, verificar que soporte esa versión: ni demasiado nuevo ni demasiado viejo.
- Al instalar o quitar un paquete, actualizar `requirements.txt` en el mismo cambio.

### Estructura de carpetas

- **`resources/`** en la raíz contiene todo el front:
  - `resources/static/` → assets, subdivididos por tipo (`css/`, `js/`, `favicon/`, etc.).
  - `resources/templates/` → templates, fuera de `static/`.
  - Se configura con `STATICFILES_DIRS` y `TEMPLATES["DIRS"]`; no se usan las carpetas `static/`/`templates/` por app.
- **`Core`** es la app que contiene todo lo importante para el funcionamiento del sistema base (models, vistas, urls, admin principales).

---

# Parte 2 — Este proyecto: Portfolio (jersdev.com)

Portfolio personal en **Django 5.2**, **Python 3.12.3** (venv `myvenv`). PostgreSQL en local y en producción.

### Cómo se aplica el estándar acá

- Paquete del proyecto: `Base/` → [Base/settingslocal.py](Base/settingslocal.py), [Base/settingsproduction.py](Base/settingsproduction.py), [Base/storagemedia.py](Base/storagemedia.py).
- `storagemedia.py`: `MediaStorageDev` sube a `media-dev/` y `MediaStorageProd` a `media/`. Static se sirve de disco en dev (`StaticFilesStorage`) y desde S3 en producción (`S3Boto3Storage`, prefijo `static/`).
- Cada máquina tiene su propio `.env`; [.env.example](.env.example) es la plantilla con todos los nombres (bloques LOCAL, PROD y AWS). Variable nueva → se agrega ahí también.
- App única: `Base/Core` (label `Base.Core` en `INSTALLED_APPS`, `ROOT_URLCONF` y `AppConfig.name`). [Base/urls.py](Base/urls.py) monta `/admin/` y delega el resto a [Base/Core/urls.py](Base/Core/urls.py).

### Pipeline (jersdev.com en AWS Lightsail)

Cada push a `main` (o "Run workflow" a mano en Actions) dispara [.github/workflows/deploy.yml](.github/workflows/deploy.yml):

1. **Job `test`** (ubuntu-24.04, Python 3.12, Postgres 16 como service, `DJANGO_SETTINGS_MODULE=Base.settingsproduction` con variables de mentira): `pip install -r requirements.txt` → `check --deploy --fail-level ERROR` → `makemigrations --check --dry-run` → `migrate` desde cero → `manage.py test`.
2. **Job `deploy`** (solo si pasó `test`): entra por SSH (secrets `SSH_KEY`, `SSH_HOST`, `SSH_USER`) y corre la versión de [deploy.sh](deploy.sh) que está en `origin/main`.

[deploy.sh](deploy.sh) en `/var/www/Portfolio` (venv `venv/`): `git reset --hard origin/main` → `pip install` → `check --deploy` → `migrate` → `collectstatic` (a S3) → `systemctl restart gunicorn` → verifica que `/` y `/admin/login/` respondan 200 → `limpiarestaticos` (comando propio en `Base/Core/management/commands/`: borra de `static/` en S3 todo lo que no figura en `staticfiles.json`, o sea versiones viejas con hash y archivos sacados del código; si falla solo avisa). Si algo falla antes de la verificación, rollback automático al commit anterior (la base no vuelve atrás).

Qué revisar en cada cambio para no romperlo:

- **`config('ALGO')` nuevo en `settingsproduction.py`** → sumarlo al bloque `env:` del job `test` en `deploy.yml` (con valor de mentira) y a `.env.example`, y avisar al usuario que lo cargue en el `.env` del server.
- **Cambio en models** → el CI corre `makemigrations --check`: si falta la migración, falla. Avisar al usuario que tiene que generarla antes de pushear (las migraciones las hace él).
- **Paquete nuevo** → en `requirements.txt` con versión fija; si necesita librerías del sistema para compilar, agregar el `apt-get` en `deploy.yml` y avisar que también hay que instalarlo en el server.
- **URL o página nueva** → que no rompa con la base vacía (los tests corren sin datos). Si la home cambia de ruta o se agrega una página crítica, actualizar `URLS_A_VERIFICAR` en `deploy.sh`.
- **`URLS_VIEJAS`** en `tests.py` es **momentáneo**: las URLs viejas que, si tiran 500, solo dan warning y no cortan el deploy. Se mantiene así **hasta que el usuario diga lo contrario**; no vaciarla ni quitar la excepción por iniciativa propia (ni siquiera al borrar las vistas viejas). Cuando lo pida, se elimina el mecanismo y toda URL que tire 500 corta el pipeline, sin excepciones. Nunca sumar URLs nuevas a esa lista para esquivar un fallo.
- Cualquier edición a mano en el server se pisa con el `reset --hard`: todo cambio va por el repo.
- **Estáticos versionados en producción** (`S3ManifestStaticStorage`): cada estático está dos veces en `static/` del bucket, el original (`base.css`) y el versionado (`base.<hash>.css`). La página usa **solo el versionado**, según `static/staticfiles.json`. Las versiones viejas las borra solo `limpiarestaticos` en cada deploy, así que nunca se acumulan. En `static/` no se borra nada a mano: si se borra un versionado, ese archivo da 404 hasta volver a correr `collectstatic` (Actions → "CI/CD" → Run workflow). En local no aplica: con `DEBUG = True` se sirven sin hash.

### Comandos

Activar el venv primero (Windows: `.\myvenv\Scripts\activate`).

```sh
py manage.py runserver          # usa Base.settingslocal
py manage.py createsuperuser    # para editar contenido desde /admin/
pip install -r requirements.txt
```

```sh
py manage.py test               # tests de humo (Base/Core/tests.py), los mismos que corre el CI
```

Migraciones: solo cuando el usuario lo pide. No hay linter/formatter configurado.

### Foco actual: reestructuración

- **`base.html` es el home y LA base.** Todo el sitio (hero, about, projects, skills, experience, contact, footer) en una sola página con anclas. La única vista vigente es `Home` (`/`) → `base.html`.
- **Diseño:** sale de `base.html` + [resources/static/css/base.css](resources/static/css/base.css) y se replica en todo el resto. Tokens en `:root` de `base.css`:
  `--primary-color: #667eea`, `--secondary-color: #764ba2`, `--dark-bg: #0a0e27`, `--darker-bg: #040613`, `--light-text: #e2e8f0`, `--muted-text: #94a3b8`, `--accent-color: #f59e0b`, `--success-color: #10b981`, `--navbar-height: 70px`.
  Usar siempre estas variables, nunca hardcodear un color nuevo.

### Normas de código

- **Un archivo nuevo = un trío con el mismo nombre:** `resources/templates/X.html` + `resources/static/css/X.css` + `resources/static/js/X.js` (como `base.*`).
- **Lo mínimo hardcodeado.** El texto va en la base de datos y se edita desde el admin, no en el HTML. **Excepción:** los títulos y subtítulos fijos de cada sección (ej. "About Me", "Skills & Technologies" y sus subtítulos) dicen siempre lo mismo y van hardcodeados en el HTML; no se hace un model ni un campo para eso. Ante la duda de si un texto es fijo, preguntar. Al trabajar en cualquier sección, **sugerir proactivamente qué conviene pasar a models**; el usuario espera esa propuesta.
- **Nada de `TextChoices` / `choices=` para listas que pueden crecer** (categorías, tipos, estados): model aparte + `ForeignKey`, así se agregan opciones desde el admin sin tocar código. `choices` solo si el conjunto es fijo por naturaleza.
- **`return render(...)` siempre en una sola línea**, con el contexto inline, por más largo que quede.
- **Nunca dejar un N+1.** Si el template accede a una relación (`{{ obj.fk.campo }}`, `{% for x in obj.hijos.all %}`), la vista la trae de antemano: `select_related()` para FK, `prefetch_related()` para inversas y M2M. Vale también al sumar un campo relacionado a un template existente.
- **Nada de `help_text`.** Las aclaraciones van como comentario `#` en la misma línea del campo (ver "`models.py`" en la Parte 1); si le sirven al usuario en el admin, van en el `verbose_name` (primer argumento posicional).
- **Emails con Redis + Celery, a futuro.** Hoy no hay nada instalado; no agregarlo hasta que se pida.

### Patrones de models/admin

- **Singleton para contenido único** (ej. `AboutMeContent`): `save()` fuerza `pk=1`, expone `load()` (get-or-create); en el admin `has_add_permission` da `False` si ya existe y `has_delete_permission` siempre `False`.
- **Colección ordenada para listas** (ej. `AboutMeStat`, `AboutMeImage`): campo `order` (`PositiveIntegerField`) con `ordering = ('order',)`.
- Los hijos de `Project` (`ProjectImage`, `ProjectTag`, `ProjectLink`) tienen su propio admin, con el proyecto por `raw_id_fields` y filtro dropdown; no son inlines.
- Todo el contenido se administra desde `/admin/`; no hay forms ni CRUD públicos.

### Cosas viejas (no tocar, se borran más adelante)

Siguen ruteadas pero no hay que arreglarlas, mantenerlas ni migrarlas:

- Vistas `Index`, `AboutMe`, `SpaceCommanderInfo`, `GemsCrawlerInfo`, `FinalProjectInfo` en [Base/Core/views.py](Base/Core/views.py).
- URLs `portfolio`, `about-me`, `space-commander-seu`, `gems-crawler`, `final-project` en [Base/Core/urls.py](Base/Core/urls.py).
- Todo `resources/static/img/` (imágenes viejas como static; la excepción a la regla de S3).
- Todos los templates de `resources/templates/` menos `base.html`.
