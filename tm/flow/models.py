from django.db import models
from django.conf import settings
from django.utils import timezone


class Workspace(models.Model):
    """Рабочее пространство (Personal / Team)"""
    name = models.CharField(max_length=120, verbose_name="Название")
    description = models.TextField(blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_workspaces"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="workspaces",
        blank=True
    )

    is_personal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Рабочее пространство"
        verbose_name_plural = "Рабочие пространства"
        ordering = ['name']

    def __str__(self):
        return self.name


class Board(models.Model):
    """Доска проекта"""
    title = models.CharField(max_length=150, verbose_name="Название доски")
    description = models.TextField(blank=True, null=True)

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="boards"
    )

    color = models.CharField(max_length=7, default="#8B5CF6")  # hex цвет
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_boards"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Доска"
        verbose_name_plural = "Доски"
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def get_task_count(self):
        """Подсчёт всех задач на доске"""
        return sum(column.tasks.count() for column in self.columns.all())


class Column(models.Model):
    """Колонка на доске"""
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")
    title = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default="#64748B")

    class Meta:
        verbose_name = "Колонка"
        verbose_name_plural = "Колонки"
        ordering = ['order']

    def __str__(self):
        return f"{self.title} — {self.board.title}"


class Label(models.Model):
    """Метки задач"""
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default="#64748B")
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="labels")

    class Meta:
        verbose_name = "Метка"
        verbose_name_plural = "Метки"

    def __str__(self):
        return self.name


class Task(models.Model):
    """Задача"""
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    labels = models.ManyToManyField(Label, blank=True)

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks"
    )

    due_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_priority_color(self):
        colors = {
            'low': 'green-400',
            'medium': 'yellow-400',
            'high': 'red-400'
        }
        return colors.get(self.priority, 'zinc-400')


class Comment(models.Model):
    """Комментарии"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author} → {self.task.title[:40]}"


class Notification(models.Model):
    """Уведомления"""
    TYPE_CHOICES = [
        ('mention', 'Упоминание'),
        ('task_assigned', 'Назначение задачи'),
        ('invite', 'Приглашение'),
        ('comment', 'Новый комментарий'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='mention')
    text = models.TextField()
    link = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type}"