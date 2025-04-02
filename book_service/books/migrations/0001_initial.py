# Generated by Django 5.1.7 on 2025-04-01 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('ISBN', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('Author', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('genre', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
            ],
            options={
                'ordering': ['ISBN'],
            },
        ),
    ]
