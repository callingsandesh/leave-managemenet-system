# Generated by Django 5.0.6 on 2024-07-10 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apidataupload', '0009_alter_leave_leave_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leave',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
