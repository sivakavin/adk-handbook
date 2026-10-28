import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import litellm
litellm.modify_params=True

load_dotenv()

root_agent=Agent(
    name="my_agent",
    model=LiteLlm(model="groq/qwen/qwen3.8-27b"),
    description="A simple assistant agent",
    instruction="You are a helpful assistant.Answer the user's question clearly"
)