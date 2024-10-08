# Generated by Django 5.0.4 on 2024-07-19 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terno', '0015_llmconfiguration_delete_llmapikey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='llmconfiguration',
            name='llm_type',
            field=models.CharField(choices=[('openai', 'OpenAI'), ('gemini', 'Gemini'), ('anthropic', 'Anthropic'), ('custom', 'CustomLLM')], help_text='Select the type of LLM (e.g., OpenAI, Gemini, etc.).', max_length=50),
        ),
    ]
