from django.db import models
from django.utils.text import slugify

class AboutMeContent(models.Model):
    title = models.CharField("Title", max_length=50, null=False, blank=False, default='About Me')
    subtitle = models.CharField("Subtitle", max_length=200, null=False, blank=False)
    header = models.CharField("Header", max_length=200, null=False, blank=False)
    paragraph = models.TextField("Paragraph", null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'About Me - Content'
        verbose_name_plural = 'About Me - Content'

    def __str__(self):
        return f"{self.title}"

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
    # Lo que se ve en el botón del filtro, ej: Game Dev
    name = models.CharField("Name", max_length=50, null=False, blank=False)
    # Identificador interno del filtro (el data-filter del front). Si se deja vacío se genera solo desde name en save()
    slug = models.SlugField("Slug", max_length=50, unique=True, null=False, blank=True)
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
    image = models.ImageField("Image", upload_to='Projects/', null=False, blank=False)
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
    # La clase de Font Awesome que se renderiza como <i class="...">
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