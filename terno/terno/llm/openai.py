from .base import BaseLLM
from openai import OpenAI


class OpenAILLM(BaseLLM):
    o_series_models = ['o1', 'o1-2024-12-17',
                       'o1-preview', 'o1-preview-2024-09-12',
                       'o1-mini', 'o1-mini-2024-09-12',
                       'o3-mini', 'o3-mini-2025-01-31']
    """O series models configuration."""
    model_name: str = "gpt-3.5-turbo"
    """Model name to use.

    You can use the
    [List models](https://platform.openai.com/docs/api-reference/models/list) API to
    see all of your available models, or see OpenAI's
    [Model overview](https://platform.openai.com/docs/models/overview) for
    descriptions of them.
    """
    temperature: float = 0
    """What sampling temperature to use, between 0 and 2."""
    max_tokens: int = 1024
    """The maximum number of tokens to generate in the completion."""
    top_p: float = 1
    """Controls the cumulative probability threshold for next-word selection.
    The model considers the smallest set of words whose combined probability
    is at least top_p. A lower value reduces randomness, focusing on more
    probable words."""

    def __init__(self, api_key: str,
                 model_name: str = None,
                 temperature: float = None,
                 max_tokens: int = None,
                 top_p: float = None,
                 **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = model_name or self.model_name
        self.temperature = temperature if temperature is not None else self.temperature
        self.max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        self.top_p = top_p if top_p is not None else self.top_p

    def get_model_instance(self):
        client = OpenAI(
            api_key=self.api_key,
        )
        return client

    def create_message_for_llm(self, system_prompt, ai_prompt, human_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": ai_prompt},
            {"role": "user", "content": human_prompt},
        ]
        return messages

    def get_response(self, messages) -> dict:
        model = self.get_model_instance()
        model_name = self.model_name
        if model_name in self.o_series_models:
            messages[0]['role'] = 'developer'
            response = model.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **self.custom_parameters
            )
        else:
            response = model.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                **self.custom_parameters
            )

        return_dict = {}
        generated_sql = response.choices[0].message.content
        return_dict['generated_sql'] = generated_sql.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()

        try:
            return_dict['input_tokens'] = response.usage.prompt_tokens
            return_dict['input_tokens_cached'] = response.usage.prompt_tokens_details['cached_tokens']
            return_dict['output_tokens'] = response.usage.completion_tokens
            return_dict['model'] = response.model
            return_dict['llm_provider'] = 'openai'
        except Exception as e:
            pass
        return return_dict
