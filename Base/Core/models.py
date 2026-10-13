import re
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'mp4'] # Formatos que aceptan los file de media (ProjectImage, ExperienceMedia)
VIDEO_EXTENSIONS = ['mp4'] # Los que se renderizan como <video>, el resto como <img>

class AboutMeContent(models.Model):
    header = models.CharField("Header", max_length=200, null=False, blank=False)
    paragraph = models.TextField("Paragraph", null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'About Me - Content'
        verbose_name_plural = 'About Me - Content'

    def __str__(self):
        return f"{self.header}"

    # Singleton - Solo existe 1 registro
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

class AboutMeStat(models.Model):
    value = models.CharField("Value", max_length=10, null=False, blank=False)
    label = models.CharField("Label", max_length=50, null=False, blank=False)
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'About Me - Stat'
        verbose_name_plural = 'About Me - Stats'
        ordering = ('order',)

    def __str__(self):
        return f"{self.value} {self.label}"

class AboutMeImage(models.Model):
    image = models.ImageField("Image", upload_to='AboutMe/', null=False, blank=False)
    description = models.CharField("description", max_length=100, null=False, blank=False)
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'About Me - Image'
        verbose_name_plural = 'About Me - Images'
        ordering = ('order',)

    def __str__(self):
        return f"{self.description}"

class ProjectCategory(models.Model):
    name = models.CharField("Name", max_length=50, null=False, blank=False) # Lo que se ve en el botón del filtro, ej: Game Dev
    slug = models.SlugField("Slug", max_length=50, unique=True, null=False, blank=True) # Identificador interno del filtro (el data-filter del front).
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Project - Category'
        verbose_name_plural = 'Project - Categories'
        ordering = ('order',)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Project(models.Model):
    title = models.CharField("Title", max_length=100, null=False, blank=False)
    description = models.TextField("Description", null=False, blank=False)
    category = models.ForeignKey(ProjectCategory, verbose_name="Category", on_delete=models.PROTECT, related_name='projects')
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ('order',)

    def __str__(self):
        return f"{self.title}"

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, verbose_name="Project", on_delete=models.CASCADE, related_name='images')
    file = models.FileField("File (jpg, png, webp, gif, mp4)", upload_to='Projects/', null=True, blank=False, validators=[FileExtensionValidator(MEDIA_EXTENSIONS)]) # Imagen, GIF o video MP4.
    description = models.CharField("Description", max_length=100, null=False, blank=False)
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Project - Image'
        verbose_name_plural = 'Project - Images'
        ordering = ('order',)

    def __str__(self):
        return f"{self.project.title} - {self.description}"

    @property
    def isVideo(self):
        return self.file.name.lower().rsplit('.', 1)[-1] in VIDEO_EXTENSIONS

class ProjectTag(models.Model):
    project = models.ForeignKey(Project, verbose_name="Project", on_delete=models.CASCADE, related_name='tags')
    name = models.CharField("Name", max_length=30, null=False, blank=False)
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Project - Tag'
        verbose_name_plural = 'Project - Tags'
        ordering = ('order',)

    def __str__(self):
        return f"{self.project.title} - {self.name}"

class ProjectLink(models.Model):
    project = models.ForeignKey(Project, verbose_name="Project", on_delete=models.CASCADE, related_name='links')
    label = models.CharField("Label", max_length=30, null=False, blank=False)
    url = models.URLField("URL", max_length=300, null=False, blank=False)
    icon = models.CharField("Icon (ej: fa-brands fa-github)", max_length=50, null=False, blank=False, default='fa-solid fa-link')
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Project - Link'
        verbose_name_plural = 'Project - Links'
        ordering = ('order',)

    def __str__(self):
        return f"{self.project.title} - {self.label}"

class SkillLevel(models.Model):
    name = models.CharField("Name", max_length=30, null=False, blank=False) # Lo que se ve debajo del nombre de la skill, ej: Advanced
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Skill - Level'
        verbose_name_plural = 'Skill - Levels'
        ordering = ('order',)

    def __str__(self):
        return f"{self.name}"

