"""Logs Ingestion API client for AIInteractions_CL.

Best-effort: telemetry failure must never break /chat.
"""

import logging
import os
import uuid
from typing import Any

from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient

logger = logging.getLogger(__name__)

_credential = DefaultAzureCredential()
_client = LogsIngestionClient(
    endpoint=os.environ["DCE_INGESTION_ENDPOINT"],
    credential=_credential,
)
_RULE_ID = os.environ["DCR_IMMUTABLE_ID"]
_STREAM = os.environ["LAW_STREAM_NAME"]


def new_session_id() -> str:
    return str(uuid.uuid4())


def build_record(
    *,
    time_generated: str,
    session_id: str,
    user_id: str,
    user_groups: list[str],
    prompt: str,
    response: str,
    sources: list[str],
    tool_calls: list[dict],
    latency_ms: int,
    prompt_tokens: int,
    completion_tokens: int,
    prompt_shield_verdict: str | None = None,
    prompt_shield_categories: list[str] | None = None,
    output_eval_verdict: str | None = None,
    output_eval_findings: list[dict] | None = None,
    blocked_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "TimeGenerated": time_generated,
        "session_id": session_id,
        "user_id": user_id,
        "user_groups": user_groups,
        "prompt": prompt,
        "response": response,
        "sources": sources,
        "tool_calls": tool_calls,
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "prompt_shield_verdict": prompt_shield_verdict,
        "prompt_shield_categories": prompt_shield_categories,
        "output_eval_verdict": output_eval_verdict,
        "output_eval_findings": output_eval_findings,
        "blocked_reason": blocked_reason,
    }


async def log_interaction(record: dict) -> None:
    try:
        await _client.upload(rule_id=_RULE_ID, stream_name=_STREAM, logs=[record])
    except Exception as e:
        logger.warning("telemetry_upload_failed: %s", e)
