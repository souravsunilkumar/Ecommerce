# Generated by Django 5.0.6 on 2024-07-12 07:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.sub_category'),
        ),
    ]
