# Generated by Django 2.1.5 on 2019-03-22 00:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('myBlog', '0002_node'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='node',
            name='host',
            field=models.CharField(max_length=400),
        ),
    ]
