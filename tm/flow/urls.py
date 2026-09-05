from django.urls import path
from flow.views import (
    board, dashboard, home, index, favorites, profile, archive,
    api_board_create, api_task_create, api_workspace_create, api_board_delete, api_board_favorite, api_board_archive,
    api_boards_list, api_user_search, api_board_member_add,
    api_notifications_list, api_notifications_read, api_notifications_read_all, api_task_move
)
from .api_views import RecentActivityAPIView, TaskDetailAPIView, TaskListCreateAPIView

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
    path('api/board/<int:board_id>/members/add/', api_board_member_add, name='api_board_member_add'),
    path('api/board/create/', api_board_create, name='api_board_create'),
    path('api/board/delete/<int:board_id>/', api_board_delete, name='api_board_delete'),
    path('api/board/favorite/<int:board_id>/', api_board_favorite, name='api_board_favorite'),
    path('api/board/archive/<int:board_id>/', api_board_archive, name='api_board_archive'),
    path('api/task/create/', api_task_create, name='api_task_create'),
    path('api/workspace/create/', api_workspace_create, name='api_workspace_create'),
    path("api/drf/tasks/", TaskListCreateAPIView.as_view(), name='drf_tasks'),
    path("api/drf/tasks/<int:pk>/",TaskDetailAPIView.as_view(),name="drf_task_detail",),
    path("api/drf/activity/", RecentActivityAPIView.as_view(), name="drf_recent_activity"),

    # Notifications API
    path('api/notifications/', api_notifications_list, name='api_notifications_list'),
    path('api/notifications/<int:notification_id>/read/', api_notifications_read, name='api_notifications_read'),
    path('api/notifications/read-all/', api_notifications_read_all, name='api_notifications_read_all'),
    path("api/task/<int:task_id>/move/",api_task_move,name="api_task_move",
         ),
]
