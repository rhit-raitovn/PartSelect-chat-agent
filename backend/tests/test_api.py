"""
Tests for API Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.api.routes import app
from app.models.schemas import IntentType, Intent, Product, AgentResponse


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Create mock agent"""
    with patch('app.api.routes.get_agent') as mock:
        agent = mock.return_value
        agent.process_message = AsyncMock()
        agent.clear_conversation = AsyncMock()
        agent.get_conversation_history = AsyncMock(return_value=[])
        yield agent


class TestHealthEndpoints:
    """Tests for health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns status"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'online'
        assert 'service' in data
        assert 'version' in data
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'components' in data
        assert data['components']['api'] == 'operational'


class TestChatEndpoint:
    """Tests for /api/chat endpoint"""
    
    def test_chat_endpoint_success(self, client, mock_agent):
        """Test successful chat request"""
        # Mock agent response
        mock_agent_response = AgentResponse(
            message="Here is the information you requested.",
            products=[],
            intent=Intent(
                intent_type=IntentType.PRODUCT_INFO,
                confidence=0.85,
                entities={'part_number': 'PS11752778'}
            ),
            suggested_actions=["View details", "Check compatibility"],
            conversation_id="test-conv-123"
        )
        mock_agent.process_message.return_value = mock_agent_response
        
        # Make request
        response = client.post(
            "/api/chat",
            json={
                "message": "Tell me about PS11752778",
                "conversation_id": None,
                "user_context": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'response' in data
        assert data['response']['message'] == "Here is the information you requested."
        assert data['response']['conversation_id'] == "test-conv-123"
    
    def test_chat_endpoint_with_products(self, client, mock_agent):
        """Test chat response with product recommendations"""
        mock_product = Product(
            part_number='PS11752778',
            name='Ice Maker Assembly',
            description='Complete ice maker unit',
            price=124.99,
            category='refrigerator',
            compatibility=['WDT780SAEM1'],
            image_url='https://example.com/image.jpg'
        )
        
        mock_agent_response = AgentResponse(
            message="Here are the recommended parts:",
            products=[mock_product],
            intent=Intent(
                intent_type=IntentType.PRODUCT_INFO,
                confidence=0.9,
                entities={}
            ),
            suggested_actions=["Add to cart"],
            conversation_id="test-conv-123"
        )
        mock_agent.process_message.return_value = mock_agent_response
        
        response = client.post(
            "/api/chat",
            json={"message": "Show me ice makers"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['response']['products']) == 1
        assert data['response']['products'][0]['part_number'] == 'PS11752778'
        assert data['response']['products'][0]['price'] == 124.99
    
    def test_chat_endpoint_validation_error(self, client):
        """Test chat endpoint with invalid request"""
        response = client.post(
            "/api/chat",
            json={"message": ""}  # Empty message should fail validation
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_endpoint_missing_message(self, client):
        """Test chat endpoint with missing message field"""
        response = client.post(
            "/api/chat",
            json={}
        )
        
        assert response.status_code == 422
    
    def test_chat_endpoint_long_message(self, client, mock_agent):
        """Test chat endpoint with maximum length message"""
        mock_agent_response = AgentResponse(
            message="Response",
            products=[],
            intent=Intent(intent_type=IntentType.GENERAL, confidence=0.7, entities={}),
            suggested_actions=[],
            conversation_id="test"
        )
        mock_agent.process_message.return_value = mock_agent_response
        
        long_message = "A" * 2000  # Max length
        response = client.post(
            "/api/chat",
            json={"message": long_message}
        )
        
        assert response.status_code == 200
    
    def test_chat_endpoint_too_long_message(self, client):
        """Test chat endpoint rejects messages that are too long"""
        too_long_message = "A" * 2001  # Exceeds max
        response = client.post(
            "/api/chat",
            json={"message": too_long_message}
        )
        
        assert response.status_code == 422
    
    def test_chat_endpoint_with_conversation_id(self, client, mock_agent):
        """Test chat endpoint maintains conversation ID"""
        conversation_id = "existing-conv-123"
        
        mock_agent_response = AgentResponse(
            message="Continuing conversation",
            products=[],
            intent=Intent(intent_type=IntentType.GENERAL, confidence=0.7, entities={}),
            suggested_actions=[],
            conversation_id=conversation_id
        )
        mock_agent.process_message.return_value = mock_agent_response
        
        response = client.post(
            "/api/chat",
            json={
                "message": "Follow-up question",
                "conversation_id": conversation_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['response']['conversation_id'] == conversation_id
    
    def test_chat_endpoint_user_context(self, client, mock_agent):
        """Test chat endpoint accepts user context"""
        mock_agent_response = AgentResponse(
            message="Response",
            products=[],
            intent=Intent(intent_type=IntentType.GENERAL, confidence=0.7, entities={}),
            suggested_actions=[],
            conversation_id="test"
        )
        mock_agent.process_message.return_value = mock_agent_response
        
        response = client.post(
            "/api/chat",
            json={
                "message": "Test",
                "user_context": {"user_id": "123", "preferences": {}}
            }
        )
        
        assert response.status_code == 200


class TestConversationEndpoints:
    """Tests for conversation management endpoints"""
    
    def test_clear_conversation_success(self, client, mock_agent):
        """Test clearing conversation"""
        conversation_id = "test-conv-123"
        
        response = client.post(
            f"/api/conversation/clear?conversation_id={conversation_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        mock_agent.clear_conversation.assert_called_once_with(conversation_id)
    
    
    def test_get_conversation_error(self, client, mock_agent):
        """Test error handling when getting conversation"""
        mock_agent.get_conversation_history.side_effect = Exception("Get error")
        
        response = client.get("/api/conversation/test")
        
        assert response.status_code == 500


class TestCORSHeaders:
    """Tests for CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are present in response"""
        response = client.options(
            "/api/chat",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_404_not_found(self, client):
        """Test 404 for non-existent endpoint"""
        response = client.get("/api/nonexistent")
        
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method"""
        response = client.get("/api/chat")  # Should be POST
        
        assert response.status_code == 405


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def test_complete_chat_flow(self, client, mock_agent):
        """Test complete chat interaction flow"""
        # Configure mock for realistic scenario
        mock_product = Product(
            part_number='PS11752778',
            name='Ice Maker Assembly',
            description='Ice maker',
            price=124.99,
            category='refrigerator',
            compatibility=['WDT780SAEM1']
        )
        
        mock_agent_response = AgentResponse(
            message="Here is the ice maker you requested.",
            products=[mock_product],
            intent=Intent(
                intent_type=IntentType.PRODUCT_INFO,
                confidence=0.9,
                entities={'part_number': 'PS11752778'}
            ),
            suggested_actions=["View details", "Check compatibility"],
            conversation_id="integration-test-123"
        )
        mock_agent.process_message.return_value = mock_agent_response
        
        # Step 1: Initial query
        response = client.post(
            "/api/chat",
            json={"message": "I need an ice maker"}
        )
        
        assert response.status_code == 200
        data = response.json()
        conversation_id = data['response']['conversation_id']
        
        # Step 2: Follow-up query
        response2 = client.post(
            "/api/chat",
            json={
                "message": "Is it compatible with WDT780SAEM1?",
                "conversation_id": conversation_id
            }
        )
        
        assert response2.status_code == 200
        assert response2.json()['response']['conversation_id'] == conversation_id
        
        # Step 3: Clear conversation
        response3 = client.post(
            f"/api/conversation/clear?conversation_id={conversation_id}"
        )
        
        assert response3.status_code == 200
        assert response3.json()['success'] is True