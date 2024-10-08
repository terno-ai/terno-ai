# Generated by Django 5.0.4 on 2024-09-11 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terno', '0030_systemprompts'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='connection_json',
            field=models.JSONField(blank=True, help_text='JSON key file contents for authentication', null=True),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='type',
            field=models.CharField(choices=[('generic', 'Generic'), ('oracle', 'Oracle'), ('mysql', 'MySQL'), ('postgres', 'Postgres'), ('bigquery', 'BigQuery')], default='generic', max_length=20),
        ),
    ]
