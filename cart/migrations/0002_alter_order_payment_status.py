# Generated by Django 5.2 on 2025-05-16 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(default='PENDING', max_length=20),
        ),
    ]
