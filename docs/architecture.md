# PartSelect AI Agent Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (React)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │Conversational│  │   Product    │  │   Real-time Updates  │ │
│  │      UI      │  │    Cards     │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  API Gateway (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Request    │  │Authentication│  │   Rate Limiting      │ │
│  │   Routing    │  │              │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Agent Core                              │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Intent     │  ──► │   Entity     │  ──► │    Scope     │ │
│  │ Classifier   │      │  Extractor   │      │  Validator   │ │
│  └──────────────┘      └──────────────┘      └──────┬───────┘ │
│                                                      │         │
│                                                      ▼         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Tool Orchestrator                            │ │
│  │  ┌────────────────┐  ┌────────────────────────────────┐  │ │
│  │  │Product Search  │  │   Compatibility Check          │  │ │
│  │  └────────────────┘  └────────────────────────────────┘  │ │
│  │  ┌────────────────┐  ┌────────────────────────────────┐  │ │
│  │  │Installation    │  │   Troubleshooting              │  │ │
│  │  │Guide           │  │                                │  │ │
│  │  └────────────────┘  └────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────┬────────────┬────────────┬────────────┬────────────┘
             │            │            │            │
    ┌────────┘            │            │            └────────┐
    ▼                     ▼            ▼                     ▼
┌─────────┐      ┌────────────────┐ ┌──────────┐      ┌──────────┐
│Deepseek │      │   Vector DB    │ │PartSelect│      │  Redis   │
│   LLM   │      │   (Pinecone)   │ │   API    │      │  Cache   │
│         │      │                │ │          │      │          │
│Natural  │      │Semantic Search │ │ Product  │      │ Session  │
│Language │      │  Embeddings    │ │Catalog   │      │ Storage  │
└─────────┘      └────────────────┘ └──────────┘      └──────────┘
```

## Data Flow

```
User Query
    │
    ▼
Frontend (React UI)
    │
    ▼
API Gateway (Authentication, Rate Limiting)
    │
    ▼
Intent Classifier (Determine user goal)
    │
    ▼
Entity Extractor (Extract key information)
    │
    ▼
Scope Validator (Validate request scope)
    │
    ▼
Tool Orchestrator (Select and execute tools)
    │
    ├─► Deepseek LLM (Generate response)
    ├─► Vector DB (Semantic search)
    ├─► PartSelect API (Product data)
    └─► Redis Cache (Check cache/store)
    │
    ▼
Response Assembly
    │
    ▼
API Gateway
    │
    ▼
Frontend (Display to user)
```

## Project Structure

```
partselect-ai-agent/
├── frontend/
|   ├── public/
|   |   ├── index.html
|   |   ├── manifest.json
│   ├── src/
│   │   ├── api/
│   │   │   ├── api.js
│   │   ├── components/
│   │   │   ├── ChatWindow.css
│   │   │   └── ChatWindow.js
│   │   ├── App.css
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── reportWebVitals.js
│   │   └── setupTests.js
│   ├── package.json
│   └── package-lock.json
│
├── backend/
│   ├── app/
│   |   ├── __init__.py
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── core.py           # Main agent logic
│   │   │   ├── intent.py         # Intent classification
│   │   │   └── tools.py          # Tool implementations
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py         # API endpoints
│   │   │   └── middleware.py     # Rate limiting, auth
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py        # Pydantic models
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── deepseek.py       # Deepseek integration
│   │       ├── vector_db.py      # Vector DB client
│   │       └── cache.py          # Redis caching
│   ├── data/
│   │   ├── products.json         # Product catalog
│   │   └── compatibility.json    # Compatibility matrix
│   ├── tests/
│   │   ├── test_agent.py
│   │   ├── test_intent.py
│   │   └── test_api.py
|   ├── scripts/
|   │   └──  setup_vector_db.py   # Initialize vector database
│   ├── main.py                   # Application entry point
│   ├── README.md
│   ├── .env
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/
│   └── ARCHITECTURE.md
│
├── .github/
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline
│
├── docker-compose.yml
├── README.md
└── LICENSE
```