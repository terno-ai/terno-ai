# Generated by Django 5.0.4 on 2024-06-27 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terno', '0009_tablerowfilterselector'),
    ]

    operations = [
        migrations.CreateModel(
            name='LLMApiKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('openai', 'OpenAI'), ('gemini', 'Gemini'), ('anthropic', 'Anthropic')], max_length=20)),
                ('key', models.CharField(max_length=150)),
            ],
        ),
    ]
