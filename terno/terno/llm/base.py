from abc import ABC, abstractmethod
from django.core.exceptions import ObjectDoesNotExist
from ..models import LLMConfiguration, OrganisationLLM


class BaseLLM(ABC):
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.custom_parameters = kwargs

    @abstractmethod
    def get_model_instance(self):
        pass

    @abstractmethod
    def create_message_for_llm(self, system_prompt, ai_prompt, human_prompt):
        pass

    @abstractmethod
    def get_response(self, query: str) -> dict:
        pass


class LLMFactory:
    @staticmethod
    def create_llm(organisation) -> BaseLLM:
        try:
            organisation_llm = OrganisationLLM.objects.get(
                organisation=organisation,
                llm__enabled=True
            )
            config = organisation_llm.llm
        except ObjectDoesNotExist:
            raise ValueError("No enabled LLM configuration found.")
        common_params = {
                'api_key': config.api_key,
                'model_name': config.model_name,
                'temperature': config.temperature,
                'max_tokens': config.max_tokens,
                'top_p': config.top_p,
            }

        custom_params = config.custom_parameters or {}

        if config.llm_type == "openai":
            from .openai import OpenAILLM
            return OpenAILLM(**common_params, **custom_params)
        elif config.llm_type == "gemini":
            from .gemini import GeminiLLM
            return GeminiLLM(**common_params, top_k=config.top_k, **custom_params)
        elif config.llm_type == "anthropic":
            from .anthropic import AnthropicLLM
            return AnthropicLLM(**common_params, top_k=config.top_k, **custom_params)
        elif config.llm_type == "ollama":
            from .ollama import OllamaLLM
            return OllamaLLM(**custom_params)
        elif config.llm_type == "custom":
            from .custom_llm import CustomLLM
            return CustomLLM(
                api_key=config.api_key,
                **custom_params,
                # Custom parameters to pass
                )
        else:
            raise ValueError(f"Unknown LLM type: {config.llm_type}")
