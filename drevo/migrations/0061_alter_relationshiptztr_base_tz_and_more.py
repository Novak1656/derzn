# Generated by Django 4.1.1 on 2023-03-23 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0060_relationshiptztr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationshiptztr',
            name='base_tz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base_relationship', to='drevo.tz', verbose_name='Вид базового знания'),
        ),
        migrations.AlterField(
            model_name='relationshiptztr',
            name='rel_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relationship', to='drevo.tr', verbose_name='Вид связи'),
        ),
        migrations.AlterField(
            model_name='relationshiptztr',
            name='rel_tz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_relationship', to='drevo.tz', verbose_name='Вид связанного знания'),
        ),
    ]
