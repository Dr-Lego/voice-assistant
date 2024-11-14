import ollama
from typing import Iterator, Union


class LLM:
    def __init__(self, model_name: str, system_prompt: str = None, host: str = None):
        self.client = ollama.Client(host=host)
        self.model_name = model_name
        self.system_prompt = system_prompt

        if system_prompt:
            self.create_model()

    def create_model(self):
        modelfile = f"""
        FROM {self.model_name}
        SYSTEM {self.system_prompt}
        """
        self.client.create(model=f"custom_{self.model_name}", modelfile=modelfile)
        self.model_name = f"custom_{self.model_name}"

    def chat(
        self, prompt: str = None, stream: bool = False, messages: list = None
    ) -> Union[str, Iterator[str]]:
        if prompt:
            messages = [{"role": "user", "content": prompt}]
        elif not messages:
            raise ValueError("Either prompt or messages must be provided")

        return (
            self._stream_response(messages) if stream else self._get_response(messages)
        )

    def _stream_response(self, messages: list) -> Iterator[str]:
        for chunk in self.client.chat(
            model=self.model_name, messages=messages, stream=True
        ):
            yield chunk["message"]["content"]

    def _get_response(self, messages: list) -> str:
        response = self.client.chat(model=self.model_name, messages=messages)
        return response["message"]["content"]
