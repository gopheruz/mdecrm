# Generated by Django 5.2 on 2025-05-13 18:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('med_app', '0009_call_ip_operator'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='call',
            options={'ordering': ['-created_at'], 'verbose_name': 'Звонок', 'verbose_name_plural': 'Звонки'},
        ),
        migrations.AlterField(
            model_name='call',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='call',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='call',
            name='med_card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='med_app.medcard', verbose_name='Медкарта'),
        ),
        migrations.AlterField(
            model_name='call',
            name='operator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Оператор (Система)'),
        ),
        migrations.AlterField(
            model_name='call',
            name='phone_number',
            field=models.CharField(max_length=20, verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='call',
            name='recording_path',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Путь к записи (шаблон)'),
        ),
    ]
