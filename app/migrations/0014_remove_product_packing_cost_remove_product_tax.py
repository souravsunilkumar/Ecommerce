# Generated by Django 5.0.6 on 2024-07-06 15:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_product_packing_cost_product_tax'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='packing_cost',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tax',
        ),
    ]
