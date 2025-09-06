import os
from dotenv import load_dotenv

from autogen_ext.models.openai import OpenAIChatCompletionClient
from src.config.constants import MODEL

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_model_client():
    model_client=OpenAIChatCompletionClient(api_key=OPENAI_API_KEY, model=MODEL)
    return model_client
