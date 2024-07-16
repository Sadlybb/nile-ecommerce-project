# Generated by Django 5.0.7 on 2024-07-16 06:54

import ckeditor_uploader.fields
import django.db.models.deletion
import store.models
import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='user_name',
        ),
        migrations.AddField(
            model_name='review',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='customer',
            name='image',
            field=models.ImageField(blank=True, default='person.png', null=True, upload_to=store.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='product',
            name='full_description',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='-'),
        ),
        migrations.AlterField(
            model_name='product',
            name='specifications',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='-'),
        ),
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(default='product.png', upload_to='store/images/product'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='full_description',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='-'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='image',
            field=models.ImageField(blank=True, default='person.png', null=True, upload_to=store.models.user_directory_path),
        ),
    ]
