# Generated by Django 4.2.1 on 2023-05-21 11:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_first_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribtion',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ['-id'],
            },
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={
                'ordering': ['id'], 'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи'},
        ),
        migrations.DeleteModel(
            name='Follow',
        ),
        migrations.AddField(
            model_name='subscribtion',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='author', to=settings.AUTH_USER_MODEL,
                verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='subscribtion',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='subscriber', to=settings.AUTH_USER_MODEL,
                verbose_name='Подписчик'),
        ),
        migrations.AddConstraint(
            model_name='subscribtion',
            constraint=models.UniqueConstraint(fields=('user', 'author'),
                                               name='unique_subscribtion'),
        ),
    ]
