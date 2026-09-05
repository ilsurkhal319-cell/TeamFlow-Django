from django.contrib import admin
from .models import Workspace, Board, Column, Task, Label, Comment


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'workspace', 'color', 'is_favorite', 'is_archived', 'created_by', 'updated_at')
    list_filter = ('is_favorite', 'is_archived', 'workspace')
    search_fields = ('title', 'description')
    raw_id_fields = ('created_by',)
    filter_horizontal = ('members',)


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'order')
    list_filter = ('board',)
    ordering = ('board', 'order')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'column', 'priority', 'assignee', 'due_date', 'order')
    list_filter = ('priority', 'column__board', 'due_date')
    search_fields = ('title', 'description')
    raw_id_fields = ('assignee', 'created_by')


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'board')
    list_filter = ('board',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'task', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text',)
