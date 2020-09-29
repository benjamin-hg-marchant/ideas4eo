# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-11-05 19:04
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import notebooks.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=1000, unique=True)),
                ('title', models.CharField(max_length=1000)),
                ('content', models.TextField()),
                ('content_formatted', models.TextField()),
                ('article_url_link_list', models.TextField()),
                ('image_url_link_list', models.TextField()),
                ('file_url_link_list', models.TextField()),
                ('video_url_link_list', models.TextField()),
                ('nb_public_photos', models.IntegerField(default=0)),
                ('removed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docfile', models.FileField(upload_to=notebooks.models.uploaded_file_path)),
                ('url', models.CharField(max_length=1000, unique=True)),
                ('name', models.CharField(max_length=500)),
                ('format', models.CharField(max_length=500)),
                ('size', models.IntegerField(null=True)),
                ('width', models.IntegerField(null=True)),
                ('height', models.IntegerField(null=True)),
                ('timestamp', models.CharField(default='', max_length=1000)),
                ('removed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_type', models.CharField(max_length=500)),
                ('title', models.CharField(max_length=1000)),
                ('note_full_path', models.TextField()),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
                ('date_modified', models.DateTimeField(default=datetime.datetime.now)),
                ('public', models.BooleanField(default=True)),
                ('language', models.CharField(max_length=4)),
                ('abstract', models.TextField(default='')),
                ('abstract_formatted', models.TextField(default='')),
                ('comments_counts', models.IntegerField(null=True)),
                ('comments', models.BooleanField(default=True)),
                ('comments_blocked', models.BooleanField(default=False)),
                ('nb_views', models.IntegerField(default=0, null=True)),
                ('keywords', models.TextField()),
                ('keywords_machine', models.TextField()),
                ('removed', models.BooleanField(default=False)),
                ('article', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Article')),
                ('image', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Image')),
            ],
        ),
        migrations.CreateModel(
            name='Note_Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('removed', models.BooleanField(default=False)),
                ('note_01', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='note_01', to='notebooks.Note')),
                ('note_02', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='note_02', to='notebooks.Note')),
            ],
        ),
        migrations.CreateModel(
            name='Notebook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField(unique=True)),
                ('notebook_type', models.IntegerField(null=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
                ('account_active', models.BooleanField(default=True)),
                ('account_blocked', models.BooleanField(default=False)),
                ('last_activity_date', models.DateTimeField(default=datetime.datetime.now)),
                ('docfile', models.FileField(blank=True, upload_to=notebooks.models.notebook_uploaded_file_path)),
                ('profile_picture', models.BooleanField(default=False)),
                ('header_img_file', models.FileField(blank=True, upload_to=notebooks.models.notebook_uploaded_file_path)),
                ('header_img', models.BooleanField(default=False)),
                ('display_full_name', models.BooleanField(default=False)),
                ('display_about_button', models.BooleanField(default=False)),
                ('full_name', models.CharField(default='', max_length=200)),
                ('middle_name', models.CharField(default='', max_length=100)),
                ('pseudo_changed', models.DateTimeField(default=datetime.datetime.now)),
                ('country', models.IntegerField(null=True)),
                ('sex', models.IntegerField(null=True)),
                ('date_of_birth', models.DateTimeField(default=datetime.datetime.now)),
                ('language', models.CharField(max_length=4)),
                ('phone', models.IntegerField(null=True)),
                ('isced_level', models.IntegerField(null=True)),
                ('content', models.TextField()),
                ('content_formatted', models.TextField()),
                ('abstract', models.TextField()),
                ('abstract_formatted', models.TextField()),
                ('content_fr', models.TextField()),
                ('content_fr_formatted', models.TextField()),
                ('abstract_fr', models.TextField()),
                ('abstract_fr_formatted', models.TextField()),
                ('security_questions', models.BooleanField(default=False)),
                ('security_question_1_idx', models.IntegerField(null=True)),
                ('security_question_1', models.TextField()),
                ('security_question_2_idx', models.IntegerField(null=True)),
                ('security_question_2', models.TextField()),
                ('security_question_3_idx', models.IntegerField(null=True)),
                ('security_question_3', models.TextField()),
                ('nb_public_photos', models.IntegerField(default=0)),
                ('key_words', models.TextField()),
                ('key_words_machine', models.TextField()),
                ('removed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notebook_Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_admin', models.BooleanField(default=False)),
                ('can_see', models.BooleanField(default=True)),
                ('can_edit', models.BooleanField(default=True)),
                ('is_author', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
                ('removed', models.BooleanField(default=False)),
                ('note', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Note')),
                ('notebook', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Notebook')),
            ],
        ),
        migrations.CreateModel(
            name='Notebook_Stats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes_count', models.IntegerField(null=True)),
                ('article_count', models.IntegerField(null=True)),
                ('image_count', models.IntegerField(null=True)),
                ('file_count', models.IntegerField(null=True)),
                ('code_count', models.IntegerField(null=True)),
                ('visitor_weekly_count', models.IntegerField(null=True)),
                ('removed', models.BooleanField(default=False)),
                ('notebook', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Notebook')),
            ],
        ),
        migrations.AddField(
            model_name='note_link',
            name='notebook',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Notebook'),
        ),
        migrations.AddField(
            model_name='note',
            name='notebook',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Notebook'),
        ),
        migrations.AddField(
            model_name='image',
            name='notebook',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Notebook'),
        ),
        migrations.AddField(
            model_name='article',
            name='notebook',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='notebooks.Notebook'),
        ),
    ]
