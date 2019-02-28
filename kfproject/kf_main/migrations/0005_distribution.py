# Generated by Django 2.2b1 on 2019-02-28 21:51

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kf_main', '0004_delete_distribution'),
    ]

    operations = [
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('action', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('artifact', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('creature', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('upgrade', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('amber', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'distribution',
                'managed': True,
            },
        ),
    ]
