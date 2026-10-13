"""
Qué campos de cada model se traducen. django-modeltranslation crea por cada uno las columnas _es, _en y _pt,
y {{ obj.campo }} devuelve la del idioma activo (si está vacía, la de español).
El español se carga a mano en el admin; el inglés y el portugués los completa solo traduccion.py al guardar.

No se registran los nombres de tecnologías (ProjectTag, Skill): se ven igual en todos los idiomas y traducirlos solo gastaría cupo.
"""
from modeltranslation.translator import translator, TranslationOptions
from .models import AboutMeContent, AboutMeStat, AboutMeImage, ProjectCategory, Project, ProjectImage, ProjectLink, SkillLevel, ExperienceCategory, Experience, ExperienceMetric, ExperienceHighlight, ExperienceHighlightMedia, ExperienceSkill, ExperienceLink, ExperienceMedia

class AboutMeContentTranslation(TranslationOptions):
    fields = ('header', 'paragraph')

class AboutMeStatTranslation(TranslationOptions):
    fields = ('label',)

class AboutMeImageTranslation(TranslationOptions):
    fields = ('description',)

class ProjectCategoryTranslation(TranslationOptions):
    fields = ('name',)

class ProjectTranslation(TranslationOptions):
    fields = ('title', 'description')

class ProjectImageTranslation(TranslationOptions):
    fields = ('description',)

class ProjectLinkTranslation(TranslationOptions):
    fields = ('label',)

class SkillLevelTranslation(TranslationOptions):
    fields = ('name',)

class ExperienceCategoryTranslation(TranslationOptions):
    fields = ('name',)

class ExperienceTranslation(TranslationOptions):
    fields = ('role', 'location', 'summary')

class ExperienceMetricTranslation(TranslationOptions):
    fields = ('label',)

class ExperienceHighlightTranslation(TranslationOptions):
    fields = ('title', 'description')

class ExperienceHighlightMediaTranslation(TranslationOptions):
    fields = ('label',)

class ExperienceSkillTranslation(TranslationOptions):
    fields = ('name',) # Solo se traducen las soft skills (ver ExperienceSkill.esTraducible)

class ExperienceLinkTranslation(TranslationOptions):
    fields = ('label',)

class ExperienceMediaTranslation(TranslationOptions):
    fields = ('title', 'caption')

translator.register(AboutMeContent, AboutMeContentTranslation)
translator.register(AboutMeStat, AboutMeStatTranslation)
translator.register(AboutMeImage, AboutMeImageTranslation)
translator.register(ProjectCategory, ProjectCategoryTranslation)
translator.register(Project, ProjectTranslation)
translator.register(ProjectImage, ProjectImageTranslation)
translator.register(ProjectLink, ProjectLinkTranslation)
translator.register(SkillLevel, SkillLevelTranslation)
translator.register(ExperienceCategory, ExperienceCategoryTranslation)
translator.register(Experience, ExperienceTranslation)
translator.register(ExperienceMetric, ExperienceMetricTranslation)
translator.register(ExperienceHighlight, ExperienceHighlightTranslation)
translator.register(ExperienceHighlightMedia, ExperienceHighlightMediaTranslation)
translator.register(ExperienceSkill, ExperienceSkillTranslation)
translator.register(ExperienceLink, ExperienceLinkTranslation)
translator.register(ExperienceMedia, ExperienceMediaTranslation)