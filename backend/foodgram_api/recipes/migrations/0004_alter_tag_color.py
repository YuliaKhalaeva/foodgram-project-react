# Generated by Django 3.2.18 on 2023-03-16 18:58

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230315_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#ffffff', image_field=None, max_length=15, samples=None, verbose_name='tag color'),
        ),
    ]