from django.db import models

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

    def __str__(self):
        return f"{self.description}"