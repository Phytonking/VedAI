# Generated by Django 5.0.2 on 2024-02-25 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_solution_sol_id_alter_solution_solution_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientsordered',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
