import secrets
import string

from django.db import migrations, models


def populate_join_codes(apps, schema_editor):
    Board = apps.get_model('flow', 'Board')
    alphabet = string.ascii_uppercase + string.digits
    used = set(Board.objects.exclude(join_code__isnull=True).values_list('join_code', flat=True))

    for board in Board.objects.filter(join_code__isnull=True):
        code = ''.join(secrets.choice(alphabet) for _ in range(8))
        while code in used:
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
        board.join_code = code
        board.save(update_fields=['join_code'])
        used.add(code)


class Migration(migrations.Migration):
    dependencies = [
        ('flow', '0004_remove_workspace_is_private_remove_workspace_members_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='join_code',
            field=models.CharField(blank=True, editable=False, max_length=8, null=True, unique=True),
        ),
        migrations.RunPython(populate_join_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='board',
            name='join_code',
            field=models.CharField(editable=False, max_length=8, unique=True),
        ),
    ]
