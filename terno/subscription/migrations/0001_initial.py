# Generated by Django 5.1.1 on 2025-01-29 01:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenAIPricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_type', models.CharField(choices=[('input', 'input'), ('cached_input', 'cached_input'), ('output', 'output')], help_text='Select the type of token (e.g., input, cached_input, output.)', max_length=64)),
                ('model_name', models.CharField(help_text='Specify the model name to use.', max_length=256)),
                ('price_per_1ktoken', models.DecimalField(decimal_places=16, help_text='Price per 1k tokens in USD', max_digits=24)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LLMCredit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit', models.DecimalField(decimal_places=16, default=0.0, max_digits=24)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='llm_credt', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
