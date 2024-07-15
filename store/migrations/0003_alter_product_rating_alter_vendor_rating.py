# Generated by Django 5.0.7 on 2024-07-13 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.IntegerField(choices=[(0, '☆☆☆☆☆'), (1, '★☆☆☆☆'), (2, '★★☆☆☆'), (3, '★★★☆☆'), (4, '★★★★☆'), (5, '★★★★★')], default=3),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='rating',
            field=models.IntegerField(choices=[(0, '☆☆☆☆☆'), (1, '★☆☆☆☆'), (2, '★★☆☆☆'), (3, '★★★☆☆'), (4, '★★★★☆'), (5, '★★★★★')]),
        ),
    ]
