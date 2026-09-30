from django.contrib import admin

from .models import ResearchNote, ResearchPaper, ResearchProject


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    search_fields = ('title', 'description')


@admin.register(ResearchPaper)
class ResearchPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'project', 'publication_year')
    search_fields = ('title', 'authors', 'keywords')
    list_filter = ('project', 'publication_year')


@admin.register(ResearchNote)
class ResearchNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'paper', 'created_at')
    search_fields = ('title', 'content')
