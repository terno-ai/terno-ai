from terno.llm import BaseLLM
import ollama


class OllamaLLM(BaseLLM):
    host: str = "127.0.0.1:11434"
    model_name: str = "llama3.1"
    temperature: float = 0

    def __init__(self,
                 api_key: str = None,
                 host: str = None,
                 model_name: str = None,
                 temperature: float = None,
                 **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = model_name or self.model_name
        self.temperature = temperature if temperature is not None else self.temperature
        self.host = host if host is not None else self.host

    def get_model_instance(self):
        client = ollama.Client(host=self.host)
        return client

    def create_message_for_llm(self, system_prompt, ai_prompt, human_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": ai_prompt},
            {"role": "user", "content": human_prompt},
        ]
        return messages

    def get_response(self, messages) -> str:
        model = self.get_model_instance()
        response = model.chat(model=self.model_name, messages=messages)
        return response['message']['content']
