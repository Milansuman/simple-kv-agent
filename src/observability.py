from netra import Netra, SpanType
import os
from dotenv import load_dotenv
import uuid
import git
from langchain.messages import AIMessage, ToolMessage, HumanMessage
from typing import List

load_dotenv()

NETRA_API_KEY = os.getenv("NETRA_API_KEY")
NETRA_ENDPOINT = os.getenv("NETRA_OTLP_ENDPOINT")

if not NETRA_API_KEY or not NETRA_ENDPOINT:
    raise ValueError("NETRA_API_KEY and NETRA_OTLP_ENDPOINT environment variables must be set.")

HEADERS = f"x-api-key={NETRA_API_KEY}"
def initialize_netra():
    print("Initializing Netra observability...")
    Netra.init(
        app_name="kv-github-agent",
        headers=HEADERS,
        trace_content=True,
        disable_batch=True
    )
    Netra.set_tenant_id("kv-interns")

def initialize_netra_session():
    print("Initializing Netra session...")
    Netra.set_session_id(uuid.uuid4().hex)
    Netra.set_user_id(git.get_author_info()["name"])

def record_agent_thought_process(messages: List[AIMessage | ToolMessage | HumanMessage], model: str):
    with Netra.start_span("agent_thought_process") as span:
        span.set_llm_system("groq")
        span.set_model(model)

        for message in messages:
            if isinstance(message, AIMessage):
                with Netra.start_span("ai_response", as_type=SpanType.GENERATION) as ai_span:
                    ai_span.set_attribute("content", message.content)
                    if "reasoning_content" in message.additional_kwargs.keys():
                        ai_span.set_attribute("reasoning_content", message.additional_kwargs["reasoning_content"])
            elif isinstance(message, ToolMessage):
                with Netra.start_span("tool_call", as_type=SpanType.TOOL) as tool_span:
                    tool_span.set_attribute("tool_name", message.name)
                    tool_span.set_attribute("tool_output", message.content)
            elif isinstance(message, HumanMessage):
                with Netra.start_span("user_message", as_type=SpanType.GENERATION) as user_span:
                    user_span.set_attribute("content", message.content)

        span.set_success()