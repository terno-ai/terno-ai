from abc import ABC, abstractmethod
from django.core.exceptions import ObjectDoesNotExist
from ..models import LLMConfiguration


class BaseLLM(ABC):
    @abstractmethod
    def __init__(self, api_key: str, system_message: str = None, **kwargs):
        self.api_key = api_key
        self.system_message = system_message or self.get_system_prompt()

    def get_system_prompt(self) -> str:
        return "You are an SQL Analyst. Generate the SQL given a question. Only generate SQL without markdown or any formatting and nothing else. The output you give will be directly executed on the database. So return the response accordingly."

    def get_chat_history(self) -> str:
        pass

    @abstractmethod
    def get_model_instance(self):
        pass

    @abstractmethod
    def get_response(self, query: str, db_schema) -> str:
        pass


class LLMFactory:
    @staticmethod
    def create_llm() -> BaseLLM:
        try:
            config = LLMConfiguration.objects.get(enabled=True)
        except ObjectDoesNotExist:
            raise ValueError("No enabled LLM configuration found.")

        if config.llm_type == "openai":
            from .openai import OpenAILLM
            return OpenAILLM(
                api_key=config.api_key,
                model_name=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                system_message=config.custom_system_message,
                top_p=config.top_p,
                top_k=config.top_k,
            )
        elif config.llm_type == "gemini":
            from .gemini import GeminiLLM
            return GeminiLLM(
                api_key=config.api_key,
                model_name=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                system_message=config.custom_system_message,
                top_p=config.top_p,
                top_k=config.top_k,
            )
        elif config.llm_type == "anthropic":
            from .anthropic import AnthropicLLM
            return AnthropicLLM(
                api_key=config.api_key,
                model_name=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                system_message=config.custom_system_message,
                top_p=config.top_p,
                top_k=config.top_k,
            )
        elif config.llm_type == "custom":
            pass
        else:
            raise ValueError(f"Unknown LLM type: {config.llm_type}")
