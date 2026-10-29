
import re
from datetime import datetime
from typing import Optional

import litellm
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext
from google.genai import types

# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()
litellm.modify_params = True

MODEL = "groq/qwen/qwen3.8-27b"


# --------------------------------------------------
# Phase 5: PII Guardrail using regex
# --------------------------------------------------

PII_PATTERNS = {
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),
    "PHONE": re.compile(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
    ),
    "AADHAAR": re.compile(
        r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)"
    ),
    "CREDIT_CARD": re.compile(
        r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"
    ),
}


def block_pii(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """
    Block the model call if the latest user message contains
    detectable PII.
    """

    contents = llm_request.contents

    if not contents:
        return None

    # Find the most recent user message rather than assuming
    # the last content item is always from the user.
    content = next(
        (
            item
            for item in reversed(contents)
            if item.role == "user"
        ),
        None,
    )

    if content is None:
        return None

    user_text = " ".join(
        part.text
        for part in (content.parts or [])
        if part.text
    )

    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(user_text):
            # Never print the sensitive value.
            print(f"PII guardrail triggered: {pii_type}")

            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            text=(
                                "Your message contains potentially "
                                "sensitive personal information. "
                                "Please remove it and try again."
                            )
                        )
                    ],
                )
            )

    # No PII detected: allow the model call.
    return None


# --------------------------------------------------
# Phase 3: Session state / memory tool
# --------------------------------------------------

def remember_name(
    name: str,
    tool_context: ToolContext,
) -> dict:
    """Save the user's name in session state."""

    tool_context.state["user_name"] = name

    return {
        "status": "saved",
        "name": name,
    }


# --------------------------------------------------
# Phase 2: Time tool
# --------------------------------------------------

def get_current_time() -> dict:
    """Return the current date and time."""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "current_time": now,
    }


# --------------------------------------------------
# Phase 4: Greeting sub-agent
# --------------------------------------------------

greeting_agent = Agent(
    name="greeting_agent",
    model=LiteLlm(model=MODEL),
    description="Handles greetings and friendly small talk.",
    instruction=(
        "You are warm and friendly. "
        "Greet the user kindly and answer simple small-talk questions."
    ),
)


# --------------------------------------------------
# Phase 4: Time sub-agent
# --------------------------------------------------

time_agent = Agent(
    name="time_agent",
    model=LiteLlm(model=MODEL),
    description="Answers questions about the current date and time.",
    instruction=(
        "You answer questions about the current date and time. "
        "Use the get_current_time tool when needed."
    ),
    tools=[get_current_time],
)


# --------------------------------------------------
# Root agent: Router + PII guardrail
# --------------------------------------------------

root_agent = Agent(
    name="my_agent",
    model=LiteLlm(model=MODEL),
    description="Main router agent with a PII guardrail.",
    instruction="""
You are a router agent.

Routing rules:
1. Use greeting_agent for greetings and friendly small talk.
2. Use time_agent for questions about the current date and time.
3. Do not claim to have saved a user's name unless the
   remember_name tool has actually been called.
""",
    sub_agents=[
        greeting_agent,
        time_agent,
    ],
    before_model_callback=block_pii,
)
