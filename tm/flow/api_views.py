from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer


class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Task.objects
            .filter(column__board__workspace__owner=self.request.user)
            .select_related("column__board")
            .order_by("order")
        )

    def perform_create(self, serializer):
        column = serializer.validated_data["column"]

        if column.board.workspace.owner_id != self.request.user.id:
            raise PermissionDenied(
                "Нельзя создавать задачи в чужой колонке."
            )

        serializer.save(created_by=self.request.user)

class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            column__board__workspace__owner=self.request.user
        )

    def perform_update(self, serializer):
        column = serializer.validated_data.get(
            "column",
            serializer.instance.column,
        )

        if column.board.workspace.owner_id != self.request.user.id:
            raise PermissionDenied(
                "Нельзя перемещать задачу в чужую колонку."
            )

        serializer.save()