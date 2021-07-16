# Generated by Django 3.2.4 on 2021-06-29 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0005_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='link_channels',
            field=models.ManyToManyField(blank=True, to='structure.Link', verbose_name='Каналы связи'),
        ),
        migrations.AlterField(
            model_name='team',
            name='persons',
            field=models.ManyToManyField(blank=True, to='structure.Person', verbose_name='Специалисты'),
        ),
    ]