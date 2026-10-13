from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from modeltranslation.admin import TabbedTranslationAdmin
from .models import *

class AboutMeContentAdmin(TabbedTranslationAdmin):
    list_display = ('header', 'id')
    search_fields = ('header',)
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return not AboutMeContent.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False

class AboutMeStatAdmin(TabbedTranslationAdmin):
    list_display = ('value', 'label', 'id', 'order')
    search_fields = ('label',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class AboutMeImageAdmin(TabbedTranslationAdmin):
    list_display = ('description', 'id', 'order')
    search_fields = ('description',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ProjectCategoryAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'id', 'slug', 'order')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ProjectAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'id', 'category', 'order')
    list_filter = (('category', RelatedDropdownFilter),)
    list_select_related = ('category',)
    raw_id_fields = ('category',)
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ProjectImageAdmin(TabbedTranslationAdmin):
    list_display = ('description', 'id', 'project', 'isVideo', 'order')
    list_filter = (('project', RelatedDropdownFilter),)
    list_select_related = ('project',)
    raw_id_fields = ('project',)
    search_fields = ('description', 'project__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('project', 'order')

class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'project', 'order')
    list_filter = (('project', RelatedDropdownFilter),)
    list_select_related = ('project',)
    raw_id_fields = ('project',)
    search_fields = ('name', 'project__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('project', 'order')

class ProjectLinkAdmin(TabbedTranslationAdmin):
    list_display = ('label', 'id', 'project', 'url', 'order')
    list_filter = (('project', RelatedDropdownFilter),)
    list_select_related = ('project',)
    raw_id_fields = ('project',)
    search_fields = ('label', 'project__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('project', 'order')

class SkillLevelAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'id', 'order')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'level', 'percentage', 'order')
    list_filter = (('level', RelatedDropdownFilter),)
    list_select_related = ('level',)
    raw_id_fields = ('level',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ExperienceCategoryAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'id', 'slug', 'icon', 'order')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ExperienceAdmin(TabbedTranslationAdmin):
    list_display = ('role', 'id', 'organization', 'category', 'startdate', 'enddate', 'order')
    list_filter = (('category', RelatedDropdownFilter),)
    list_select_related = ('category',)
    raw_id_fields = ('category',)
    search_fields = ('role', 'organization', 'summary')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('category', 'order')

class ExperienceMetricAdmin(TabbedTranslationAdmin):
    list_display = ('value', 'label', 'id', 'experience', 'order')
    list_filter = (('experience', RelatedDropdownFilter),)
    list_select_related = ('experience',)
    raw_id_fields = ('experience',)
    search_fields = ('label', 'experience__role')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('experience', 'order')

class ExperienceHighlightAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'id', 'experience', 'icon', 'order')
    list_filter = (('experience', RelatedDropdownFilter),)
    list_select_related = ('experience',)
    raw_id_fields = ('experience',)
    search_fields = ('title', 'description', 'experience__role')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('experience', 'order')

class ExperienceHighlightMediaAdmin(TabbedTranslationAdmin):
    list_display = ('label', 'id', 'highlight', 'url', 'order')
    list_filter = (('highlight', RelatedDropdownFilter),)
    list_select_related = ('highlight__experience',)
    raw_id_fields = ('highlight',)
    search_fields = ('label', 'url', 'highlight__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('highlight', 'order')

class ExperienceSkillAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'id', 'experience', 'issoftskill', 'order')
    list_filter = (('experience', RelatedDropdownFilter), ('issoftskill', DropdownFilter))
    list_select_related = ('experience',)
    raw_id_fields = ('experience',)
    search_fields = ('name', 'experience__role')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('experience', 'order')

class ExperienceLinkAdmin(TabbedTranslationAdmin):
    list_display = ('label', 'id', 'experience', 'url', 'order')
    list_filter = (('experience', RelatedDropdownFilter),)
    list_select_related = ('experience',)
    raw_id_fields = ('experience',)
    search_fields = ('label', 'experience__role')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('experience', 'order')

class ExperienceMediaAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'id', 'experience', 'isVideo', 'url', 'order')
    list_filter = (('experience', RelatedDropdownFilter),)
    list_select_related = ('experience',)
    raw_id_fields = ('experience',)
    search_fields = ('title', 'caption', 'url', 'experience__role')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('experience', 'order')

admin.site.register(AboutMeContent, AboutMeContentAdmin)
admin.site.register(AboutMeStat, AboutMeStatAdmin)
admin.site.register(AboutMeImage, AboutMeImageAdmin)
admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectImage, ProjectImageAdmin)
admin.site.register(ProjectTag, ProjectTagAdmin)
admin.site.register(ProjectLink, ProjectLinkAdmin)
admin.site.register(SkillLevel, SkillLevelAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(ExperienceCategory, ExperienceCategoryAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(ExperienceMetric, ExperienceMetricAdmin)
admin.site.register(ExperienceHighlight, ExperienceHighlightAdmin)
admin.site.register(ExperienceHighlightMedia, ExperienceHighlightMediaAdmin)
admin.site.register(ExperienceSkill, ExperienceSkillAdmin)
admin.site.register(ExperienceLink, ExperienceLinkAdmin)
admin.site.register(ExperienceMedia, ExperienceMediaAdmin)