from abc import ABC, abstractmethod
from django.core.exceptions import ObjectDoesNotExist
from ..models import LLMConfiguration, OrganisationLLM, Organisation
from django.conf import settings
import terno.utils as utils


class NoSufficientCreditsException(Exception):
    def __init__(self, message="You have insufficient credits. Please set up your LLM."):
        super().__init__(message)


class NoDefaultLLMException(Exception):
    def __init__(self, message="No LLM Setup. Please set up your LLM."):
        super().__init__(message)


class BaseLLM(ABC):
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.custom_parameters = kwargs

    @abstractmethod
    def get_model_instance(self):
        pass

    @abstractmethod
    def get_role_specific_message(self, message, role):
        pass

    @abstractmethod
    def create_message_for_llm(self, system_prompt, ai_prompt, human_prompt):
        pass

    @abstractmethod
    def get_response(self, query) -> dict:
        pass

    @abstractmethod
    def csv_llm_response(self, messages):
        pass


class LLMFactory:
    @staticmethod
    def create_llm(organisation) -> BaseLLM:
        organisation_llm = OrganisationLLM.objects.filter(
            organisation=organisation,
            llm__enabled=True
        ).first()
        if organisation_llm:
            config = organisation_llm.llm
            is_default_llm = False
        else:
            default_org = Organisation.objects.filter(subdomain='terno-root').first()
            if default_org:
                # Get the default LLM (subdomain 'terno-root') if available
                organisation_llm = OrganisationLLM.objects.filter(
                    organisation=default_org,
                    llm__enabled=True
                ).first()

                if organisation_llm:
                    if organisation.llm_credit.credit > 0:
                        config = organisation_llm.llm
                        is_default_llm = True
                    else:
                        raise NoSufficientCreditsException()
                else:
                    raise NoDefaultLLMException()
            else:
                raise NoDefaultLLMException()

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
            return OpenAILLM(**common_params, **custom_params), is_default_llm
        elif config.llm_type == "gemini":
            from .gemini import GeminiLLM
            return GeminiLLM(**common_params, top_k=config.top_k, **custom_params), is_default_llm
        elif config.llm_type == "anthropic":
            from .anthropic import AnthropicLLM
            return AnthropicLLM(**common_params, top_k=config.top_k, **custom_params), is_default_llm
        elif config.llm_type == "ollama":
            from .ollama import OllamaLLM
            return OllamaLLM(**custom_params), is_default_llm
        elif config.llm_type == "custom":
            from .custom_llm import CustomLLM
            return CustomLLM(
                api_key=config.api_key,
                **custom_params,
                # Custom parameters to pass
                ), is_default_llm
        else:
            raise ValueError(f"Unknown LLM type: {config.llm_type}")
