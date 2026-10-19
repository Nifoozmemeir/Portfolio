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
- **Constantes y `choices`: dónde van depende de cuántos models las usan.** Nunca se repite la misma constante en dos models.
  - **Si la usa un solo model** → adentro de ese model, en sus primeras líneas (antes de los campos). Desde los métodos se usa con `self.CONSTANTE`:
    ```python
    class ExperienceMedia(models.Model):
        YOUTUBE_PATTERN = r'...' # Saca el id del video de cualquier link de YouTube

        url = models.URLField(...)
    ```
  - **Si la usan dos o más models** → a nivel módulo, arriba de todo: después de los imports y antes del primer model. Desde los métodos se usa directo, sin `self.`:
    ```python
    from django.db import models

    MEDIA_EXTENSIONS = ['jpg', 'png', 'mp4'] # Formatos que aceptan los file de media (ProjectImage, ExperienceMedia)

    class ProjectImage(models.Model):
        file = models.FileField(..., validators=[FileExtensionValidator(MEDIA_EXTENSIONS)])
    ```
  - Si una constante de un model pasa a usarse en otro, se sube al módulo en ese mismo cambio.
- **Toda `ForeignKey` (y `OneToOneField`) va con `on_delete=models.PROTECT`.** Nunca `CASCADE`: borrar un registro no puede llevarse puesto en silencio todo lo que cuelga de él; para borrar un padre primero se borran (o reasignan) sus hijos. Solo se usa otra opción (`CASCADE`, `SET_NULL`) en un caso excepcional, consultado con el usuario y con el motivo comentado en la misma línea del campo.

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
- **NUNCA una key, contraseña, token o credencial escrita en un archivo que se commitee**, aunque sea de desarrollo, de prueba o "de mentira" (incluye la `SECRET_KEY` de `settingslocal.py` y el CI: la del CI se genera al azar en cada run). Si hace falta una, va al `.env` con su nombre en `.env.example`. Si una ya se subió, se considera pública: se genera una nueva, no alcanza con sacarla.
- El `.env` nunca se commitea.

### `.gitignore` completo

Tiene que cubrir como mínimo: entornos virtuales, `__pycache__`/compilados, `.env` y `.env.*`, configs de editor (`.vscode/`, `.idea/`), `.claude/`, logs, bases locales, `staticfiles/` (collectstatic) y archivos del sistema operativo. Si aparece algo nuevo generado o sensible, se agrega.

### `requirements.txt` siempre actualizado

- Siempre con versiones fijas (`paquete==x.y.z`).
- Las versiones tienen que ser **compatibles con la versión de Python del proyecto** (la del venv). Antes de agregar o subir un paquete, verificar que soporte esa versión: ni demasiado nuevo ni demasiado viejo.
- Al instalar o quitar un paquete, actualizar `requirements.txt` en el mismo cambio.

### Librerías siempre en su última versión

- Todo lo que viene de afuera se mantiene en su **última versión**: las librerías del front por CDN (Bootstrap, Font Awesome, SweetAlert2, etc.) y los paquetes de `requirements.txt`. Una versión vieja trae bugs y faltantes (ej.: íconos de Font Awesome que no existen en una versión anterior).
- **Versiones menores y parches** (5.3.7 → 5.3.8, 7.0 → 7.3) se actualizan directo, al revisar o tocar algo que las usa.
- **Versión mayor** (Bootstrap 5 → 6, Django 5 → 6, etc.) **no se actualiza sola**: puede romper todo. Se avisa al usuario qué cambia y se espera el OK.
- En los CDN, siempre versión exacta (`@7.3.1`, nunca `@latest` ni `@7`) y con `integrity` (SRI) recalculado para la versión nueva, verificado contra el archivo real.
- Los paquetes de Python, además, compatibles con la versión de Python del proyecto (ver arriba).

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
- Cada máquina tiene su propio `.env`; [.env.example](.env.example) es la plantilla con todos los nombres (bloques LOCAL, PROD, AWS, DeepL y Email/Celery/Redis). Variable nueva → se agrega ahí también.
- App única: `Base/Core` (label `Base.Core` en `INSTALLED_APPS`, `ROOT_URLCONF` y `AppConfig.name`). [Base/urls.py](Base/urls.py) monta `/admin/` y delega el resto a [Base/Core/urls.py](Base/Core/urls.py) dentro de `i18n_patterns` (`/` español sin prefijo, `/en/` inglés, `/pt/` portugués).

