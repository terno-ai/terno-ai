# Generated by Django 5.0.4 on 2024-07-19 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terno', '0017_alter_llmconfiguration_api_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='llmconfiguration',
            name='top_k',
            field=models.FloatField(blank=True, help_text='Set the top-k parameter value (Limits the model to consider only the top k most probable next words). Leave blank for default.', null=True),
        ),
    ]