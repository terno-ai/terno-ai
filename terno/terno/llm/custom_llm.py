from .base import BaseLLM


class CustomLLM(BaseLLM):

    def __init__(self, api_key: str,
                 **kwargs):
        super().__init__(api_key, **kwargs)

    def get_model_instance(self):
        pass

    def get_role_specific_message(self, message, role):
        pass

    def create_message_for_llm(self, system_prompt, ai_prompt, human_prompt):
        pass

    def get_response(self, messages) -> dict:
        pass
