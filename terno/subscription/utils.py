import subscription.models as models
from django.utils import timezone


def calculate_price_from_tokens(data):
    llm_provider = data[0].get('llm_provider')
    if llm_provider == 'openai':
        return openai_price_calculate(data)
    else:
        raise Exception("Invalid LLM provider")


def openai_price_calculate(data):
    model_name = data[0].get('model')

    token_counts = {
        'input': 0,
        'cached_input': 0,
        'output': 0,
    }

    for record in data:
        uncached_input_tokens = record.get('input_tokens') - record.get('input_tokens_cached')
        token_counts['input'] += uncached_input_tokens
        token_counts['cached_input'] += record.get('input_tokens_cached')
        token_counts['output'] += record.get('output_tokens')

    pricing_objects = models.OpenAIPricing.objects.filter(
        token_type__in=token_counts.keys(),
        model_name=model_name
    ).values('token_type', 'price_per_1ktoken')

    # Map pricing to token types for quick access
    pricing = {item['token_type']: item['price_per_1ktoken'] for item in pricing_objects}

    # Calculate total usage cost
    usage = sum(
        (token_counts[token_type] * pricing[token_type] / 1000)
        for token_type in token_counts
    )

    return usage


def deduct_llm_credits(llm_credit, response):
    data = []
    for res in response:
        data.append(res[0])
    usage = calculate_price_from_tokens(data)
    # print(f"{usage}")
    llm_credit.credit -= usage
    llm_credit.updated_at = timezone.now()
    llm_credit.save()
