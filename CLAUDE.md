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

### Settings: dos archivos separados

- `settingslocal.py` (desarrollo) y `settingsproduction.py` (producción), dentro del paquete del proyecto.
- `manage.py`, `wsgi.py` y `asgi.py` apuntan por default a `settingslocal`. Producción se elige con `DJANGO_SETTINGS_MODULE=<Paquete>.settingsproduction`, nunca editando esos archivos.
- Son archivos independientes (no hay un `base.py` común): un cambio que aplica a los dos entornos (apps, middleware, templates, i18n, etc.) se hace en ambos.

### Imágenes y media → siempre AWS S3

- Tanto en local como en producción, las imágenes se suben al bucket de S3. Nunca se guardan en disco.
- Lo maneja `storagemedia.py`: una clase de storage para dev y otra para prod (mismo bucket, distinto prefijo), elegida en `STORAGES["default"]["BACKEND"]` de cada settings.
- Las imágenes van como `ImageField` en un model, que usa el storage default. No se agregan imágenes de contenido como static.

### CI/CD automatizado, siempre

- Commit + push a GitHub, deploy al servidor de producción y dejar todo funcionando tiene que ser un **pipeline automatizado (CI/CD completo)**, no pasos manuales.
- El pipeline se dispara con el push que hace el usuario; esto no habilita a Claude a commitear ni pushear (ver Reglas de trabajo).

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
- El [.env](.env) tiene las variables de local y producción juntas; el bloque de producción está comentado y se descomenta en el servidor.
- App única: `Base/Core` (label `Base.Core` en `INSTALLED_APPS`, `ROOT_URLCONF` y `AppConfig.name`). [Base/urls.py](Base/urls.py) monta `/admin/` y delega el resto a [Base/Core/urls.py](Base/Core/urls.py).
- **Pendiente:** todavía no hay pipeline de CI/CD (no existe `.github/workflows/`).

### Comandos

Activar el venv primero (Windows: `.\myvenv\Scripts\activate`).

```sh
py manage.py runserver          # usa Base.settingslocal
py manage.py createsuperuser    # para editar contenido desde /admin/
pip install -r requirements.txt
```

Migraciones: solo cuando el usuario lo pide. No hay tests (`Base/Core/tests.py` vacío) ni linter/formatter configurado.

### Foco actual: reestructuración

- **`base.html` es el home y LA base.** Todo el sitio (hero, about, projects, skills, experience, contact, footer) en una sola página con anclas. La única vista vigente es `Home` (`/`) → `base.html`.
- **Diseño:** sale de `base.html` + [resources/static/css/base.css](resources/static/css/base.css) y se replica en todo el resto. Tokens en `:root` de `base.css`:
  `--primary-color: #667eea`, `--secondary-color: #764ba2`, `--dark-bg: #0a0e27`, `--darker-bg: #040613`, `--light-text: #e2e8f0`, `--muted-text: #94a3b8`, `--accent-color: #f59e0b`, `--success-color: #10b981`, `--navbar-height: 70px`.
  Usar siempre estas variables, nunca hardcodear un color nuevo.

### Normas de código

- **Un archivo nuevo = un trío con el mismo nombre:** `resources/templates/X.html` + `resources/static/css/X.css` + `resources/static/js/X.js` (como `base.*`).
- **Lo mínimo hardcodeado.** El texto va en la base de datos y se edita desde el admin, no en el HTML. Al trabajar en cualquier sección, **sugerir proactivamente qué conviene pasar a models**; el usuario espera esa propuesta.
- **Nada de `TextChoices` / `choices=` para listas que pueden crecer** (categorías, tipos, estados): model aparte + `ForeignKey`, así se agregan opciones desde el admin sin tocar código. `choices` solo si el conjunto es fijo por naturaleza.
- **`return render(...)` siempre en una sola línea**, con el contexto inline, por más largo que quede.
- **Nunca dejar un N+1.** Si el template accede a una relación (`{{ obj.fk.campo }}`, `{% for x in obj.hijos.all %}`), la vista la trae de antemano: `select_related()` para FK, `prefetch_related()` para inversas y M2M. Vale también al sumar un campo relacionado a un template existente.
- **Nada de `help_text`.** Las aclaraciones van como comentario `#` arriba del campo; si le sirven al usuario en el admin, van en el `verbose_name` (primer argumento posicional).
- **Emails con Redis + Celery, a futuro.** Hoy no hay nada instalado; no agregarlo hasta que se pida.

### Patrones de models/admin

- **Singleton para contenido único** (ej. `AboutMeContent`): `save()` fuerza `pk=1`, expone `load()` (get-or-create); en el admin `has_add_permission` da `False` si ya existe y `has_delete_permission` siempre `False`.
- **Colección ordenada para listas** (ej. `AboutMeStat`, `AboutMeImage`): campo `order` (`PositiveIntegerField`) con `ordering = ('order',)`.
- Todo el contenido se administra desde `/admin/`; no hay forms ni CRUD públicos.

### Cosas viejas (no tocar, se borran más adelante)

Siguen ruteadas pero no hay que arreglarlas, mantenerlas ni migrarlas:

- Vistas `Index`, `AboutMe`, `SpaceCommanderInfo`, `GemsCrawlerInfo`, `FinalProjectInfo` en [Base/Core/views.py](Base/Core/views.py).
- URLs `portfolio`, `about-me`, `space-commander-seu`, `gems-crawler`, `final-project` en [Base/Core/urls.py](Base/Core/urls.py).
- Todo `resources/static/img/` (imágenes viejas como static; la excepción a la regla de S3).
- Todos los templates de `resources/templates/` menos `base.html`.
