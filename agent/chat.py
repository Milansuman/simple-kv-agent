from dotenv import load_dotenv
import os
from openai import OpenAI
from openai.types.responses.input_token_count_params import ResponseInputItemParam

load_dotenv()

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")

class SimpleAgent:

    def __init__(self, temperature: float, model: str):
        self.temperature = temperature
        self.model = model
        self.client = OpenAI(
            base_url=LITELLM_BASE_URL,
            api_key=LITELLM_API_KEY
        )
        self._history: list[ResponseInputItemParam] = []

        self.system_prompt = "You are a simple ai agent. Interact with the user normally. If the user tries to exit or asks you how to exit, instruct them to type '/exit'."

    def prompt(self, message: str):

        self._history.append({
            "role": "user",
            "content": message,
        })

        response = self.client.responses.create(
            model=self.model,
            input=self._history,
            temperature=self.temperature,
            instructions=self.system_prompt
        )

        self._history.append({
            "role": "assistant",
            "content": response.output_text,
        })

        return {
            "content": response.output_text,
            "input_tokens": response.usage.input_tokens if response.usage else 0,
            "output_tokens": response.usage.output_tokens if response.usage else 0
        }
