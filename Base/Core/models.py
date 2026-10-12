from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

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
    MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'mp4'] # Formatos que acepta file
    VIDEO_EXTENSIONS = ['mp4'] # Los que se renderizan como <video>, el resto como <img>

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
        return self.file.name.lower().rsplit('.', 1)[-1] in self.VIDEO_EXTENSIONS

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