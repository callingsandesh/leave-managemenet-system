# Generated by Django 5.0.6 on 2024-07-10 05:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apidataupload', '0006_leave_issuer_first_name_leave_issuer_last_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('leave_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='leave',
            name='leave_type_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='apidataupload.leavetype'),
            preserve_default=False,
        ),
    ]
