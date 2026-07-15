from django.urls import path
from flow.views import (
    board, dashboard, home, index, favorites, profile, archive,
    api_board_create, api_task_create, api_workspace_create, api_board_delete, api_board_favorite, api_board_archive,
    api_boards_list, api_user_search,
    api_notifications_list, api_notifications_read, api_notifications_read_all
)

app_name = 'flow'

urlpatterns = [
    path('', index, name='index'),
    path('board/<int:board_id>/', board, name='board_detail'),
    path('dashboard/', dashboard, name='dashboard'),
    path('home/', home, name='home'),
    path('favorites/', favorites, name='favorites'),
    path('profile/', profile, name='profile'),
    path('archive/', archive, name='archive'),

    # API endpoints
    path('api/boards/', api_boards_list, name='api_boards_list'),
    path('api/users/search/', api_user_search, name='api_user_search'),
    path('api/board/create/', api_board_create, name='api_board_create'),
    path('api/board/delete/<int:board_id>/', api_board_delete, name='api_board_delete'),
    path('api/board/favorite/<int:board_id>/', api_board_favorite, name='api_board_favorite'),
    path('api/board/archive/<int:board_id>/', api_board_archive, name='api_board_archive'),
    path('api/task/create/', api_task_create, name='api_task_create'),
    path('api/workspace/create/', api_workspace_create, name='api_workspace_create'),

    # Notifications API
    path('api/notifications/', api_notifications_list, name='api_notifications_list'),
    path('api/notifications/<int:notification_id>/read/', api_notifications_read, name='api_notifications_read'),
    path('api/notifications/read-all/', api_notifications_read_all, name='api_notifications_read_all'),
]