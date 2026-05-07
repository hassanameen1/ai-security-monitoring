# AI Security Monitoring & Threat Detection Platform

Detection and response for LLM-powered applications. Inline security gateway, server-side RAG access control, behavioral KQL detections in Microsoft Sentinel, automated playbooks.

**Status:** In development.

---

## The Problem

Companies deploy LLM chatbots, copilots, and AI agents with effectively zero security monitoring. No detection for prompt injection. No visibility into data leakage through AI responses. No behavioral analytics on AI usage. No detection of RAG poisoning or function calling abuse.

Microsoft has shipped prevention tooling (Content Safety, Prompt Shields, Defender for AI preview), but there is no "Sentinel for AI" that provides detection, behavioral analytics, and automated response for AI workloads. This project builds that missing layer.

---

## Architecture

```
User
  │
  ▼
Security Gateway (FastAPI middleware)
  ├── INPUT: Azure AI Content Safety Prompt Shields + custom watchlist
  ├── If ALLOWED → Azure OpenAI (GPT-4o-mini)
  │     ├── RAG: Azure AI Search with Entra ID group security filters
  │     └── Function calling: mock HR database
  └── OUTPUT: PII pattern scan + classification check
                  │
                  ▼
        Telemetry (direct Logs Ingestion API)
                  │
                  ▼
        Log Analytics Workspace → Microsoft Sentinel
              ├── KQL detections × 5 (injection, leakage, anomaly, function abuse, RAG poisoning)
              ├── Automation rules → Logic App playbooks
              └── Sentinel workbook (AI Security Operations Dashboard)
```

---

## What Makes This Different

1. **Inline security gateway** — prompts and responses are evaluated in real time before reaching the user, not detected after the fact.
2. **Server-side RAG access control** — document access enforced by Entra ID groups at the Azure AI Search query level, not by the system prompt. The model never sees documents the user isn't authorized to access.
3. **Defense in depth** — Content Safety Prompt Shields (ML-based, broad) running alongside KQL pattern + behavioral detections (org-specific, tunable, post-hoc analytics).

---

## Tech Stack

| Component | Technology |
|---|---|
| AI model | Azure OpenAI Service (GPT-4o-mini) |
| Knowledge base | Azure AI Search (free tier) |
| Application | Python (FastAPI) on Azure App Service B1 |
| Security gateway | FastAPI middleware |
| Content Safety | Azure AI Content Safety — Prompt Shields |
| Identity | Microsoft Entra ID (group-based RAG security filters) |
| Telemetry | Direct Logs Ingestion API → Log Analytics |
| Detection | Microsoft Sentinel — KQL analytics rules |
| Response | Logic Apps (consumption tier) |
| IaC | Terraform (`azurerm` provider) |
| Region | `swedencentral` |

---

## Detections (planned)

| # | Detection | Type | MITRE | Auto-remediate? |
|---|---|---|---|---|
| 1 | Prompt injection (watchlist + Prompt Shields verdict) | Pattern + behavioral | T1059 / ATLAS AML.T0051 | Block session |
| 2 | Data leakage (PII regex against responses) | Pattern | T1530 | Alert + redact |
| 3 | Anomalous usage (per-user rate vs baseline) | Behavioral | T1078 | Alert only |
| 4 | Function calling abuse (enumeration patterns) | Behavioral | T1087 | Alert only |
| 5 | RAG poisoning (document-add ↔ response-change correlation) | Behavioral | ATLAS AML.T0051 | Alert only |

---

## Repository Structure (target)

```
ai-security-monitoring/
├── README.md
├── CLAUDE.md                           # project spec
├── architecture/
│   ├── diagram.mmd
│   └── threat-model.md                 # STRIDE + MITRE ATLAS mapping
├── app/
│   ├── main.py                         # FastAPI chatbot
│   ├── security_gateway.py             # inline input/output evaluation
│   ├── rag.py                          # AI Search + group-based security filter
│   ├── function_tools.py               # mock HR database tools
│   ├── telemetry.py                    # Logs Ingestion API client
│   └── requirements.txt
├── data/
│   ├── knowledge_base/                 # fake company docs (4 classification levels)
│   ├── mock_hr_db.json                 # fake employee data
│   └── injection_watchlist.csv         # known injection patterns
├── terraform/
│   └── modules/                        # openai, ai-search, content-safety, app-service, loganalytics, sentinel-rules, logic-apps, identity
├── kql/
│   ├── detection-prompt-injection.kql
│   ├── detection-data-leakage.kql
│   ├── detection-anomalous-usage.kql
│   ├── detection-function-abuse.kql
│   ├── detection-rag-poisoning.kql
│   └── workbook-queries/
├── tests/
│   └── attack_scenarios/               # scripted demo attacks
└── screenshots/
```

---

## Production Architecture (what I'd build differently at scale)

To be expanded as the project ships. Highlights:

- Purview DLP integration for semantic data leakage detection (vs regex)
- Multi-application monitoring with tenant-aware telemetry routing
- Compliance audit trail with immutable storage (WORM)
- Model supply chain security (MITRE ATLAS AML.T0020 reference)
- ML-based injection classification (fine-tuned model vs watchlist)
- Full SOAR integration with ServiceNow/Jira ticketing

---

## Companion Project

Builds on the same Sentinel + KQL + Logic App + Terraform foundation as my cloud security auto-remediation project: [defender-sentinel-pipeline](https://github.com/hassanameen1/defender-sentinel-pipeline).

Two-project narrative: cloud security operations + AI security operations.
