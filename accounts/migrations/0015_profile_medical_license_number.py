# Generated by Django 4.2.13 on 2024-08-31 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_province_slug_province_tel_prefix_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='medical_license_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
