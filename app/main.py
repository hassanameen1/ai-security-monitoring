import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncAzureOpenAI
from pydantic import BaseModel

load_dotenv()

from function_tools import TOOL_REGISTRY, TOOL_SCHEMAS  # noqa: E402
from rag import format_context, retrieve  # noqa: E402  (import after load_dotenv)
from telemetry import build_record, log_interaction, new_session_id  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Security Monitoring - Chatbot")

client = AsyncAzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

DEPLOYMENT = os.environ["AZURE_OPENAI_DEPLOYMENT"]


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    response: str
    sources: list[str]


SYSTEM_PROMPT = (
    "You are an HR assistant for Al-Riyadh Holdings. You have two information sources:\n"
    "1. Knowledge base context (policies, org chart) — cite by doc_id.\n"
    "2. Tools (list_employees, get_employee_details, get_department_info) for live employee/department data.\n"
    "Use the knowledge base for policies and structure; call the tools for specific employee or department queries. "
    "If neither source has the answer, say you don't know."
)


app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")


@app.get("/")
def root():
    return RedirectResponse(url="/ui/chat.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    x_user_groups: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> ChatResponse:
    session_id = new_session_id()
    started = time.monotonic()
    user_id = x_user_id or "anonymous"
    groups = [g.strip() for g in x_user_groups.split(",")] if x_user_groups else []
    captured_tool_calls: list[dict] = []

    docs = retrieve(req.prompt, groups=groups)
    context = format_context(docs)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Context:\n{context}"},
        {"role": "user", "content": req.prompt},
    ]
    try:
        completion = await client.chat.completions.create(
            model=DEPLOYMENT,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )
        message = completion.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for call in message.tool_calls:
                fn = TOOL_REGISTRY[call.function.name]
                args = json.loads(call.function.arguments)
                captured_tool_calls.append({"name": call.function.name, "args": args})
                logger.info("tool_call: %s args=%s", call.function.name, args)
                result = fn(**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, default=str),
                })
            completion = await client.chat.completions.create(model=DEPLOYMENT, messages=messages)
    except (openai.APIConnectionError, openai.APITimeoutError) as e:
        logger.error("upstream_unavailable: %s", e)
        raise HTTPException(
            status_code=503,
            detail={"error": "upstream_unavailable", "message": "AI service is unreachable"},
        )
    except openai.APIStatusError as e:
        logger.error("upstream_error status=%s: %s", e.status_code, e)
        raise HTTPException(
            status_code=502,
            detail={"error": "upstream_error", "status": e.status_code},
        )

    response_text = completion.choices[0].message.content
    elapsed_ms = int((time.monotonic() - started) * 1000)
    record = build_record(
        time_generated=datetime.now(timezone.utc).isoformat(),
        session_id=session_id,
        user_id=user_id,
        user_groups=groups,
        prompt=req.prompt,
        response=response_text,
        sources=[d["doc_id"] for d in docs],
        tool_calls=captured_tool_calls,
        latency_ms=elapsed_ms,
        prompt_tokens=completion.usage.prompt_tokens,
        completion_tokens=completion.usage.completion_tokens,
    )
    asyncio.create_task(log_interaction(record))

    return ChatResponse(response=response_text, sources=[d["doc_id"] for d in docs])