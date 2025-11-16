"""
Shared test fixtures and configuration
"""
import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def sample_product():
    """Sample product for testing"""
    return {
        'part_number': 'PS11752778',
        'name': 'Ice Maker Assembly',
        'description': 'Complete ice maker assembly for refrigerators',
        'price': 124.99,
        'category': 'refrigerator',
        'compatibility': ['WDT780SAEM1', 'WRS325SDHZ'],
        'image_url': 'https://example.com/image.jpg',
        'installation_guide_url': 'https://example.com/guide'
    }


@pytest.fixture
def sample_products():
    """List of sample products for testing"""
    return [
        {
            'part_number': 'PS11752778',
            'name': 'Ice Maker Assembly',
            'description': 'Ice maker for refrigerators',
            'price': 124.99,
            'category': 'refrigerator',
            'compatibility': ['WDT780SAEM1']
        },
        {
            'part_number': 'PS11757302',
            'name': 'Water Inlet Valve',
            'description': 'Water inlet valve',
            'price': 45.99,
            'category': 'refrigerator',
            'compatibility': ['WRS325SDHZ']
        },
        {
            'part_number': 'PS2366603',
            'name': 'Dishwasher Spray Arm',
            'description': 'Lower spray arm assembly',
            'price': 34.99,
            'category': 'dishwasher',
            'compatibility': ['WDT780SAEM1']
        }
    ]


@pytest.fixture
def sample_troubleshooting_guide():
    """Sample troubleshooting guide for testing"""
    return {
        'problem': 'Ice maker not working',
        'brand': 'Whirlpool',
        'appliance': 'refrigerator',
        'solution': 'Check water supply and ice maker switch',
        'common_parts': ['PS11752778', 'PS11757302'],
        'difficulty': 'moderate'
    }


@pytest.fixture
def sample_conversation_messages():
    """Sample conversation messages for testing"""
    return [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi! How can I help you?'},
        {'role': 'user', 'content': 'I need an ice maker'},
        {'role': 'assistant', 'content': 'I can help you find the right ice maker.'}
    ]


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # This ensures clean state for each test
    import app.agent.core as core_module
    import app.agent.intent as intent_module
    import app.agent.tools as tools_module
    import app.services.deepseek as deepseek_module
    import app.services.vector_db as vector_db_module
    import app.services.cache as cache_module
    
    # Reset all module-level singleton variables
    if hasattr(core_module, '_agent'):
        core_module._agent = None
    if hasattr(deepseek_module, '_deepseek_service'):
        deepseek_module._deepseek_service = None
    if hasattr(vector_db_module, '_vector_db_service'):
        vector_db_module._vector_db_service = None
    if hasattr(cache_module, '_cache_service'):
        cache_module._cache_service = None
    
    yield
    
    # Clean up after test
    if hasattr(core_module, '_agent'):
        core_module._agent = None


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'test-api-key-123')
    monkeypatch.setenv('DEBUG', 'true')
    monkeypatch.setenv('VECTOR_DB_PATH', './test_chroma_db')
    monkeypatch.setenv('CACHE_TTL', '3600')


# Async test support
pytest_plugins = ['pytest_asyncio']


def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )