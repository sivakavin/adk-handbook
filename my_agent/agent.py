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
# Phase4 - Multi agent


def remember_name(name:str,tool_context:ToolContext) ->dict:
    """Saves the user's name to memory"""
    tool_context.state["user_name"]=name
    return {"status":"saved","name":name}

def get_current_time() ->dict:
    """Returns the current date and time."""
    now =datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time":now}


# Defining Agent
greeting_agent= Agent(
    name="greeting_agent",
    model=LiteLlm(model="groq/qwen/qwen3.8-27b"),
    description="Handles greeting and friendly small talk.",
    instruction="You are warm and friendly.Greet the user kindly.",
)

time_agent=Agent(
    name="time_agent",
    model=LiteLlm(model="groq/qwen/qwen3.8-27b"),
    description="Answer questions about the current date and time",
    instruction="You tell the user the current time.Use your tools.",
    tools=[get_current_time],
)

root_agent=Agent(
    name="my_agent",
    model=LiteLlm(model="groq/qwen/qwen3.8-27b"),
    description="Main router agent.",
    instruction="""You are a router.Look at the user's request and hand it to the
    right specilist.
    Use greeting_agent for greetings and small task.
    Use time_agent for anything about date and time.""",
    sub_agents=[greeting_agent,time_agent],
)