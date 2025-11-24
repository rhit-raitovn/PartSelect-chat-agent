# Instalily Case Study Submission

**Naziia Raitova's Submission for PartSelect AI Agent**

---

## Presentation
https://docs.google.com/presentation/d/1-YNhvWx7w5N1cOra2-lBCzmH4X9imUSGFXzmfd5HBew/edit?slide=id.g3a4420436e5_0_1401#slide=id.g3a4420436e5_0_1401

### 1. Source Code (Complete & Production-Ready)

**Location:** `partselect-ai-agent/` folder

- **Backend:** FastAPI + DeepSeek LLM
- **Frontend:** React chat interface
- **Infrastructure:** Docker, setup scripts, configuration
- **Data:** Sample products and troubleshooting guides


### 2. Documentation 

**Technical Documentation:**
- `README.md` - Main documentation
- `docs/ARCHITECTURE.md` - Technical deep dive + Code organization + Visual architecture

---

## How to Test the Submission

### Quick Start (Windows PowerShell)

```powershell
# 1. Navigate to project
cd partselect-ai-agent

# 2. Run automated setup
.\setup.ps1

# 3. Add your DEEPSEEK_API_KEY or OPENROUTER_API_KEY

# 4. Start the application
.\start-all.ps1

# 5. Open browser to http://localhost:3000
```

### Test Queries

Once running, try these:

1. "How can I install part number PS11752778?"
2. "Is this part compatible with my WDT780SAEM1 model?"
3. "The ice maker on my Whirlpool fridge is not working"
4. **Out of Scope:** "Can you help with my washing machine?"

---

## Technology Stack

**Backend:**
- FastAPI (async Python web framework)
- DeepSeek LLM (function calling)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)
- Pydantic (validation)

**Frontend:**
- React 18 (UI framework)
- Modern CSS (flexbox, grid)
- Fetch API (HTTP client)

**Infrastructure:**
- Docker & Docker Compose
- ChromaDB (local storage)
- In-memory caching

