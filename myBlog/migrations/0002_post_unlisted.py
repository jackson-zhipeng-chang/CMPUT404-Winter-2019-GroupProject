# Generated by Django 2.1.5 on 2019-02-20 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myBlog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='unlisted',
            field=models.BooleanField(default=False),
        ),
    ]
