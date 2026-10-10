from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from .models import *

class AboutMeContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'header')
    search_fields = ('title',)
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

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'description', 'order')
    ordering = ('order',)

class ProjectTagInline(admin.TabularInline):
    model = ProjectTag
    extra = 1
    fields = ('name', 'order')
    ordering = ('order',)

class ProjectLinkInline(admin.TabularInline):
    model = ProjectLink
    extra = 1
    fields = ('label', 'url', 'icon', 'order')
    ordering = ('order',)

class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'slug', 'order')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'category', 'order')
    list_filter = (('category', RelatedDropdownFilter),)
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('order',)
    inlines = (ProjectImageInline, ProjectTagInline, ProjectLinkInline)

admin.site.register(AboutMeContent, AboutMeContentAdmin)
admin.site.register(AboutMeStat, AboutMeStatAdmin)
admin.site.register(AboutMeImage, AboutMeImageAdmin)
admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register(Project, ProjectAdmin)