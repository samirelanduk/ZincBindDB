# Generated by Django 2.0.2 on 2018-06-09 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zinc', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chain',
            name='cluster',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
