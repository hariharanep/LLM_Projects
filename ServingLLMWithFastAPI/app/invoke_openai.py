from openai import OpenAI
import os
import sys

class OpenAIAgent:
    def __init__(self):
        # Initialize openai client and chat conversation history
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OpenAI API Key must be provided as an environment variable.")
            sys.exit(1)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-turbo-preview"


    def translate_text(self, input_str: str):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert translator who translates text from english to french and only returns the translated text",
                },
                {"role": "user", "content": input_str},
            ],
        )
        return completion.choices[0].message.content