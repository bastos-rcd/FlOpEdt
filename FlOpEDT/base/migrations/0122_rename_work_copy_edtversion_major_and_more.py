# Generated by Django 4.2 on 2024-03-15 07:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0121_alter_edtversion_unique_together_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="edtversion",
            old_name="work_copy",
            new_name="major",
        ),
        migrations.RenameField(
            model_name="edtversion",
            old_name="version",
            new_name="minor",
        ),
        migrations.AlterUniqueTogether(
            name="edtversion",
            unique_together={("department", "period", "major")},
        ),
    ]
