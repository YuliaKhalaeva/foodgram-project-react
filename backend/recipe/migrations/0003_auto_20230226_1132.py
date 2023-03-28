

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_auto_20230210_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, null=True, validators=[django.core.validators.RegexValidator('^#([a-fA-F0-9]{6})', message='Поле должно содержать HEX-код выбранного цвета.')], verbose_name='Цвет в HEX'),
        ),
    ]
