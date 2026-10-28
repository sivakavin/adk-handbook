import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import litellm
litellm.modify_params=True
## Phase2 - Adding tool functionality
from datetime import datetime
load_dotenv()

def get_current_time() ->dict:
    """Returns the current date and time."""
    now =datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time":now}


root_agent=Agent(
    name="my_agent",
    model=LiteLlm(model="groq/qwen/qwen3.8-27b"),
    description="A simple assistant agent",
    instruction="""You are a helpful assistant.Answer the user's question clearly.
    Use your tools when relevant.
    """,
    tools=[get_current_time],
)