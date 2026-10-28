import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import litellm
litellm.modify_params=True
# Phase2 - Adding tool functionality
from datetime import datetime
# Phase3 - Add session & state
from google.adk.tools import ToolContext
load_dotenv()

def remember_name(name:str,tool_context:ToolContext) ->dict:
    """Saves the user's name to memory"""
    tool_context.state["user_name"]=name
    return {"status":"saved","name":name}

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
    The user's name is {user_name?}.Greet them by name if you know it.
    """,
    tools=[get_current_time,remember_name],
)