# Generated by Django 2.1.5 on 2019-03-22 01:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myBlog', '0005_auto_20190321_1845'),
    ]

    operations = [
        migrations.RenameField(
            model_name='node',
            old_name='password',
            new_name='remotePassword',
        ),
        migrations.RenameField(
            model_name='node',
            old_name='username',
            new_name='remoteUsername',
        ),
    ]