### Idiomas (es / en / pt)

- **Contenido de la base:** `django-modeltranslation` ([Base/Core/translation.py](Base/Core/translation.py)). Se carga solo en español; al guardar, `traducirAlGuardar` ([Base/Core/traduccion.py](Base/Core/traduccion.py)) completa inglés y portugués con DeepL (`DEEPL_API_KEY`). Lo que falte lo completa `traducircontenido` en cada deploy.
- **Texto fijo de los templates** (`{% translate '...' %}`): vive en `resources/locale/<idioma>/LC_MESSAGES/django.po`. No se usa `makemessages`: después de agregar o cambiar un `{% translate %}` se corre `py manage.py traducirtextos`, que traduce lo nuevo con DeepL y saca lo que ya no se usa (respeta correcciones a mano). Si no se corre, los tests fallan.
- **Los `.mo` no se commitean** (`*.mo` en `.gitignore`): los compilan el CI y `deploy.sh` con `compilemessages`. En Windows no hay gettext, así que en local se compilan con el de WSL (ver Comandos); si el `.mo` local quedó viejo, `testTraduccionesCompiladas` falla solo en la PC.

### Form de contacto: Celery + Redis + AWS SES

- POST por `fetch` a la view `contact` ([Base/Core/views.py](Base/Core/views.py)), validado con `ContactMessageForm` ([Base/Core/forms.py](Base/Core/forms.py)). El HTML del form está escrito a mano en `base.html`: el Django Form solo valida en el back, nunca se renderiza con `{{ form }}` ni hay sticky forms.
- Defensas anti-bots: honeypot (`website`), trampa de tiempo (token firmado, mínimo `SEGUNDOS_MINIMOS`) y límites en Redis (`LIMITE_POR_IP` por hora, `LIMITE_DIARIO` en total). A un bot se le responde `ok` sin guardar nada.
- Guarda el `ContactMessage` (queda siempre en el admin) y encola `enviarEmailContacto` ([Base/Core/tasks.py](Base/Core/tasks.py)), que manda por SES con From `DEFAULT_FROM_EMAIL`, To `CONTACT_EMAIL` y **Reply-To el email del visitante (nunca como remitente)**, y marca `issent`. Si SES falla, Celery reintenta 5 veces con backoff.
- Redis: base 0 = cola de Celery (`CELERY_BROKER_URL`), base 1 = cache (`REDIS_CACHE_URL`, contadores de límite). La app de Celery está en [Base/celery.py](Base/celery.py).
- La IP del visitante sale de `X-Real-IP`, que pone nginx (`include proxy_params`); gunicorn escucha en un socket unix, sin ese header no hay IP.

### Pipeline (jersdev.com en AWS Lightsail)

Cada push a `main` (o "Run workflow" a mano en Actions) dispara [.github/workflows/deploy.yml](.github/workflows/deploy.yml):

1. **Job `test`** (ubuntu-24.04, Python 3.12, Postgres 16 y Redis 7 como services, `DJANGO_SETTINGS_MODULE=Base.settingsproduction` con variables de mentira y `CELERY_TASK_ALWAYS_EAGER=True`, sin worker): `apt-get` de `libpq-dev` y `gettext` → `pip install -r requirements.txt` → `check --deploy --fail-level ERROR` → `makemigrations --check --dry-run` → `migrate` desde cero → `compilemessages` → `manage.py test`.
2. **Job `deploy`** (solo si pasó `test`): entra por SSH (secrets `SSH_KEY`, `SSH_HOST`, `SSH_USER`) y corre la versión de [deploy.sh](deploy.sh) que está en `origin/main`.

[deploy.sh](deploy.sh) en `/var/www/Portfolio` (venv `venv/`): `git reset --hard origin/main` → `pip install` → `check --deploy` → `migrate` → `compilemessages` → `traducircontenido` (DeepL; si falla solo avisa) → `collectstatic` (a S3) → `systemctl restart gunicorn celery` → verifica que `URLS_A_VERIFICAR` (`/`, `/en/`, `/pt/`, `/admin/login/`) respondan 200 y que `redis-server` y `celery` estén activos → `limpiarestaticos` (comando propio en `Base/Core/management/commands/`: borra de `static/` en S3 todo lo que no figura en `staticfiles.json`, o sea versiones viejas con hash y archivos sacados del código; si falla solo avisa). Si algo falla antes de la verificación, rollback automático al commit anterior, reiniciando gunicorn y celery (la base no vuelve atrás).

