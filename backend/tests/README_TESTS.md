# Testing Guide - PartSelect AI Agent

## Overview

This document provides comprehensive information about the test suite for the PartSelect AI Agent backend.

## Test Structure

```
backend/tests/
├── __init__.py              # Tests package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_intent.py           # Intent classification tests (45+ tests)
├── test_agent.py            # Agent core logic tests (30+ tests)
├── test_api.py              # API endpoint tests (35+ tests)
└── test_tools.py            # Tools module tests (40+ tests)
```

**Total Test Count:** 150+ tests

## Test Categories

### 1. Unit Tests
- **Intent Classification** (`test_intent.py`)
  - Pattern matching tests
  - Entity extraction tests
  - LLM fallback tests
  - Edge cases and error handling

- **Agent Tools** (`test_tools.py`)
  - Individual tool functionality
  - Tool execution
  - Error handling
  - Input validation

### 2. Integration Tests
- **Agent Core** (`test_agent.py`)
  - Message processing flow
  - Tool calling integration
  - Conversation management
  - Multi-turn conversations

- **API Endpoints** (`test_api.py`)
  - Complete request/response cycles
  - Multi-step workflows
  - Error scenarios

### 3. API Tests
- Health check endpoints
- Chat endpoint (various scenarios)
- Conversation management
- CORS and error handling

## Running Tests

### Prerequisites

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install test dependencies
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run with detailed output
pytest -vv
```

### Run Specific Test Files

```bash
# Run intent tests only
pytest tests/test_intent.py

# Run API tests only
pytest tests/test_api.py

# Run agent tests only
pytest tests/test_agent.py

# Run tools tests only
pytest tests/test_tools.py
```

### Run Specific Test Classes or Functions

```bash
# Run specific test class
pytest tests/test_intent.py::TestIntentClassifier

# Run specific test function
pytest tests/test_intent.py::TestIntentClassifier::test_classify_installation_pattern

# Run tests matching a pattern
pytest -k "installation"
```

### Run Tests by Markers

```bash
# Run only async tests
pytest -m asyncio

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View coverage in terminal
pytest --cov=app --cov-report=term-missing

# Generate XML coverage report (for CI/CD)
pytest --cov=app --cov-report=xml

# Set minimum coverage threshold
pytest --cov=app --cov-fail-under=70
```

View HTML coverage report:
```bash
# Open htmlcov/index.html in your browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
```