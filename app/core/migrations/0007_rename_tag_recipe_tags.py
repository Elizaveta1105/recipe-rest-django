# Generated by Django 3.2.25 on 2025-06-14 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_recipe_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
    ]
