from django import forms
from .models import Workspace, Board, Column, Task, Label, Comment


class WorkspaceForm(forms.ModelForm):
    """Форма для создания и редактирования рабочего пространства"""

    class Meta:
        model = Workspace
        fields = ['name', 'description', 'is_personal']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Введите название рабочего пространства',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Описание (необязательно)',
            }),
            'is_personal': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-purple-600 rounded focus:ring-purple-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Название"
        self.fields['description'].label = "Описание"
        self.fields['is_personal'].label = "Личное пространство"


class BoardForm(forms.ModelForm):
    """Форма для создания и редактирования доски"""

    class Meta:
        model = Board
        fields = ['title', 'description', 'color', 'is_favorite']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Название доски',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Описание доски (необязательно)',
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-12 h-12 rounded-lg cursor-pointer border-2 border-gray-200',
                'type': 'color',
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-purple-600 rounded focus:ring-purple-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Название доски"
        self.fields['description'].label = "Описание"
        self.fields['color'].label = "Цвет"
        self.fields['is_favorite'].label = "Добавить в избранное"


class ColumnForm(forms.ModelForm):
    """Форма для создания и редактирования колонки"""

    class Meta:
        model = Column
        fields = ['title', 'order', 'color']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Название колонки',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-10 h-10 rounded-lg cursor-pointer border-2 border-gray-200',
                'type': 'color',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Название"
        self.fields['order'].label = "Порядок"
        self.fields['color'].label = "Цвет"


class LabelForm(forms.ModelForm):
    """Форма для создания и редактирования метки"""

    class Meta:
        model = Label
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Название метки',
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-10 h-10 rounded-lg cursor-pointer border-2 border-gray-200',
                'type': 'color',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Название"
        self.fields['color'].label = "Цвет"


class TaskForm(forms.ModelForm):
    """Форма для создания и редактирования задачи"""

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'labels',
            'assignee', 'due_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Название задачи',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Описание задачи',
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white',
            }),
            'labels': forms.CheckboxSelectMultiple(attrs={
                'class': 'flex flex-wrap gap-2',
            }),
            'assignee': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white',
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Название"
        self.fields['description'].label = "Описание"
        self.fields['priority'].label = "Приоритет"
        self.fields['labels'].label = "Метки"
        self.fields['assignee'].label = "Исполнитель"
        self.fields['due_date'].label = "Срок выполнения"


class TaskCreateForm(forms.ModelForm):
    """Упрощённая форма создания задачи"""

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Что нужно сделать?',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Подробнее о задаче (необязательно)',
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Название"
        self.fields['description'].label = "Описание"
        self.fields['priority'].label = "Приоритет"


class CommentForm(forms.ModelForm):
    """Форма для комментариев"""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Напишите комментарий...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = "Комментарий"