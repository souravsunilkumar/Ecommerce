# Generated by Django 5.0.6 on 2024-07-11 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='shipping_cost',
        ),
        migrations.RemoveField(
            model_name='order',
            name='tax',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_amount',
        ),
    ]
