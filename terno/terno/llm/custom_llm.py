from .base import BaseLLM


class CustomLLM(BaseLLM):

    def __init__(self, api_key: str,
                 system_message: str = None):
        super().__init__(api_key, system_message)

    def get_model_instance(self):
        pass

    def get_response(self, query: str, db_schema) -> str:
        pass