class Skill(models.Model):
    name = models.CharField("Name", max_length=50, null=False, blank=False)
    icon = models.CharField("Icon (ej: fa-brands fa-python)", max_length=50, null=False, blank=False, default='fa-solid fa-code')
    level = models.ForeignKey(SkillLevel, verbose_name="Level", on_delete=models.PROTECT, related_name='skills')
    percentage = models.PositiveSmallIntegerField("Percentage (0-100)", null=False, blank=False, default=50, validators=[MaxValueValidator(100)])
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        ordering = ('order',)

    def __str__(self):
        return f"{self.name}"

class ExperienceCategory(models.Model):
    name = models.CharField("Name", max_length=50, null=False, blank=False) # Lo que se ve en el tab, ej: Work
    slug = models.SlugField("Slug", max_length=50, unique=True, null=False, blank=True) # Identificador interno del tab (el data-target del front).
    icon = models.CharField("Icon (ej: fa-solid fa-briefcase)", max_length=50, null=False, blank=False, default='fa-solid fa-briefcase') # Va en el tab y en el círculo del timeline
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Experience - Category'
        verbose_name_plural = 'Experience - Categories'
        ordering = ('order',)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Experience(models.Model):
    category = models.ForeignKey(ExperienceCategory, verbose_name="Category", on_delete=models.PROTECT, related_name='experiences')
    role = models.CharField("Role", max_length=100, null=False, blank=False)
    organization = models.CharField("Organization", max_length=100, null=False, blank=False)
    logo = models.ImageField("Logo", upload_to='Experience/', null=True, blank=True) # Si está vacío no se muestra
    location = models.CharField("Location", max_length=100, null=False, blank=True)
    startdate = models.DateField("Start date", null=False, blank=False)
    enddate = models.DateField("End date (vacío = Present)", null=True, blank=True) # Vacío muestra "Present" y el badge "Current role"
    summary = models.TextField("Summary", null=False, blank=True)
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'
        ordering = ('order',)

    def __str__(self):
        return f"{self.role} - {self.organization}"

class ExperienceMetric(models.Model):
    experience = models.ForeignKey(Experience, verbose_name="Experience", on_delete=models.CASCADE, related_name='metrics')
    value = models.CharField("Value (ej: 12+)", max_length=10, null=False, blank=False)
    label = models.CharField("Label", max_length=60, null=False, blank=False)
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Experience - Metric'
        verbose_name_plural = 'Experience - Metrics'
        ordering = ('order',)

    def __str__(self):
        return f"{self.experience.role} - {self.value} {self.label}"

class ExperienceHighlight(models.Model):
    experience = models.ForeignKey(Experience, verbose_name="Experience", on_delete=models.CASCADE, related_name='highlights')
    title = models.CharField("Title", max_length=100, null=False, blank=True) # También es el título del modal de imágenes
    description = models.TextField("Description", null=False, blank=False)
    icon = models.CharField("Icon (ej: fa-solid fa-envelope)", max_length=50, null=False, blank=False, default='fa-solid fa-check')
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Experience - Highlight'
        verbose_name_plural = 'Experience - Highlights'
        ordering = ('order',)

    def __str__(self):
        return f"{self.experience.role} - {self.title or self.description[:50]}"

    # Separan la media ya prefetcheada (no hacen queries): las imágenes van todas juntas a un botón que abre el modal, las URLs van cada una en su botón
    @property
    def imageMedia(self):
        return [media for media in self.media.all() if media.image]

    @property
    def urlMedia(self):
        return [media for media in self.media.all() if not media.image]

class ExperienceHighlightMedia(models.Model):
    DEFAULT_URL_ICON = 'fa-solid fa-arrow-up-right-from-square' # El que se pone si cargás una URL sin icon

    highlight = models.ForeignKey(ExperienceHighlight, verbose_name="Highlight", on_delete=models.CASCADE, related_name='media')
    image = models.ImageField("Image", upload_to='Experience/Highlights/', null=True, blank=True) # Todas las imágenes del highlight se ven juntas en un modal con carrusel. Va image o url, no los dos
    url = models.URLField("URL (video, demo, repo, etc.)", max_length=300, null=False, blank=True) # Se muestra como botón chico que abre el link en otra pestaña
    label = models.CharField("Label (texto del botón o descripción de la imagen)", max_length=60, null=False, blank=False)
    icon = models.CharField("Icon, solo para URL (ej: fa-brands fa-youtube)", max_length=50, null=False, blank=True) # Opcional: las imágenes usan siempre fa-images, y una URL sin icon toma DEFAULT_URL_ICON
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Experience - Highlight Media'
        verbose_name_plural = 'Experience - Highlight Media'
        ordering = ('order',)

    def __str__(self):
        return f"{self.highlight} - {self.label}"

    def clean(self):
        if not self.image and not self.url:
            raise ValidationError("Cargá una imagen o una URL.")
        if self.image and self.url:
            raise ValidationError("Cargá una imagen o una URL, no las dos.")

    def save(self, *args, **kwargs):
        if self.url and not self.icon:
            self.icon = self.DEFAULT_URL_ICON
        super().save(*args, **kwargs)

