# Generated by Django 5.0.7 on 2024-08-20 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_emailsubscription_alter_category_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ]
