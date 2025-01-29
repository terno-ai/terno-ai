from .base import BaseLLM
import google.generativeai as genai


class GeminiLLM(BaseLLM):
    supported_system_instructions_model = ["gemini-1.5-flash-001",
                                           "gemini-1.5-pro-001"]
    """Models that support setting system instructions."""
    model_name: str = "gemini-1.5-pro-001"
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
                 top_p: float = None,
                 top_k: int = None,
                 **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = model_name or self.model_name
        self.temperature = temperature if temperature is not None else self.temperature
        self.max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        self.top_p = top_p if top_p is not None else self.top_p
        self.top_k = top_k if top_k is not None else self.top_k

    def get_model_instance(self, system_prompt):
        # models = genai.list_models()
        # supported_models_generativeModel = [m.name[7:] for m in models]
        if self.model_name in self.supported_system_instructions_model:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
            )
        # elif self.model_name in supported_models_generativeModel:
        #     model = genai.GenerativeModel(
        #         model_name = self.model_name,
        #     )
        else:
            raise ValueError(f"This model is not currently supported: {self.model_name}")

        return model

    def create_message_for_llm(self, system_prompt, ai_prompt, human_prompt):
        messages = [{'role': 'system', 'parts': [system_prompt]},
                    {'role': 'model', 'parts': [ai_prompt]},
                    {'role': 'user', 'parts': [human_prompt]}]
        return messages

    def get_response(self, messages) -> dict:
        system_prompt = messages[0]['parts'][0]
        messages = messages[1:]
        genai.configure(api_key=self.api_key)
        model = self.get_model_instance(system_prompt)
        response = model.generate_content(
            contents=messages,
            generation_config=dict(
                {
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "max_output_tokens": self.max_tokens,
                    "top_k": self.top_k,
                    **self.custom_parameters
                }
            ),
        )

        response = response.text.strip().removeprefix("```sql").removesuffix("```")

        return {'generated_sql': response}
