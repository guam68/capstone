# Generated by Django 2.2b1 on 2019-02-28 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kf_main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distribution',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
