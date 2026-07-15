import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Workspace, Board, Task, Column, Label, Notification
from .forms import WorkspaceForm, BoardForm, TaskForm, CommentForm, LabelForm


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_sidebar_boards(user):
    """Получить последние доски для сайдбара (одинаковые на всех страницах)"""
    return Board.objects.filter(
        workspace__owner=user,
        is_archived=False
    ).order_by('-updated_at')[:5]


import re
from django.contrib.auth import get_user_model

User = get_user_model()


def parse_mentions(text):
    """Извлекает список username из текста по @username"""
    if not text:
        return []
    pattern = r'@(\w+)'
    return re.findall(pattern, text)


def create_mention_notifications(task, text, author, notification_type='mention'):
    """Создает уведомления для упомянутых пользователей"""
    mentioned_usernames = parse_mentions(text)

    for username in mentioned_usernames:
        try:
            user = User.objects.get(username=username)
            # Не создавать уведомление для автора
            if user.id == author.id:
                continue

            link = f'/board/{task.column.board.id}/'
            Notification.objects.create(
                user=user,
                type=notification_type,
                text=f'{author.first_name or author.username} упомянул вас в задаче "{task.title}"',
                link=link
            )
        except User.DoesNotExist:
            continue


# ============================================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ФОРМ
# ============================================================


@login_required
def workspace_create(request):
    """Создание рабочего пространства"""
    if request.method == 'POST':
        form = WorkspaceForm(request.POST)
        if form.is_valid():
            workspace = form.save(commit=False)
            workspace.owner = request.user
            workspace.save()
            return redirect('workspace_detail', workspace_id=workspace.id)
    else:
        form = WorkspaceForm()

    return render(request, 'flow/workspace_form.html', {
        'form': form,
        'title': 'Создание рабочего пространства'
    })


@login_required
def workspace_edit(request, workspace_id):
    """Редактирование рабочего пространства"""
    workspace = get_object_or_404(Workspace, id=workspace_id, owner=request.user)

    if request.method == 'POST':
        form = WorkspaceForm(request.POST, instance=workspace)
        if form.is_valid():
            form.save()
            return redirect('workspace_detail', workspace_id=workspace.id)
    else:
        form = WorkspaceForm(instance=workspace)

    return render(request, 'flow/workspace_form.html', {
        'form': form,
        'title': 'Редактирование рабочего пространства'
    })


@login_required
def board_create(request, workspace_id):
    """Создание доски"""
    workspace = get_object_or_404(Workspace, id=workspace_id)

    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.workspace = workspace
            board.created_by = request.user
            board.save()
            return redirect('board_detail', board_id=board.id)
    else:
        form = BoardForm()

    return render(request, 'flow/board_form.html', {
        'form': form,
        'title': 'Создание доски'
    })


@login_required
def board_edit(request, board_id):
    """Редактирование доски"""
    board = get_object_or_404(Board, id=board_id)

    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            return redirect('board_detail', board_id=board.id)
    else:
        form = BoardForm(instance=board)

    return render(request, 'flow/board_form.html', {
        'form': form,
        'title': 'Редактирование доски'
    })


