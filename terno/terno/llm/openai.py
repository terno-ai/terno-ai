from .base import BaseLLM
from openai import OpenAI


class OpenAILLM(BaseLLM):
    o1_beta_models = ['o1-preview', 'o1-mini']
    """O1 beta models which do not support system prompt and some parameters."""
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

    def get_response(self, messages) -> str:
        model = self.get_model_instance()
        model_name = self.model_name
        if model_name in self.o1_beta_models:
            messages[0]['role'] = 'assistant'
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
        response = response.choices[0].message.content
        response = response.strip().removeprefix("```sql").removesuffix("```")
        return response