Servicios del server (Ubuntu 24.04, usuario `ubuntu`): nginx (`/etc/nginx/sites-enabled/portfolio`, certbot) → gunicorn (`gunicorn.service`, socket unix `portfolio.sock`); `redis-server` (apt, solo escucha en `127.0.0.1`); `celery.service` (`venv/bin/celery -A Base worker --concurrency=1`, mismo usuario/grupo y `DJANGO_SETTINGS_MODULE` que gunicorn). Los units de systemd y la instalación de Redis se hicieron a mano en el server y **no están en el repo** (pendiente para cumplir "nada de pasos manuales").

Qué revisar en cada cambio para no romperlo:

- **`config('ALGO')` nuevo en `settingsproduction.py`** → sumarlo al bloque `env:` del job `test` en `deploy.yml` (con valor de mentira) y a `.env.example`, y avisar al usuario que lo cargue en el `.env` del server.
- **Cambio en models** → el CI corre `makemigrations --check`: si falta la migración, falla. Avisar al usuario que tiene que generarla antes de pushear (las migraciones las hace él).
- **Paquete nuevo** → en `requirements.txt` con versión fija; si necesita librerías del sistema para compilar, agregar el `apt-get` en `deploy.yml` y avisar que también hay que instalarlo en el server.
- **URL o página nueva** → que no rompa con la base vacía (los tests corren sin datos). Si la home cambia de ruta o se agrega una página crítica, actualizar `URLS_A_VERIFICAR` en `deploy.sh`.
- **Toda URL que tire 500 corta el pipeline, sin excepciones.** No hay lista de URLs toleradas; no crear una para esquivar un fallo.
- **Servicio nuevo en el server** (otro worker, otro unit de systemd) → sumarlo al `restart` y a la verificación de `deploy.sh` (y al `rollback`), y avisar al usuario que lo cree en el server antes de pushear: si no existe, el deploy hace rollback.
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
py manage.py test               # tests de humo (Base/Core/tests.py), los mismos que corre el CI. Necesita Redis arriba
py manage.py traducirtextos     # después de agregar/cambiar un {% translate %}
wsl msgfmt -o resources/locale/en/LC_MESSAGES/django.mo resources/locale/en/LC_MESSAGES/django.po   # compilar el .mo en local (ídem con pt)
celery -A Base worker -l info --pool=solo   # worker local para probar el envío real (en Windows va --pool=solo)
```

Redis local corre en WSL (Ubuntu 24.04) como servicio, en `127.0.0.1:6379`; arranca solo al abrir Ubuntu (`redis-cli ping` → `PONG`). Los tests usan esa misma Redis y `SmokeContactoTest` le hace `cache.clear()` a la base 1.

Al darle comandos al usuario, decir siempre **en qué terminal** va cada uno: Bash del venv en VS Code (Git Bash, `(myvenv)`), Ubuntu de WSL (Redis) o SSH del server.

Migraciones: solo cuando el usuario lo pide. No hay linter/formatter configurado.

### Foco actual: reestructuración

- **`base.html` es el home y LA base.** Todo el sitio (hero, about, projects, skills, experience, contact, footer) en una sola página con anclas. Las únicas vistas son `home` (`/`) → `base.html` y `contact` (POST del form, responde JSON). No queda nada del sitio viejo: si hace falta otra página, se crea con su trío y su vista nueva.
- **Diseño:** sale de `base.html` + [resources/static/css/base.css](resources/static/css/base.css) y se replica en todo el resto. Tokens en `:root` de `base.css`:
  `--primary-color: #667eea`, `--secondary-color: #764ba2`, `--dark-bg: #0a0e27`, `--darker-bg: #040613`, `--light-text: #e2e8f0`, `--muted-text: #94a3b8`, `--accent-color: #f59e0b`, `--success-color: #10b981`, `--navbar-height: 70px`, `--photo-ratio: 1600 / 739`, `--about-photo-ratio: 4 / 3`.
  Usar siempre estas variables, nunca hardcodear un color nuevo.

### Normas de código

