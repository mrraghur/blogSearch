# Generated by Django 3.1.6 on 2021-05-08 03:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='newsletterscrapestatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('downloadedsitemap', models.BooleanField(verbose_name=False)),
                ('generatedAllPostUrls', models.BooleanField(verbose_name=False)),
            ],
        ),
        migrations.CreateModel(
            name='substacknewsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='newsletterPostUrls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField()),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='scraperpipeline.substacknewsletter')),
            ],
        ),
    ]
