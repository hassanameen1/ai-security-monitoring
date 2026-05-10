import logging
import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import AsyncAzureOpenAI
from pydantic import BaseModel

load_dotenv()

from rag import format_context, retrieve  # noqa: E402  (import after load_dotenv)

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
    "You are an HR assistant for Al-Riyadh Holdings. Answer using only the provided context. "
    "If the context does not contain the answer, say you don't know. Cite sources by doc_id."
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    docs = retrieve(req.prompt)
    context = format_context(docs)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Context:\n{context}"},
        {"role": "user", "content": req.prompt},
    ]
    try:
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
    return ChatResponse(
        response=completion.choices[0].message.content,
        sources=[d["doc_id"] for d in docs],
    )