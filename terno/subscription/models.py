from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LLMCredit(models.Model):
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='llm_credt')
    credit = models.DecimalField(default=0.0, max_digits=24, decimal_places=16)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class OpenAIPricing(models.Model):

    TOKEN_TYPES = [
        ('input', 'input'),
        ('cached_input', 'cached_input'),
        ('output', 'output')
    ]

    token_type = models.CharField(
        max_length=64, choices=TOKEN_TYPES,
        help_text="Select the type of token (e.g., input, cached_input, output.)")
    model_name = models.CharField(
        max_length=256,
        help_text="Specify the model name to use.")
    price_per_1ktoken = models.DecimalField(max_digits=24, decimal_places=16, help_text="Price per 1k tokens in USD")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        existing_pricing = OpenAIPricing.objects.filter(model_name=self.model_name, token_type=self.token_type).first()

        if existing_pricing:
            existing_pricing.price_per_1ktoken = self.price_per_1ktoken
            existing_pricing.updated_at = timezone.now()
            super(OpenAIPricing, existing_pricing).save(update_fields=["price_per_1ktoken", "updated_at"])
        else:
            super().save(*args, **kwargs)
