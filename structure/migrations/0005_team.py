# Generated by Django 3.2.4 on 2021-06-18 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0004_alter_person_transition_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='Название команды')),
                ('team_priority', models.IntegerField(blank=True, default=1, verbose_name='Индекс в графике')),
                ('persons', models.ManyToManyField(blank=True, to='structure.Person', verbose_name='Название команды')),
                ('timezone', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='structure.timezone')),
            ],
            options={
                'verbose_name': 'Команда',
                'verbose_name_plural': 'Команды',
            },
        ),
    ]
