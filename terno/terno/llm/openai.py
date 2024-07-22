from .base import BaseLLM
from openai import OpenAI


class OpenAILLM(BaseLLM):

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
                 top_k: int = None):
        super().__init__(api_key, system_message)
        self.model_name = model_name or self.model_name
        self.temperature = temperature if temperature is not None else self.temperature
        self.max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        self.top_p = top_p if top_p is not None else self.top_p
        self.top_k = top_k if top_k is not None else self.top_k

    def get_model_instance(self):
        client = OpenAI(
            api_key=self.api_key,
        )
        return client

    def get_response(self, query: str, db_schema) -> str:
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "assistant", "content": "The database schema is as follows: " + db_schema},
            {"role": "user", "content": query},
        ]
        model = self.get_model_instance()
        response = model.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            top_k=self.top_k
        )
        return response.choices[0].message.content