@login_required
def task_create(request, column_id):
    """Создание задачи"""
    column = get_object_or_404(Column, id=column_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.column = column
            task.created_by = request.user
            task.save()
            # ManyToMany нужно сохранить после commit=False
            if form.cleaned_data.get('labels'):
                form.save_m2m()
            return redirect('board_detail', board_id=column.board.id)
    else:
        form = TaskForm()

    return render(request, 'flow/task_form.html', {
        'form': form,
        'title': 'Создание задачи'
    })


@login_required
def task_edit(request, task_id):
    """Редактирование задачи"""
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if form.cleaned_data.get('labels'):
                form.save_m2m()
            return redirect('board_detail', board_id=task.column.board.id)
    else:
        form = TaskForm(instance=task)

    return render(request, 'flow/task_form.html', {
        'form': form,
        'title': 'Редактирование задачи'
    })


@login_required
def task_comment(request, task_id):
    """Добавление комментария к задаче"""
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()

            # Создаем уведомления для @mentions в комментарии
            create_mention_notifications(task, comment.text, request.user, 'comment')

            return redirect('task_detail', task_id=task.id)
    else:
        form = CommentForm()

    return render(request, 'flow/comment_form.html', {
        'form': form,
        'title': 'Добавить комментарий'
    })

def index(request):
    context = {'title': 'Главная',}
    return render(request, 'flow/index.html', context)

@login_required
def home(request):
    # Получаем параметр workspace из URL
    workspace_param = request.GET.get('workspace', 'personal')

    # Фильтруем доски по workspace
    if workspace_param == 'personal':
        boards = Board.objects.filter(
            workspace__owner=request.user,
            workspace__is_personal=True,
            is_archived=False
        ).order_by('-updated_at')[:4]
    elif workspace_param == 'team':
        boards = Board.objects.filter(
            workspace__owner=request.user,
            workspace__is_personal=False,
            is_archived=False
        ).order_by('-updated_at')[:4]
    else:
        try:
            workspace_id = int(workspace_param)
            boards = Board.objects.filter(
                workspace__owner=request.user,
                workspace__id=workspace_id,
                is_archived=False
            ).order_by('-updated_at')[:4]
        except ValueError:
            boards = Board.objects.filter(
                workspace__owner=request.user,
                is_archived=False
            ).order_by('-updated_at')[:4]

    context = {
        'title': 'Главная',
        'boards': boards,
        'sidebar_boards': get_sidebar_boards(request.user),
        'current_workspace': workspace_param
    }
    return render(request, 'flow/home.html', context)

@login_required
def dashboard(request):
    workspace_param = request.GET.get('workspace', 'personal')
    sort_by = request.GET.get('sort', 'updated')

    # Определяем поле для сортировки
    if sort_by == 'created':
        order_by = '-created_at'
    elif sort_by == 'alpha':
        order_by = 'title'
    else:
        order_by = '-updated_at'

    if workspace_param == 'personal':
        boards = Board.objects.filter(
            workspace__owner=request.user,
            workspace__is_personal=True,
            is_archived=False
        ).order_by(order_by)
    elif workspace_param == 'team':
        boards = Board.objects.filter(
            workspace__owner=request.user,
            workspace__is_personal=False,
            is_archived=False
        ).order_by(order_by)
    else:
        try:
            workspace_id = int(workspace_param)
            boards = Board.objects.filter(
                workspace__owner=request.user,
                workspace__id=workspace_id,
                is_archived=False
            ).order_by(order_by)
        except ValueError:
            boards = Board.objects.filter(
                workspace__owner=request.user,
                is_archived=False
            ).order_by(order_by)

    workspaces = Workspace.objects.filter(owner=request.user)[:10]
    context = {
        'title': 'Доски',
        'boards': boards,
        'workspaces': workspaces,
        'sidebar_boards': get_sidebar_boards(request.user),
        'current_workspace': workspace_param,
        'sort_by': sort_by
    }
    return render(request, 'flow/dashboard.html', context)

@login_required
def board(request, board_id=None):
    user = request.user

    # Загружаем доску с колонками и задачами (фильтр по пользователю)
    if board_id:
        board_obj = Board.objects.filter(id=board_id, workspace__owner=user).first()
    else:
        # Первая доска пользователя
        board_obj = Board.objects.filter(workspace__owner=user).first()

    # Если доски нет - создаём демо-данные для текущего пользователя
    if not board_obj:
        # Создаём рабочее пространство
        workspace = Workspace.objects.create(
            name='Мои задачи',
            owner=user,
            is_personal=True
        )

        # Создаём доску
        board_obj = Board.objects.create(
            title='Разработка TeamFlow',
            description='Основная доска проекта',
            color='#8B5CF6',
            workspace=workspace,
            created_by=user
        )

        # Создаём колонки
        Column.objects.create(board=board_obj, title='To Do', order=0, color='#64748B')
        Column.objects.create(board=board_obj, title='In Progress', order=1, color='#3B82F6')
        Column.objects.create(board=board_obj, title='Review', order=2, color='#F59E0B')
        Column.objects.create(board=board_obj, title='Done', order=3, color='#10B981')

    if board_obj:
        columns = board_obj.columns.prefetch_related('tasks').order_by('order')
    else:
        columns = []

    context = {
        'title': 'Доски',
        'board': board_obj,
        'columns': columns,
        'sidebar_boards': get_sidebar_boards(request.user)
    }
    return render(request, 'flow/board.html', context)

@login_required
def favorites(request):
    favorite_boards = Board.objects.filter(
        workspace__owner=request.user,
        is_favorite=True,
        is_archived=False
    ).order_by('-updated_at')
    context = {
        'title': 'Избранное',
        'boards': favorite_boards,
        'urgent_tasks': [],
        'sidebar_boards': get_sidebar_boards(request.user)
    }
    return render(request, 'flow/favorites.html', context)

@login_required
def profile(request):
    context = {
        'title': 'Профиль',
        'sidebar_boards': get_sidebar_boards(request.user)
    }
    return render(request, 'flow/profile.html', context)

@login_required
def archive(request):
    archived_boards = Board.objects.filter(
        workspace__owner=request.user,
        is_archived=True
    ).order_by('-updated_at')
    context = {
        'title': 'Архив',
        'boards': archived_boards,
        'sidebar_boards': get_sidebar_boards(request.user)
    }
    return render(request, 'flow/archive.html', context)


# ============================================================
# API VIEWS (JSON)
# ============================================================

from django.contrib.auth import get_user_model
User = get_user_model()


@csrf_exempt
def api_user_search(request):
    """API: Поиск пользователей"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'success': True, 'users': []})

    # Ищем пользователей по username или email
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]

    users_data = [{
        'id': user.id,
        'username': user.username,
        'name': user.get_full_name() or user.username,
        'email': user.email,
    } for user in users]

    return JsonResponse({'success': True, 'users': users_data})


@csrf_exempt
def api_boards_list(request):
    """API: Получение списка досок для выбранного workspace"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

    workspace_param = request.GET.get('workspace', 'personal')

    # Фильтруем по workspace
    if workspace_param == 'personal':
        boards = Board.objects.filter(workspace__owner=request.user, workspace__is_personal=True)
    elif workspace_param == 'team':
        boards = Board.objects.filter(workspace__owner=request.user, workspace__is_personal=False)
    else:
        # Если передан ID workspace
        try:
            workspace_id = int(workspace_param)
            boards = Board.objects.filter(workspace__id=workspace_id, workspace__owner=request.user)
        except ValueError:
            boards = Board.objects.filter(workspace__owner=request.user)

    boards_data = [{
        'id': board.id,
        'title': board.title,
        'color': board.color,
        'is_favorite': board.is_favorite,
        'is_archived': board.is_archived,
        'task_count': board.get_task_count(),
        'workspace_id': board.workspace.id,
        'workspace_is_personal': board.workspace.is_personal
    } for board in boards]

    return JsonResponse({'success': True, 'boards': boards_data})


def api_board_create(request):
    """API: Создание доски"""""
    if request.method == 'POST':
        # Проверяем аутентификацию
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

        try:
            data = json.loads(request.body)
            user = request.user

            # Пытаемся найти workspace
            workspace_id = data.get('workspace')
            workspace_name = data.get('workspace_name', 'My Workspace')

            # Обрабатываем 'personal' как специальный тип
            if workspace_id == 'personal' or workspace_id == 'team':
                workspace = Workspace.objects.filter(
                    owner=user,
                    is_personal=(workspace_id == 'personal')
                ).first()
                if not workspace:
                    workspace = Workspace.objects.create(
                        name=workspace_name,
                        owner=user,
                        is_personal=(workspace_id == 'personal')
                    )
            elif workspace_id:
                try:
                    workspace = Workspace.objects.get(id=int(workspace_id), owner=user)
                except (Workspace.DoesNotExist, ValueError):
                    return JsonResponse({'success': False, 'error': 'Рабочее пространство не найдено'}, status=404)
            else:
                # Создаём рабочее пространство по умолчанию
                workspace = Workspace.objects.filter(owner=user, is_personal=True).first()
                if not workspace:
                    workspace = Workspace.objects.create(
                        name='My Workspace',
                        owner=user,
                        is_personal=True
                    )

            board = Board.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                color=data.get('color', '#8B5CF6'),
                workspace=workspace,
                created_by=user
            )

            # Создаём колонки по умолчанию
            Column.objects.create(board=board, title='To Do', order=0, color='#64748B')
            Column.objects.create(board=board, title='In Progress', order=1, color='#3B82F6')
            Column.objects.create(board=board, title='Review', order=2, color='#F59E0B')
            Column.objects.create(board=board, title='Done', order=3, color='#10B981')

            return JsonResponse({
                'success': True,
                'board': {
                    'id': board.id,
                    'title': board.title,
                    'color': board.color
                }
            })
        except Exception as e:
            import traceback
            return JsonResponse({'success': False, 'error': str(e), 'trace': traceback.format_exc()}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_task_create(request):
    """API: Создание задачи"""
    if request.method == 'POST':
        # Проверяем аутентификацию
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

        try:
            data = json.loads(request.body)

            user = request.user

            column_id = data.get('column_id')

            # Пытаемся найти колонку, принадлежащую пользователю
            try:
                column = Column.objects.get(id=column_id, board__workspace__owner=user)
            except Column.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Колонка не найдена'}, status=404)

            task = Task.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                priority=data.get('priority', 'medium'),
                column=column,
                created_by=user
            )

            # Создаем уведомления для @mentions в описании
            if data.get('description'):
                create_mention_notifications(task, data.get('description'), user)

            return JsonResponse({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'priority': task.priority
                }
            })
        except Exception as e:
            import traceback
            return JsonResponse({'success': False, 'error': str(e), 'trace': traceback.format_exc()}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_workspace_create(request):
    """API: Создание рабочего пространства"""
    if request.method == 'POST':
        # Проверяем аутентификацию
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

        try:
            data = json.loads(request.body)

            user = request.user

            workspace = Workspace.objects.create(
                name=data.get('name'),
                description=data.get('description', ''),
                is_personal=data.get('is_personal', False),
                owner=user
            )

            return JsonResponse({
                'success': True,
                'workspace': {
                    'id': workspace.id,
                    'name': workspace.name,
                    'is_personal': workspace.is_personal
                }
            })
        except Exception as e:
            import traceback
            return JsonResponse({'success': False, 'error': str(e), 'trace': traceback.format_exc()}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_board_delete(request, board_id):
    """API: Удаление доски"""
    if request.method == 'POST' or request.method == 'DELETE':
        # Проверяем аутентификацию
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

        try:
            board = Board.objects.get(id=board_id, workspace__owner=request.user)
            board_title = board.title
            board.delete()
            return JsonResponse({
                'success': True,
                'message': f'Доска "{board_title}" удалена'
            })
        except Board.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Доска не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_board_favorite(request, board_id):
    """API: Переключение избранного"""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

        try:
            board = Board.objects.get(id=board_id, workspace__owner=request.user)
            board.is_favorite = not board.is_favorite
            board.save()
            return JsonResponse({
                'success': True,
                'is_favorite': board.is_favorite,
                'message': 'Добавлено в избранное' if board.is_favorite else 'Убрано из избранного'
            })
        except Board.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Доска не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_board_archive(request, board_id):
    """API: Архивирование/разархивирование доски"""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

        try:
            board = Board.objects.get(id=board_id, workspace__owner=request.user)
            board.is_archived = not board.is_archived
            board.save()
            return JsonResponse({
                'success': True,
                'is_archived': board.is_archived,
                'message': 'Доска архивирована' if board.is_archived else 'Доска восстановлена'
            })
        except Board.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Доска не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


# ============================================================
# NOTIFICATIONS API
# ============================================================

@login_required
def api_notifications_list(request):
    """API: Получение списка уведомлений пользователя"""
    notifications = Notification.objects.filter(user=request.user)[:20]

    notifications_data = [{
        'id': n.id,
        'type': n.type,
        'text': n.text,
        'link': n.link,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications]

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return JsonResponse({
        'success': True,
        'notifications': notifications_data,
        'unread_count': unread_count
    })


@login_required
def api_notifications_read(request, notification_id):
    """API: Пометка уведомления как прочитанного"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Уведомление не найдено'}, status=404)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@login_required
def api_notifications_read_all(request):
    """API: Пометка всех уведомлений как прочитанных"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
