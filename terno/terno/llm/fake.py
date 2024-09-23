from .base import BaseLLM


class FakeLLM(BaseLLM):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_model_instance(self):
        pass

    def create_message_for_llm(self, system_prompt, ai_prompt, human_prompt):
        return []

    def get_response(self, messages) -> str:
        self.get_model_instance()
        return "SELECT 1"
