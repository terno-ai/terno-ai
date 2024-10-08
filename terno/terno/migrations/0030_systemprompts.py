# Generated by Django 5.0.4 on 2024-09-02 08:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terno', '0029_remove_datasource_db_info_datasource_dialect_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemPrompts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_prompt', models.TextField(blank=True, null=True)),
                ('data_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='terno.datasource')),
            ],
        ),
    ]
