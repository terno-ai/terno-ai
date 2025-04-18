# Generated by Django 5.1.1 on 2025-04-07 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terno', '0041_organisation_assign_llm_credit'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='is_erp',
            field=models.BooleanField(default=False, help_text='Flag to indicate if the datasource is an ERP system.'),
        ),
    ]
