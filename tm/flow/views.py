import json
import logging
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages
from .models import Workspace, Board, Task, Column, Label, Notification
from .forms import WorkspaceForm, BoardForm, TaskForm, CommentForm, LabelForm
from .services import create_mention_notifications
from users.forms import UserProfileForm
import re
from django.contrib.auth import get_user_model
from django.utils import timezone

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_sidebar_boards(user):
    """Получить последние доски для сайдбара (одинаковые на всех страницах)"""
    return Board.objects.filter(
        Q(workspace__owner=user) | Q(members=user),
        is_archived=False,
    ).distinct().order_by('-updated_at')[:5]


def get_user_boards(user, **filters):
    """Доски, доступные владельцу или участнику."""
    return Board.objects.filter(
        Q(workspace__owner=user) | Q(members=user),
        **filters,
    ).distinct()


def get_main_workspace(user):
    return Workspace.objects.get_or_create(
        owner=user,
        name='Main',
    )[0]


def get_selected_workspace(user, value):
    if value in (None, '', 'main'):
        return get_main_workspace(user)
    if value == 'all':
        return None
    try:
        return Workspace.objects.filter(
            Q(owner=user) | Q(boards__members=user),
            id=int(value),
        ).distinct().get()
    except (Workspace.DoesNotExist, TypeError, ValueError):
        return get_main_workspace(user)


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
    preview_board = None
    if request.user.is_authenticated:
        preview_board = get_user_boards(
            request.user,
            is_archived=False,
        ).order_by('-updated_at').first()
    context = {'title': 'Главная', 'preview_board': preview_board}
    return render(request, 'flow/index.html', context)

@login_required
def home(request):
    workspace = get_selected_workspace(request.user, request.GET.get('workspace'))
    boards = get_user_boards(request.user, is_archived=False)
    if workspace is not None:
        boards = boards.filter(workspace=workspace)
    boards = boards.order_by('-updated_at')[:4]
    workspace_param = 'all' if workspace is None else str(workspace.id)

    context = {
        'title': 'Главная',
        'boards': boards,
        'sidebar_boards': get_sidebar_boards(request.user),
        'current_workspace': workspace_param
    }
    return render(request, 'flow/home.html', context)

