from django.test import TestCase
from users.models import CustomUser
from flow.models import Workspace, Board, Column, Task
from django.urls import reverse
import json

class WorkspaceModelTests(TestCase):
    def test_workspace_can_be_created(self):
        user = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPassword123"
        )

        workspace = Workspace.objects.create(
            name="Test Workspace",
            description="Test description",
            owner=user,
            is_personal=True
        )

        self.assertEqual(workspace.name, "Test Workspace")
        self.assertEqual(workspace.owner, user)
        self.assertTrue(workspace.is_personal)

class BoardModelTests(TestCase):
    def test_board_can_be_created(self):
        user = CustomUser.objects.create_user(
            username="owner2",
            email="owner2@example.com",
            password="StrongPassword123"
        )

        workspace = Workspace.objects.create(
            name="Test Workspace",
            owner=user,
            is_personal=True
        )

        board = Board.objects.create(
            title="Test Board",
            description="Test board description",
            workspace=workspace,
            created_by=user
        )

        self.assertEqual(board.title, "Test Board")
        self.assertEqual(board.workspace, workspace)
        self.assertEqual(board.created_by, user)
        self.assertFalse(board.is_archived)

class TaskModelTests(TestCase):
    def test_task_can_be_created(self):
        user = CustomUser.objects.create_user(
            username="owner3",
            email="owner3@example.com",
            password="StrongPassword123"
        )

        workspace = Workspace.objects.create(
            name="Test Workspace",
            owner=user,
            is_personal=True
        )

        board = Board.objects.create(
            title="Test Board",
            workspace=workspace,
            created_by=user
        )

        column = Column.objects.create(
            board=board,
            title="To Do",
            order=0
        )

        task = Task.objects.create(
            column=column,
            title="Test Task",
            description="Test task description",
            priority="medium",
            created_by=user
        )

        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.column, column)
        self.assertEqual(task.created_by, user)
        self.assertEqual(task.priority, "medium")

class BoardAccessTests(TestCase):
    def test_user_cannot_access_other_user_board(self):
        owner = CustomUser.objects.create_user(
            username="owner4",
            email="owner4@example.com",
            password="StrongPassword123"
        )

        other_user = CustomUser.objects.create_user(
            username="other4",
            email="other4@example.com",
            password="StrongPassword123"
        )

        workspace = Workspace.objects.create(
            name="Owner Workspace",
            owner=owner,
            is_personal=True
        )

        board = Board.objects.create(
            title="Private Board",
            workspace=workspace,
            created_by=owner
        )

        self.client.login(username="other4", password="StrongPassword123")

        response = self.client.get(reverse("flow:board_detail", args=[board.id]))

        self.assertNotEqual(response.context["board"], board)

class TaskApiTests(TestCase):
    def test_authenticated_user_can_create_task(self):
        user = CustomUser.objects.create_user(
            username="apiuser",
            email="apiuser@example.com",
            password="StrongPassword123"
        )

        workspace = Workspace.objects.create(
            name="API Workspace",
            owner=user,
            is_personal=True
        )

        board = Board.objects.create(
            title="API Board",
            workspace=workspace,
            created_by=user
        )

        column = Column.objects.create(
            board=board,
            title="To Do",
            order=0
        )

        self.client.login(username="apiuser", password="StrongPassword123")

        response = self.client.post(
            reverse("flow:api_task_create"),
            data=json.dumps({
                "title": "Task from API",
                "description": "Created in test",
                "priority": "high",
                "column_id": column.id
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(title="Task from API").exists())