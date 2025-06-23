import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()
model = os.getenv('MODEL')
api_key = os.getenv("ANTHROPIC_API_KEY")


llm = LLM(
    model=model,
    api_key=api_key,
)