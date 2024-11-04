# Generated by Django 5.0.6 on 2024-07-26 07:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_alter_product_description_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon_code',
            name='expiry_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='coupon_code',
            name='used',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coupon_code',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='coupon_code',
            name='code',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