class ExperienceSkill(models.Model):
    experience = models.ForeignKey(Experience, verbose_name="Experience", on_delete=models.CASCADE, related_name='skills')
    name = models.CharField("Name", max_length=50, null=False, blank=False)
    issoftskill = models.BooleanField("Is soft skill", null=False, blank=False, default=False) # Se muestra como tag verde
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Experience - Skill'
        verbose_name_plural = 'Experience - Skills'
        ordering = ('order',)

    def __str__(self):
        return f"{self.experience.role} - {self.name}"

    # Solo las soft skills se traducen solas, las tecnologías se ven igual en todos los idiomas
    @property
    def esTraducible(self):
        return self.issoftskill

class ExperienceLink(models.Model):
    experience = models.ForeignKey(Experience, verbose_name="Experience", on_delete=models.CASCADE, related_name='links')
    label = models.CharField("Label", max_length=40, null=False, blank=False)
    url = models.URLField("URL", max_length=300, null=False, blank=False)
    icon = models.CharField("Icon (ej: fa-solid fa-award)", max_length=50, null=False, blank=False, default='fa-solid fa-arrow-right')
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0) # El primero se muestra como botón principal

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Experience - Link'
        verbose_name_plural = 'Experience - Links'
        ordering = ('order',)

    def __str__(self):
        return f"{self.experience.role} - {self.label}"

class ExperienceMedia(models.Model):
    YOUTUBE_PATTERN = r'(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|live/)|youtu\.be/)([\w-]{11})' # Saca el id del video de cualquier formato de link de YouTube

    experience = models.ForeignKey(Experience, verbose_name="Experience", on_delete=models.CASCADE, related_name='media')
    file = models.FileField("File (jpg, png, webp, gif, mp4)", upload_to='Experience/', null=True, blank=True, validators=[FileExtensionValidator(MEDIA_EXTENSIONS)]) # Imagen, GIF o video MP4. Va file o url, no los dos
    url = models.URLField("URL (YouTube o link externo)", max_length=300, null=False, blank=True) # Si es de YouTube se embebe el video, si no se muestra como card con link
    title = models.CharField("Title", max_length=100, null=False, blank=False)
    caption = models.CharField("Caption", max_length=200, null=False, blank=True)
    order = models.PositiveIntegerField("Order", null=False, blank=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Experience - Media'
        verbose_name_plural = 'Experience - Media'
        ordering = ('order',)

    def __str__(self):
        return f"{self.experience.role} - {self.title}"

    def clean(self):
        if not self.file and not self.url:
            raise ValidationError("Cargá un archivo o una URL.")
        if self.file and self.url:
            raise ValidationError("Cargá un archivo o una URL, no los dos.")

    @property
    def isVideo(self):
        return bool(self.file) and self.file.name.lower().rsplit('.', 1)[-1] in VIDEO_EXTENSIONS

    @property
    def youtubeId(self):
        match = re.search(self.YOUTUBE_PATTERN, self.url)
        return match.group(1) if match else None

    @property
    def urlDomain(self):
        return urlparse(self.url).netloc.removeprefix('www.')

class ContactMessage(models.Model):
    name = models.CharField("Name", max_length=100, null=False, blank=False)
    email = models.EmailField("Email", max_length=254, null=False, blank=False) # Va como Reply-To del email, nunca como remitente (si no, cae en spam)
    subject = models.CharField("Subject", max_length=150, null=False, blank=False)
    message = models.TextField("Message", null=False, blank=False)
    issent = models.BooleanField("Is sent", null=False, blank=False, default=False) # Lo marca la tarea de Celery cuando SES aceptó el email

    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact - Message'
        verbose_name_plural = 'Contact - Messages'
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.name} - {self.subject}"