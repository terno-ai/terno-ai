from .base import BaseLLM


class FakeLLM(BaseLLM):

    def __init__(self, system_message: str = None, **kwargs):
        super().__init__(system_message, **kwargs)

    def get_model_instance(self):
        pass

    def get_response(self, messages) -> str:
        self.get_model_instance()
        return "SELECT 1"
