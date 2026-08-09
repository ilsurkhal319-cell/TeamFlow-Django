import re

from django.contrib.auth import get_user_model

from .models import Notification


User = get_user_model()


def parse_mentions(text):
    if not text:
        return []

    pattern = r"@(\w+)"
    return re.findall(pattern, text)


def create_mention_notifications(task, text, author, notification_type="mention"):
    mentioned_usernames = parse_mentions(text)

    for username in mentioned_usernames:
        try:
            user = User.objects.get(username=username)

            if user.id == author.id:
                continue

            link = f"/board/{task.column.board.id}/"

            Notification.objects.create(
                user=user,
                type=notification_type,
                text=f'{author.first_name or author.username} упомянул вас в задаче "{task.title}"',
                link=link,
            )
        except User.DoesNotExist:
            continue