@login_required
def dashboard(request):
    workspace = get_selected_workspace(request.user, request.GET.get('workspace'))
    sort_by = request.GET.get('sort', 'updated')

    # Определяем поле для сортировки
    if sort_by == 'created':
        order_by = '-created_at'
    elif sort_by == 'alpha':
        order_by = 'title'
    else:
        order_by = '-updated_at'

    boards = get_user_boards(request.user, is_archived=False)
    if workspace is not None:
        boards = boards.filter(workspace=workspace)
    boards = boards.order_by(order_by)

    workspaces = Workspace.objects.filter(
        Q(owner=request.user) | Q(boards__members=request.user)
    ).distinct().order_by('name')
    workspace_param = 'all' if workspace is None else str(workspace.id)
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
        board_obj = get_object_or_404(get_user_boards(user), id=board_id)
    else:
        # Первая доска пользователя
        board_obj = get_user_boards(user).first()

    # Если доски нет - создаём демо-данные для текущего пользователя
    if not board_obj:
        # Создаём рабочее пространство
        workspace = get_main_workspace(user)

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
    favorite_boards = get_user_boards(
        request.user,
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
    if request.method == 'POST':
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Профиль сохранён.')
            return redirect('flow:profile')
    else:
        profile_form = UserProfileForm(instance=request.user)

    all_user_boards = get_user_boards(
        request.user,
    ).select_related('workspace', 'created_by').order_by('-updated_at')
    user_boards = all_user_boards.filter(is_archived=False)
    user_tasks = Task.objects.filter(
        Q(assignee=request.user) | Q(created_by=request.user),
        Q(column__board__workspace__owner=request.user) |
        Q(column__board__members=request.user),
    ).select_related('column__board').distinct().order_by('-updated_at')
    completed_titles = {'done', 'готово', 'завершено', 'completed'}
    today = timezone.localdate()
    completed_task_count = 0
    for task in user_tasks:
        if task.column.title.casefold() in completed_titles:
            task.profile_status = 'completed'
            task.profile_status_label = 'Завершена'
            completed_task_count += 1
        elif task.due_date and task.due_date < today:
            task.profile_status = 'overdue'
            task.profile_status_label = 'Просрочена'
        else:
            task.profile_status = 'active'
            task.profile_status_label = 'В работе'

    workspaces = Workspace.objects.filter(
        Q(owner=request.user) | Q(boards__members=request.user)
    ).distinct().annotate(
        active_board_count=Count('boards', filter=Q(boards__is_archived=False)),
    ).order_by('name')
    recent_activity = [
        {
            'kind': 'board',
            'title': board.title,
            'date': board.updated_at,
            'url_id': board.id,
        }
        for board in user_boards[:5]
    ]
    recent_activity.extend(
        {
            'kind': 'task',
            'title': task.title,
            'date': task.updated_at,
            'url_id': task.column.board_id,
        }
        for task in user_tasks[:5]
    )
    recent_activity.sort(key=lambda item: item['date'], reverse=True)
    context = {
        'title': 'Профиль',
        'sidebar_boards': get_sidebar_boards(request.user),
        'profile_form': profile_form,
        'board_count': user_boards.count(),
        'task_count': user_tasks.count(),
        'completed_task_count': completed_task_count,
        'workspaces': workspaces,
        'profile_boards': all_user_boards[:30],
        'recent_boards': user_boards[:4],
        'profile_tasks': user_tasks[:30],
        'recent_activity': recent_activity[:8],
    }
    return render(request, 'flow/profile.html', context)

@login_required
def archive(request):
    archived_boards = get_user_boards(
        request.user,
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
logger = logging.getLogger(__name__)


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


@login_required
def api_board_member_add(request, board_id):
    """Добавить пользователя на доску. Управлять составом может владелец workspace."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    board = get_object_or_404(Board, id=board_id, workspace__owner=request.user)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError
        user_id = int(data.get('user_id'))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)

    member = get_object_or_404(User, id=user_id)
    if member.id == request.user.id:
        return JsonResponse({'success': False, 'error': 'Владелец уже имеет доступ'}, status=400)

    board.members.add(member)
    Notification.objects.create(
        user=member,
        type='invite',
        text=f'Вас добавили на доску «{board.title}»',
        link=f'/board/{board.id}/',
    )
    return JsonResponse({
        'success': True,
        'message': f'@{member.username} добавлен на доску',
    })


@login_required
def api_board_join(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError
        code = str(data.get('code', '')).strip().upper()
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)

    if not code:
        return JsonResponse({'success': False, 'error': 'Введите код доски'}, status=400)

    board = get_object_or_404(Board, join_code=code)
    if board.is_archived:
        return JsonResponse({'success': False, 'error': 'Эта доска находится в архиве'}, status=400)
    if board.workspace.owner_id == request.user.id or board.members.filter(id=request.user.id).exists():
        return JsonResponse({
            'success': True,
            'message': 'У вас уже есть доступ к этой доске',
            'board_id': board.id,
        })

    board.members.add(request.user)
    Notification.objects.create(
        user=board.workspace.owner,
        type='invite',
        text=f'{request.user.username} присоединился к доске «{board.title}»',
        link=f'/board/{board.id}/',
    )
    return JsonResponse({
        'success': True,
        'message': f'Вы присоединились к доске «{board.title}»',
        'board_id': board.id,
    })


def api_boards_list(request):
    """API: Получение списка досок для выбранного workspace"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

    workspace = get_selected_workspace(request.user, request.GET.get('workspace'))
    boards = get_user_boards(request.user)
    if workspace is not None:
        boards = boards.filter(workspace=workspace)

    boards_data = [{
        'id': board.id,
        'title': board.title,
        'color': board.color,
        'is_favorite': board.is_favorite,
        'is_archived': board.is_archived,
        'task_count': board.get_task_count(),
        'workspace_id': board.workspace.id,
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
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)

        if not isinstance(data, dict):
            return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)

        title = str(data.get('title', '')).strip()
        if not title:
            return JsonResponse({'success': False, 'error': 'Введите название доски'}, status=400)
        if len(title) > 150:
            return JsonResponse({'success': False, 'error': 'Название доски слишком длинное'}, status=400)

        try:
            user = request.user

            # Пытаемся найти workspace
            workspace_id = data.get('workspace')

            if workspace_id in (None, '', 'main'):
                workspace = get_main_workspace(user)
            else:
                try:
                    workspace = Workspace.objects.get(id=int(workspace_id), owner=user)
                except (Workspace.DoesNotExist, ValueError):
                    return JsonResponse({'success': False, 'error': 'Рабочее пространство не найдено'}, status=404)

            board = Board.objects.create(
                title=title,
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
        except Exception:
            logger.exception('Не удалось создать доску')
            return JsonResponse({'success': False, 'error': 'Не удалось создать доску'}, status=500)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


def api_task_create(request):
    """API: Создание задачи"""
    if request.method == 'POST':
        # Проверяем аутентификацию
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)

        if not isinstance(data, dict):
            return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)

        title = str(data.get('title', '')).strip()
        if not title:
            return JsonResponse({'success': False, 'error': 'Введите название задачи'}, status=400)
        if len(title) > 200:
            return JsonResponse({'success': False, 'error': 'Название задачи слишком длинное'}, status=400)

        priority = data.get('priority', 'medium')
        if priority not in dict(Task.PRIORITY_CHOICES):
            return JsonResponse({'success': False, 'error': 'Некорректный приоритет'}, status=400)

        try:
            user = request.user

            column_id = data.get('column_id')

            # Пытаемся найти колонку, принадлежащую пользователю
            try:
                column = Column.objects.filter(
                    Q(board__workspace__owner=user) | Q(board__members=user),
                    id=column_id,
                ).distinct().get()
            except Column.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Колонка не найдена'}, status=404)

            task = Task.objects.create(
                title=title,
                description=data.get('description', ''),
                priority=priority,
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
        except Exception:
            logger.exception('Не удалось создать задачу')
            return JsonResponse({'success': False, 'error': 'Не удалось создать задачу'}, status=500)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


def api_workspace_create(request):
    """API: Создание рабочего пространства"""
    if request.method == 'POST':
        # Проверяем аутентификацию
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)

        if not isinstance(data, dict):
            return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)

        name = str(data.get('name', '')).strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Введите название рабочего пространства'}, status=400)
        if len(name) > 120:
            return JsonResponse({'success': False, 'error': 'Название рабочего пространства слишком длинное'}, status=400)

        try:
            user = request.user
            workspace = Workspace.objects.create(
                name=name,
                description=data.get('description', ''),
                owner=user
            )

            return JsonResponse({
                'success': True,
                'workspace': {
                    'id': workspace.id,
                    'name': workspace.name,
                }
            })
        except Exception:
            logger.exception('Не удалось создать рабочее пространство')
            return JsonResponse({'success': False, 'error': 'Не удалось создать рабочее пространство'}, status=500)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


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

def api_task_move(request, task_id):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Method not allowed"},
            status=405,
        )

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "Требуется авторизация"},
            status=401,
        )

    try:
        data = json.loads(request.body)
        column_id = data.get("column_id")
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Некорректный JSON"},
            status=400,
        )

    task = get_object_or_404(
        Task,
        Q(column__board__workspace__owner=request.user) |
        Q(column__board__members=request.user),
        id=task_id,
    )

    new_column = get_object_or_404(
        Column,
        Q(board__workspace__owner=request.user) | Q(board__members=request.user),
        id=column_id,
    )

    task.column = new_column
    task.order = Task.objects.filter(column=new_column).exclude(id=task.id).count()
    task.save()

    return JsonResponse({
        "success": True,
        "task": {
            "id": task.id,
            "column_id": new_column.id,
            "order": task.order,
        },
    })
