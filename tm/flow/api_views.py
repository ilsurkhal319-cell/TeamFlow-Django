from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q

from .models import Board, Task
from .serializers import TaskSerializer


class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Task.objects
            .filter(
                Q(column__board__workspace__owner=self.request.user)
                | Q(column__board__members=self.request.user)
            )
            .distinct()
            .select_related("column__board")
            .order_by("order")
        )

    def perform_create(self, serializer):
        column = serializer.validated_data["column"]

        if (
            column.board.workspace.owner_id != self.request.user.id
            and not column.board.members.filter(id=self.request.user.id).exists()
        ):
            raise PermissionDenied(
                "Нельзя создавать задачи в чужой колонке."
            )

        serializer.save(created_by=self.request.user)

class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            Q(column__board__workspace__owner=self.request.user)
            | Q(column__board__members=self.request.user)
        ).distinct()

    def perform_update(self, serializer):
        column = serializer.validated_data.get(
            "column",
            serializer.instance.column,
        )

        if (
            column.board.workspace.owner_id != self.request.user.id
            and not column.board.members.filter(id=self.request.user.id).exists()
        ):
            raise PermissionDenied(
                "Нельзя перемещать задачу в чужую колонку."
            )

        serializer.save()


class RecentActivityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent_tasks = (
            Task.objects
            .filter(
                Q(column__board__workspace__owner=request.user)
                | Q(column__board__members=request.user)
            )
            .distinct()
            .select_related("column__board")
            .order_by("-updated_at")[:10]
        )
        recent_boards = (
            Board.objects
            .filter(
                Q(workspace__owner=request.user) | Q(members=request.user)
            )
            .distinct()
            .order_by("-updated_at")[:10]
        )

        activity = [
            {
                "type": "task",
                "title": task.title,
                "detail": f"Доска: {task.column.board.title}",
                "updated_at": task.updated_at.isoformat(),
                "link": f"/board/{task.column.board_id}/",
            }
            for task in recent_tasks
        ]
        activity.extend(
            {
                "type": "board",
                "title": board.title,
                "detail": "Доска обновлена",
                "updated_at": board.updated_at.isoformat(),
                "link": f"/board/{board.id}/",
            }
            for board in recent_boards
        )
        activity.sort(key=lambda item: item["updated_at"], reverse=True)

        return Response({"results": activity[:10]})
