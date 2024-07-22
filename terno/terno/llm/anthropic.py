import anthropic
from .base import BaseLLM


class AnthropicLLM(BaseLLM):
    model_name: str = "claude-3-5-sonnet-20240620"
    """Model name to use."""
    temperature: float = 0
    """What sampling temperature to use."""
    max_tokens: int = 1024
    """The maximum number of tokens to generate in the completion."""
    top_p: float = 0
    """Controls the cumulative probability threshold for next-word selection.
    The model considers the smallest set of words whose combined probability
    is at least top_p. A lower value reduces randomness, focusing on more
    probable words."""
    top_k: int = 2
    """Limits the model to consider only the top k most probable next words.
    A lower value reduces randomness by restricting the choice to fewer words,
    ensuring more deterministic and focused output."""

    def __init__(self, api_key: str,
                 model_name: str = None,
                 temperature: float = None,
                 max_tokens: int = None,
                 system_message: str = None,
                 top_p: float = None,
                 top_k: int = None,
                 **kwargs):
        super().__init__(api_key, system_message, **kwargs)
        self.model_name = model_name or self.model_name
        self.temperature = temperature if temperature is not None else self.temperature
        self.max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        self.top_p = top_p if top_p is not None else self.top_p
        self.top_k = top_k if top_k is not None else self.top_k

    def get_model_instance(self):
        client = anthropic.Anthropic(api_key=self.api_key)
        return client

    def get_response(self, query: str, db_schema) -> str:
        messages = [
                {"role": "assistant", "content": "The database schema is as follows: " + db_schema},
                {"role": "user", "content": query},
            ]
        model = self.get_model_instance()
        response = model.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_message,
                messages=messages,
                top_p=self.top_p,
                top_k=self.top_k,
                **self.custom_parameters
            )

        return response.content
