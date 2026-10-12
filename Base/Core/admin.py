from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from .models import *

class AboutMeContentAdmin(admin.ModelAdmin):
    list_display = ('header', 'id')
    search_fields = ('header',)
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return not AboutMeContent.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False

class AboutMeStatAdmin(admin.ModelAdmin):
    list_display = ('value', 'label', 'id', 'order')
    search_fields = ('label',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class AboutMeImageAdmin(admin.ModelAdmin):
    list_display = ('description', 'id', 'order')
    search_fields = ('description',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'slug', 'order')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'category', 'order')
    list_filter = (('category', RelatedDropdownFilter),)
    list_select_related = ('category',)
    raw_id_fields = ('category',)
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ProjectImageAdmin(admin.ModelAdmin):
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

class ProjectLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'id', 'project', 'url', 'order')
    list_filter = (('project', RelatedDropdownFilter),)
    list_select_related = ('project',)
    raw_id_fields = ('project',)
    search_fields = ('label', 'project__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('project', 'order')

class SkillLevelAdmin(admin.ModelAdmin):
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