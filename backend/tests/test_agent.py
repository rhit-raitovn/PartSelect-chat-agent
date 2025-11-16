"""
Tests for Agent Core Module
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.agent.core import PartSelectAgent, get_agent
from app.models.schemas import IntentType, Intent, Product


class TestPartSelectAgent:
    """Test suite for PartSelectAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance with mocked dependencies"""
        with patch('app.agent.core.get_deepseek_service'), \
             patch('app.agent.core.get_intent_classifier'), \
             patch('app.agent.core.get_agent_tools'):
            return PartSelectAgent()
    
    def test_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent is not None
        assert hasattr(agent, 'deepseek')
        assert hasattr(agent, 'intent_classifier')
        assert hasattr(agent, 'tools')
        assert hasattr(agent, 'conversations')
        assert agent.system_prompt is not None
    
    # Message Processing Tests
    
    @pytest.mark.asyncio
    async def test_process_message_new_conversation(self, agent):
        """Test processing message in new conversation"""
        # Mock intent classification
        mock_intent = Intent(
            intent_type=IntentType.PRODUCT_INFO,
            confidence=0.85,
            entities={'part_number': 'PS11752778'}
        )
        agent.intent_classifier.classify = AsyncMock(return_value=mock_intent)
        
        # Mock LLM response
        mock_llm_response = {
            'content': 'Here is information about the part.',
            'tool_calls': None,
            'finish_reason': 'stop'
        }
        agent.deepseek.chat_completion = AsyncMock(return_value=mock_llm_response)
        
        response = await agent.process_message("Tell me about PS11752778")
        
        assert response is not None
        assert response.message == 'Here is information about the part.'
        assert response.conversation_id is not None
        assert response.intent.intent_type == IntentType.PRODUCT_INFO
    
    @pytest.mark.asyncio
    async def test_process_message_existing_conversation(self, agent):
        """Test processing message in existing conversation"""
        conversation_id = "test-conv-123"
        
        # Mock intent and LLM
        mock_intent = Intent(intent_type=IntentType.GENERAL, confidence=0.7, entities={})
        agent.intent_classifier.classify = AsyncMock(return_value=mock_intent)
        
        mock_llm_response = {
            'content': 'Response message',
            'tool_calls': None,
            'finish_reason': 'stop'
        }
        agent.deepseek.chat_completion = AsyncMock(return_value=mock_llm_response)
        
        # First message
        await agent.process_message("First message", conversation_id)
        
        # Second message - should maintain conversation
        response = await agent.process_message("Second message", conversation_id)
        
        assert response.conversation_id == conversation_id
        assert len(agent.conversations[conversation_id]) >= 2
    
    @pytest.mark.asyncio
    async def test_process_out_of_scope_message(self, agent):
        """Test handling of out-of-scope messages"""
        mock_intent = Intent(
            intent_type=IntentType.OUT_OF_SCOPE,
            confidence=0.9,
            entities={}
        )
        agent.intent_classifier.classify = AsyncMock(return_value=mock_intent)
        
        response = await agent.process_message("Help with my washing machine")
        
        assert response is not None
        assert "refrigerator" in response.message.lower() or "dishwasher" in response.message.lower()
        assert response.intent.intent_type == IntentType.OUT_OF_SCOPE
    
    # Tool Calling Tests
    
    @pytest.mark.asyncio
    async def test_process_message_with_tool_calls(self, agent):
        """Test message processing with tool calls"""
        # Mock intent
        mock_intent = Intent(
            intent_type=IntentType.PRODUCT_INFO,
            confidence=0.9,
            entities={'part_number': 'PS11752778'}
        )
        agent.intent_classifier.classify = AsyncMock(return_value=mock_intent)
        
        # Mock tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "get_product_by_part_number"
        mock_tool_call.function.arguments = '{"part_number": "PS11752778"}'
        
        # Mock first LLM response with tool calls
        mock_llm_response_1 = {
            'content': None,
            'tool_calls': [mock_tool_call],
            'finish_reason': 'tool_calls'
        }
        
        # Mock second LLM response after tool execution
        mock_llm_response_2 = {
            'content': 'Here is the product information you requested.',
            'tool_calls': None,
            'finish_reason': 'stop'
        }
        
        agent.deepseek.chat_completion = AsyncMock(
            side_effect=[mock_llm_response_1, mock_llm_response_2]
        )
        
        # Mock tool execution
        mock_product = {
            'part_number': 'PS11752778',
            'name': 'Ice Maker Assembly',
            'price': 124.99,
            'category': 'refrigerator',
            'description': 'Ice maker for refrigerators',
            'compatibility': ['WDT780SAEM1']
        }
        agent.tools.execute_tool = AsyncMock(return_value={'product': mock_product})
        
        response = await agent.process_message("Get info on PS11752778")
        
        assert response is not None
        assert len(response.products) == 1
        assert response.products[0].part_number == 'PS11752778'
    
    # Conversation Management Tests
    
    def test_clear_conversation(self, agent):
        """Test clearing conversation history"""
        conversation_id = "test-conv-123"
        agent.conversations[conversation_id] = [
            {"role": "user", "content": "Hello"}
        ]
        
        agent.clear_conversation(conversation_id)
        
        assert conversation_id not in agent.conversations
    
    def test_get_conversation_history(self, agent):
        """Test retrieving conversation history"""
        conversation_id = "test-conv-123"
        agent.conversations[conversation_id] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        history = agent.get_conversation_history(conversation_id)
        
        assert len(history) == 2
        assert history[0].content == "Hello"
        assert history[1].content == "Hi there!"
    
    def test_get_nonexistent_conversation(self, agent):
        """Test retrieving history for non-existent conversation"""
        history = agent.get_conversation_history("nonexistent-id")
        
        assert history == []
    
    # Context Window Management Tests
    
    @pytest.mark.asyncio
    async def test_context_window_limit(self, agent):
        """Test conversation history is limited to last 10 messages"""
        conversation_id = "test-conv-123"
        
        # Mock intent and LLM
        mock_intent = Intent(intent_type=IntentType.GENERAL, confidence=0.7, entities={})
        agent.intent_classifier.classify = AsyncMock(return_value=mock_intent)
        
        mock_llm_response = {
            'content': 'Response',
            'tool_calls': None,
            'finish_reason': 'stop'
        }
        agent.deepseek.chat_completion = AsyncMock(return_value=mock_llm_response)
        
        # Add 15 messages
        for i in range(15):
            await agent.process_message(f"Message {i}", conversation_id)
        
        # Check that LLM only receives last 10 messages
        last_call_args = agent.deepseek.chat_completion.call_args
        messages = last_call_args[1]['messages']
        
        # Should be system prompt + last 10 conversation messages
        assert len([m for m in messages if m['role'] != 'system']) <= 10
    
    # Suggested Actions Tests
    
    def test_generate_suggested_actions_product_info(self, agent):
        """Test generating suggested actions for product info intent"""
        intent = Intent(intent_type=IntentType.PRODUCT_INFO, confidence=0.8, entities={})
        products = [
            Product(
                part_number='PS11752778',
                name='Ice Maker',
                description='Test',
                price=99.99,
                category='refrigerator',
                compatibility=[]
            )
        ]
        
        actions = agent._generate_suggested_actions(intent, products)
        
        assert len(actions) > 0
        assert any('detail' in action.lower() for action in actions)
    
    def test_generate_suggested_actions_compatibility(self, agent):
        """Test generating suggested actions for compatibility intent"""
        intent = Intent(intent_type=IntentType.COMPATIBILITY, confidence=0.8, entities={})
        
        actions = agent._generate_suggested_actions(intent, [])
        
        assert len(actions) > 0
        assert any('model' in action.lower() or 'compatible' in action.lower() for action in actions)
    
    def test_generate_suggested_actions_installation(self, agent):
        """Test generating suggested actions for installation intent"""
        intent = Intent(intent_type=IntentType.INSTALLATION, confidence=0.8, entities={})
        
        actions = agent._generate_suggested_actions(intent, [])
        
        assert len(actions) > 0
        assert any('video' in action.lower() or 'guide' in action.lower() for action in actions)
    
    def test_generate_suggested_actions_troubleshooting(self, agent):
        """Test generating suggested actions for troubleshooting intent"""
        intent = Intent(intent_type=IntentType.TROUBLESHOOTING, confidence=0.8, entities={})
        
        actions = agent._generate_suggested_actions(intent, [])
        
        assert len(actions) > 0
        assert any('solution' in action.lower() or 'part' in action.lower() for action in actions)
    
    # Singleton Pattern Test
    
    def test_get_agent_singleton(self):
        """Test get_agent returns singleton instance"""
        with patch('app.agent.core.get_deepseek_service'), \
             patch('app.agent.core.get_intent_classifier'), \
             patch('app.agent.core.get_agent_tools'):
            agent1 = get_agent()
            agent2 = get_agent()
            
            assert agent1 is agent2
    
    # Error Handling Tests
    
    @pytest.mark.asyncio
    async def test_process_message_llm_error(self, agent):
        """Test handling of LLM errors"""
        mock_intent = Intent(intent_type=IntentType.GENERAL, confidence=0.7, entities={})
        agent.intent_classifier.classify = AsyncMock(return_value=mock_intent)
        
        # Mock LLM error
        agent.deepseek.chat_completion = AsyncMock(side_effect=Exception("LLM Error"))
        
        # Should not crash, but handle gracefully
        with pytest.raises(Exception):
            await agent.process_message("Test message")
    
    @pytest.mark.asyncio
    async def test_process_message_intent_classification_error(self, agent):
        """Test handling of intent classification errors"""
        # Mock intent classifier error
        agent.intent_classifier.classify = AsyncMock(side_effect=Exception("Classification Error"))
        
        with pytest.raises(Exception):
            await agent.process_message("Test message")


class TestAgentIntegration:
    """Integration tests for agent with real-like scenarios"""
    
    @pytest.fixture
    def configured_agent(self):
        """Create fully configured agent for integration tests"""
        with patch('app.agent.core.get_deepseek_service'), \
             patch('app.agent.core.get_intent_classifier'), \
             patch('app.agent.core.get_agent_tools'):
            agent = PartSelectAgent()
            
            # Setup realistic mocks
            agent.intent_classifier.classify = AsyncMock()
            agent.deepseek.chat_completion = AsyncMock()
            agent.tools.execute_tool = AsyncMock()
            agent.tools.get_tool_definitions = Mock(return_value=[])
            
            return agent
    
    @pytest.mark.asyncio
    async def test_full_installation_query_flow(self, configured_agent):
        """Test complete flow for installation query"""
        # Setup mocks for realistic scenario
        configured_agent.intent_classifier.classify = AsyncMock(return_value=Intent(
            intent_type=IntentType.INSTALLATION,
            confidence=0.9,
            entities={'part_number': 'PS11752778'}
        ))
        
        configured_agent.deepseek.chat_completion = AsyncMock(return_value={
            'content': 'Here are the installation steps...',
            'tool_calls': None,
            'finish_reason': 'stop'
        })
        
        response = await configured_agent.process_message(
            "How can I install part number PS11752778?"
        )
        
        assert response.intent.intent_type == IntentType.INSTALLATION
        assert 'PS11752778' in response.intent.entities.get('part_number', '')
        assert response.message is not None
    
    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, configured_agent):
        """Test multi-turn conversation maintains context"""
        conversation_id = "multi-turn-test"
        
        # Configure mocks
        configured_agent.intent_classifier.classify = AsyncMock(return_value=Intent(
            intent_type=IntentType.GENERAL,
            confidence=0.7,
            entities={}
        ))
        
        configured_agent.deepseek.chat_completion = AsyncMock(return_value={
            'content': 'Response',
            'tool_calls': None,
            'finish_reason': 'stop'
        })
        
        # Turn 1
        response1 = await configured_agent.process_message(
            "Hello",
            conversation_id
        )
        
        # Turn 2
        response2 = await configured_agent.process_message(
            "Tell me about ice makers",
            conversation_id
        )
        
        # Turn 3
        response3 = await configured_agent.process_message(
            "Which one is best?",
            conversation_id
        )
        
        # All should have same conversation ID
        assert response1.conversation_id == conversation_id
        assert response2.conversation_id == conversation_id
        assert response3.conversation_id == conversation_id
        
        # Conversation should have all messages
        history = configured_agent.get_conversation_history(conversation_id)
        assert len(history) == 6  # 3 user + 3 assistant
        