from django.db import migrations, models


def create_main_workspaces(apps, schema_editor):
    User = apps.get_model('users', 'CustomUser')
    Workspace = apps.get_model('flow', 'Workspace')
    for user in User.objects.all().iterator():
        Workspace.objects.get_or_create(
            owner_id=user.id,
            name='Main',
            defaults={'is_private': True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('flow', '0002_notification'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workspace',
            old_name='is_personal',
            new_name='is_private',
        ),
        migrations.AlterField(
            model_name='workspace',
            name='is_private',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(create_main_workspaces, migrations.RunPython.noop),
    ]