- **Un archivo nuevo = un trío con el mismo nombre:** `resources/templates/X.html` + `resources/static/css/X.css` + `resources/static/js/X.js` (como `base.*`).
- **Lo mínimo hardcodeado.** El texto va en la base de datos y se edita desde el admin, no en el HTML. **Excepción:** los títulos y subtítulos fijos de cada sección (ej. "About Me", "Skills & Technologies" y sus subtítulos) dicen siempre lo mismo y van hardcodeados en el HTML; no se hace un model ni un campo para eso. Ante la duda de si un texto es fijo, preguntar. Al trabajar en cualquier sección, **sugerir proactivamente qué conviene pasar a models**; el usuario espera esa propuesta.
- **Nada de `TextChoices` / `choices=` para listas que pueden crecer** (categorías, tipos, estados): model aparte + `ForeignKey`, así se agregan opciones desde el admin sin tocar código. `choices` solo si el conjunto es fijo por naturaleza.
- **Las imágenes (y videos) dentro de un container se ven SIEMPRE enteras, nunca recortadas**, en cualquier tamaño de pantalla (celular, tablet, notebook, monitor). Si la imagen es más grande o tiene otra proporción que el container, se achica hasta entrar completa: `object-fit: contain` (nunca `cover`), con un fondo de los tokens (`--dark-bg`/`--darker-bg`) en el espacio que sobra. Tampoco efectos que la recorten (ej. `scale()` en hover dentro de un `overflow: hidden`). Vale para todo lo que se agregue: cards, carruseles, modales, logos.
- **Todo recuadro de fotos tiene la proporción de una foto horizontal de WhatsApp (1600×739)**: `aspect-ratio: var(--photo-ratio)` con `width: 100%` y `height: auto`. Nunca un alto fijo en px/vh ni un `max-height`, porque rompen la proporción y dejan espacios vacíos. Así escala igual en cualquier pantalla y esas fotos lo llenan justo. Excepciones: un YouTube embebido usa el 16:9 de su reproductor, y el carrusel de About Me usa `var(--about-photo-ratio)` (4:3) porque lleva fotos de cámara (4608×3456 y 3456×2304). Si otro recuadro necesita otra proporción, se crea un token propio en `:root`, nunca un valor suelto.
- **`return render(...)` siempre en una sola línea**, con el contexto inline, por más largo que quede.
- **Nunca dejar un N+1.** Si el template accede a una relación (`{{ obj.fk.campo }}`, `{% for x in obj.hijos.all %}`), la vista la trae de antemano: `select_related()` para FK, `prefetch_related()` para inversas y M2M. Vale también al sumar un campo relacionado a un template existente.
- **Nada de `help_text`.** Las aclaraciones van como comentario `#` en la misma línea del campo (ver "`models.py`" en la Parte 1); si le sirven al usuario en el admin, van en el `verbose_name` (primer argumento posicional).
- **Emails siempre por Celery** (ver "Form de contacto"): la view guarda y encola con `.delay(pk)` (solo el id), la tarea lee de la base y es idempotente. Nunca mandar un email dentro del request.

### Patrones de models/admin

- **Singleton para contenido único** (hoy no hay ninguno): `save()` fuerza `pk=1`, expone `load()` (get-or-create); en el admin `has_add_permission` da `False` si ya existe y `has_delete_permission` siempre `False`.
- **Colección ordenada para listas** (ej. `AboutMeContent`, que son las slides del carrusel de texto de About Me, `AboutMeStat`, `AboutMeImage`): campo `order` (`PositiveIntegerField`) con `ordering = ('order',)`.
- Los hijos de `Project` (`ProjectImage`, `ProjectTag`, `ProjectLink`) tienen su propio admin, con el proyecto por `raw_id_fields` y filtro dropdown; no son inlines.
- Todo el contenido se administra desde `/admin/`; no hay CRUD público. El único form público es el de contacto, y sus mensajes (`ContactMessage`) son de solo lectura en el admin (`has_add_permission` → `False`, todos los campos en `readonly_fields`).

### Pendientes conocidos

- `resources/static/img/Foto CV 2025.jpg`: la foto del hero sigue como static, en contra de la regla de S3. Hay que pasarla a un `ImageField` (por ejemplo en un singleton nuevo para el hero) y borrar la carpeta `img/`.
- Units de systemd (`celery.service`) e instalación de Redis del server fuera del repo (ver "Pipeline").
