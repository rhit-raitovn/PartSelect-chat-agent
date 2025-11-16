┌─────────────────────────────────────────────────────┐
│                  Frontend (React)                    │
│  - Conversational UI                                 │
│  - Product Cards                                     │
│  - Real-time Updates                                 │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              API Gateway (FastAPI)                   │
│  - Request Routing                                   │
│  - Authentication                                    │
│  - Rate Limiting                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                  Agent Core                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │   Intent   │  │  Entity    │  │   Scope    │   │
│  │Classifier  │→ │ Extractor  │→ │ Validator  │   │
│  └────────────┘  └────────────┘  └────────────┘   │
│                       │                              │
│                       ▼                              │
│  ┌─────────────────────────────────────────────┐   │
│  │           Tool Orchestrator                  │   │
│  │  - Product Search                            │   │
│  │  - Compatibility Check                       │   │
│  │  - Installation Guide                        │   │
│  │  - Troubleshooting                           │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌─────────┐  ┌──────────┐
│ Deepseek │  │  Vector DB   │  │PartSelect│  │  Redis   │
│   LLM    │  │  (Pinecone)  │  │   API   │  │  Cache   │
└──────────┘  └──────────────┘  └─────────┘  └──────────┘



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