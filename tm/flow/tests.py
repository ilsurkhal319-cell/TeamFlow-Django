from django.test import TestCase
from users.models import CustomUser
from django.urls import reverse
import json
from flow.models import Workspace, Board, Column, Task, Notification
from flow.services import parse_mentions, create_mention_notifications
from rest_framework.test import APIClient

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

class TaskApiPermissionTests(TestCase):
    def test_anonymous_user_cannot_create_task(self):
        user = CustomUser.objects.create_user(
            username="owner_api",
            email="owner_api@example.com",
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

        response = self.client.post(
            reverse("flow:api_task_create"),
            data=json.dumps({
                "title": "Anonymous Task",
                "description": "Should not be created",
                "priority": "high",
                "column_id": column.id
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(Task.objects.filter(title="Anonymous Task").exists())

class TaskApiAccessTests(TestCase):
    def test_user_cannot_create_task_in_other_user_column(self):
        owner = CustomUser.objects.create_user(
            username="column_owner",
            email="column_owner@example.com",
            password="StrongPassword123"
        )

        other_user = CustomUser.objects.create_user(
            username="column_other",
            email="column_other@example.com",
            password="StrongPassword123"
        )

        workspace = Workspace.objects.create(
            name="Owner Workspace",
            owner=owner,
            is_personal=True
        )

        board = Board.objects.create(
            title="Owner Board",
            workspace=workspace,
            created_by=owner
        )

        column = Column.objects.create(
            board=board,
            title="To Do",
            order=0
        )

        self.client.login(username="column_other", password="StrongPassword123")

        response = self.client.post(
            reverse("flow:api_task_create"),
            data=json.dumps({
                "title": "Hacked Task",
                "description": "Should not be created",
                "priority": "high",
                "column_id": column.id
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Task.objects.filter(title="Hacked Task").exists())

class MentionServiceTests(TestCase):
    def test_parse_mentions_returns_usernames(self):
        mentions = parse_mentions("Hello @john and @kate")

        self.assertEqual(mentions, ["john", "kate"])

    def test_create_mention_notifications_creates_notification(self):
        author = CustomUser.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPassword123"
        )

        mentioned_user = CustomUser.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPassword123"
        )

        workspace = Workspace.objects.create(
            name="Mention Workspace",
            owner=author,
            is_personal=True
        )

        board = Board.objects.create(
            title="Mention Board",
            workspace=workspace,
            created_by=author
        )

        column = Column.objects.create(
            board=board,
            title="To Do",
            order=0
        )

        task = Task.objects.create(
            column=column,
            title="Mention Task",
            created_by=author
        )

        create_mention_notifications(
            task=task,
            text="Please check this @john",
            author=author
        )

        notification = Notification.objects.get(user=mentioned_user)

        self.assertEqual(notification.type, "mention")
        self.assertIn("Mention Task", notification.text)

    def test_author_does_not_receive_notification_about_self_mention(self):
        author = CustomUser.objects.create_user(
            username="author2",
            email="author2@example.com",
            password="StrongPassword123",
        )

        workspace = Workspace.objects.create(
            name="Self Mention Workspace",
            owner=author,
            is_personal=True,
        )
        board = Board.objects.create(
            title="Self Mention Board",
            workspace=workspace,
            created_by=author,
        )
        column = Column.objects.create(
            board=board,
            title="To Do",
            order=0,
        )
        task = Task.objects.create(
            column=column,
            title="Self Mention Task",
            created_by=author,
        )

        create_mention_notifications(
            task=task,
            text="Я сам себя упомянул: @author2",
            author=author,
        )

        self.assertFalse(Notification.objects.filter(user=author).exists())


class TaskMoveApiTests(TestCase):
    def test_user_can_move_own_task_to_another_column(self):
        user = CustomUser.objects.create_user(
            username="move_owner",
            email="move_owner@example.com",
            password="StrongPassword123",
        )
        workspace = Workspace.objects.create(
            name="Move Workspace",
            owner=user,
            is_personal=True,
        )
        board = Board.objects.create(
            title="Move Board",
            workspace=workspace,
            created_by=user,
        )
        source_column = Column.objects.create(board=board, title="To Do", order=0)
        target_column = Column.objects.create(board=board, title="Done", order=1)
        task = Task.objects.create(
            column=source_column,
            title="Move me",
            created_by=user,
        )

        self.client.login(username="move_owner", password="StrongPassword123")
        response = self.client.post(
            reverse("flow:api_task_move", args=[task.id]),
            data=json.dumps({"column_id": target_column.id}),
            content_type="application/json",
        )

        task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.column, target_column)


class DRFTaskApiTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="drf_user",
            email="drf_user@example.com",
            password="StrongPassword123",
        )
        workspace = Workspace.objects.create(
            name="DRF Workspace",
            owner=self.user,
            is_personal=True,
        )
        board = Board.objects.create(
            title="DRF Board",
            workspace=workspace,
            created_by=self.user,
        )
        self.column = Column.objects.create(
            board=board,
            title="To Do",
            order=0,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_can_create_task_through_drf_api(self):
        response = self.client.post(
            reverse("flow:drf_tasks"),
            {
                "title": "Task from DRF",
                "priority": "high",
                "column": self.column.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Task.objects.filter(title="Task from DRF").exists())

    def test_user_cannot_create_task_in_other_users_column(self):
        other_user = CustomUser.objects.create_user(
            username="other_drf_user",
            email="other_drf_user@example.com",
            password="StrongPassword123",
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            reverse("flow:drf_tasks"),
            {
                "title": "Task in чужой колонке",
                "priority": "high",
                "column": self.column.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Task.objects.filter(title="Task in чужой колонке").exists()
        )

    def test_user_can_update_own_task_through_drf_api(self):
        task = Task.objects.create(
            title="Old title",
            priority="low",
            column=self.column,
            created_by=self.user,
        )

        response = self.client.patch(
            reverse("flow:drf_task_detail", args=[task.id]),
            {
                "title": "New title",
                "priority": "high",
            },
            format="json",
        )

        task.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.title, "New title")
        self.assertEqual(task.priority, "high")

    def test_user_can_delete_own_task_through_drf_api(self):
        task = Task.objects.create(
            title="Task to delete",
            column=self.column,
            created_by=self.user,
        )

        response = self.client.delete(
            reverse("flow:drf_task_detail", args=[task.id])
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=task.id).exists())