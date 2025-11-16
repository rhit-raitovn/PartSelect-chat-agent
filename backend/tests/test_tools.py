"""
Tests for Agent Tools Module
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.agent.tools import AgentTools, get_agent_tools


class TestAgentTools:
    """Test suite for AgentTools"""
    
    @pytest.fixture
    def tools(self):
        """Create tools instance with mocked vector DB"""
        with patch('app.agent.tools.get_vector_db_service'):
            return AgentTools()
    
    def test_initialization(self, tools):
        """Test tools initializes correctly"""
        assert tools is not None
        assert hasattr(tools, 'vector_db')
    
    # Tool Definitions Tests
    
    def test_get_tool_definitions(self, tools):
        """Test tool definitions are properly formatted"""
        definitions = tools.get_tool_definitions()
        
        assert isinstance(definitions, list)
        assert len(definitions) == 5  # Should have 5 tools
        
        # Check each tool has required fields
        for tool_def in definitions:
            assert 'type' in tool_def
            assert tool_def['type'] == 'function'
            assert 'function' in tool_def
            assert 'name' in tool_def['function']
            assert 'description' in tool_def['function']
            assert 'parameters' in tool_def['function']
    
    def test_tool_definitions_have_correct_names(self, tools):
        """Test all expected tools are defined"""
        definitions = tools.get_tool_definitions()
        tool_names = [tool['function']['name'] for tool in definitions]
        
        expected_tools = [
            'search_products',
            'get_product_by_part_number',
            'check_compatibility',
            'get_installation_instructions',
            'search_troubleshooting'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    # Search Products Tests
    
    @pytest.mark.asyncio
    async def test_search_products_basic(self, tools):
        """Test basic product search"""
        mock_products = [
            {'part_number': 'PS11752778', 'name': 'Ice Maker', 'category': 'refrigerator'}
        ]
        tools.vector_db.search_products = Mock(return_value=mock_products)
        
        result = await tools._search_products(query="ice maker")
        
        assert result['count'] == 1
        assert len(result['products']) == 1
        assert result['products'][0]['part_number'] == 'PS11752778'
    
    @pytest.mark.asyncio
    async def test_search_products_with_category_filter(self, tools):
        """Test product search with category filter"""
        mock_products = [
            {'part_number': 'PS11752778', 'name': 'Ice Maker', 'category': 'refrigerator'}
        ]
        tools.vector_db.search_products = Mock(return_value=mock_products)
        
        result = await tools._search_products(
            query="ice maker",
            category="refrigerator",
            limit=5
        )
        
        # Verify filter was passed to vector DB
        tools.vector_db.search_products.assert_called_once()
        call_args = tools.vector_db.search_products.call_args
        assert call_args[1]['filter_dict'] == {'category': 'refrigerator'}
    
    @pytest.mark.asyncio
    async def test_search_products_empty_results(self, tools):
        """Test product search with no results"""
        tools.vector_db.search_products = Mock(return_value=[])
        
        result = await tools._search_products(query="nonexistent")
        
        assert result['count'] == 0
        assert result['products'] == []
    
    @pytest.mark.asyncio
    async def test_search_products_limit(self, tools):
        """Test product search respects limit"""
        mock_products = [
            {'part_number': f'PS{i}', 'name': f'Product {i}'} for i in range(10)
        ]
        tools.vector_db.search_products = Mock(return_value=mock_products[:3])
        
        result = await tools._search_products(query="test", limit=3)
        
        tools.vector_db.search_products.assert_called_once()
        call_args = tools.vector_db.search_products.call_args
        assert call_args[1]['n_results'] == 3
    
    # Get Product by Part Number Tests
    
    @pytest.mark.asyncio
    async def test_get_product_by_part_number_found(self, tools):
        """Test getting product by part number when found"""
        mock_product = {
            'part_number': 'PS11752778',
            'name': 'Ice Maker Assembly',
            'price': 124.99
        }
        tools.vector_db.get_product_by_part_number = Mock(return_value=mock_product)
        
        result = await tools._get_product_by_part_number(part_number='PS11752778')
        
        assert 'product' in result
        assert result['product']['part_number'] == 'PS11752778'
    
    @pytest.mark.asyncio
    async def test_get_product_by_part_number_not_found(self, tools):
        """Test getting product by part number when not found"""
        tools.vector_db.get_product_by_part_number = Mock(return_value=None)
        
        result = await tools._get_product_by_part_number(part_number='PSNONEXISTENT')
        
        assert 'error' in result
        assert 'not found' in result['error'].lower()
    
    # Check Compatibility Tests
    
    @pytest.mark.asyncio
    async def test_check_compatibility_compatible(self, tools):
        """Test checking compatibility when parts are compatible"""
        mock_product = {
            'part_number': 'PS11752778',
            'compatibility': ['WDT780SAEM1', 'WRS325SDHZ']
        }
        tools.vector_db.check_compatibility = Mock(return_value=True)
        tools.vector_db.get_product_by_part_number = Mock(return_value=mock_product)
        
        result = await tools._check_compatibility(
            part_number='PS11752778',
            model_number='WDT780SAEM1'
        )
        
        assert result['compatible'] is True
        assert result['part_number'] == 'PS11752778'
        assert result['model_number'] == 'WDT780SAEM1'
        assert 'WDT780SAEM1' in result['compatible_models']
    
    @pytest.mark.asyncio
    async def test_check_compatibility_not_compatible(self, tools):
        """Test checking compatibility when parts are not compatible"""
        mock_product = {
            'part_number': 'PS11752778',
            'compatibility': ['MODEL1', 'MODEL2']
        }
        tools.vector_db.check_compatibility = Mock(return_value=False)
        tools.vector_db.get_product_by_part_number = Mock(return_value=mock_product)
        
        result = await tools._check_compatibility(
            part_number='PS11752778',
            model_number='INCOMPATIBLE'
        )
        
        assert result['compatible'] is False
        assert 'compatible_models' in result
        assert 'INCOMPATIBLE' not in result['compatible_models']
    
    @pytest.mark.asyncio
    async def test_check_compatibility_product_not_found(self, tools):
        """Test compatibility check when product doesn't exist"""
        tools.vector_db.check_compatibility = Mock(return_value=False)
        tools.vector_db.get_product_by_part_number = Mock(return_value=None)
        
        result = await tools._check_compatibility(
            part_number='PSNONEXISTENT',
            model_number='WDT780SAEM1'
        )
        
        assert result['compatible'] is False
        assert result['compatible_models'] == []
    
    # Get Installation Instructions Tests
    
    @pytest.mark.asyncio
    async def test_get_installation_instructions_available(self, tools):
        """Test getting installation instructions when available"""
        mock_product = {
            'part_number': 'PS11752778',
            'installation_guide_url': 'https://example.com/guide',
            'installation_steps': '1. Step one\n2. Step two'
        }
        tools.vector_db.get_product_by_part_number = Mock(return_value=mock_product)
        
        result = await tools._get_installation_instructions(part_number='PS11752778')
        
        assert 'installation_url' in result
        assert result['installation_url'] == 'https://example.com/guide'
        assert 'instructions' in result
    
    @pytest.mark.asyncio
    async def test_get_installation_instructions_not_available(self, tools):
        """Test getting installation instructions when not available"""
        mock_product = {
            'part_number': 'PS11752778',
            'name': 'Product without guide'
        }
        tools.vector_db.get_product_by_part_number = Mock(return_value=mock_product)
        
        result = await tools._get_installation_instructions(part_number='PS11752778')
        
        assert 'error' in result
        assert 'suggestion' in result
    
    @pytest.mark.asyncio
    async def test_get_installation_instructions_product_not_found(self, tools):
        """Test installation instructions for non-existent product"""
        tools.vector_db.get_product_by_part_number = Mock(return_value=None)
        
        result = await tools._get_installation_instructions(part_number='PSNONEXISTENT')
        
        assert 'error' in result
    
    # Search Troubleshooting Tests
    
    @pytest.mark.asyncio
    async def test_search_troubleshooting_basic(self, tools):
        """Test basic troubleshooting search"""
        mock_guides = [
            {
                'problem': 'Ice maker not working',
                'solution': 'Check water supply',
                'brand': 'Whirlpool'
            }
        ]
        tools.vector_db.search_troubleshooting = Mock(return_value=mock_guides)
        
        result = await tools._search_troubleshooting(problem="ice maker not working")
        
        assert result['count'] == 1
        assert len(result['guides']) == 1
        assert 'Ice maker' in result['guides'][0]['problem']
    
    @pytest.mark.asyncio
    async def test_search_troubleshooting_with_brand_filter(self, tools):
        """Test troubleshooting search with brand filter"""
        mock_guides = [
            {
                'problem': 'Ice maker not working',
                'solution': 'Check water supply',
                'brand': 'Whirlpool'
            }
        ]
        tools.vector_db.search_troubleshooting = Mock(return_value=mock_guides)
        
        result = await tools._search_troubleshooting(
            problem="ice maker not working",
            brand="Whirlpool"
        )
        
        assert result['count'] == 1
        assert result['guides'][0]['brand'] == 'Whirlpool'
    
    @pytest.mark.asyncio
    async def test_search_troubleshooting_brand_filter_no_match(self, tools):
        """Test troubleshooting search filters out non-matching brands"""
        mock_guides = [
            {'problem': 'Issue', 'brand': 'Whirlpool'},
            {'problem': 'Issue', 'brand': 'GE'},
            {'problem': 'Issue', 'brand': 'Samsung'}
        ]
        tools.vector_db.search_troubleshooting = Mock(return_value=mock_guides)
        
        result = await tools._search_troubleshooting(
            problem="some issue",
            brand="Whirlpool"
        )
        
        # Should only return Whirlpool guides
        assert all(guide['brand'] == 'Whirlpool' for guide in result['guides'])
    
    @pytest.mark.asyncio
    async def test_search_troubleshooting_empty_results(self, tools):
        """Test troubleshooting search with no results"""
        tools.vector_db.search_troubleshooting = Mock(return_value=[])
        
        result = await tools._search_troubleshooting(problem="rare issue")
        
        assert result['count'] == 0
        assert result['guides'] == []
    
    # Execute Tool Tests
    
    @pytest.mark.asyncio
    async def test_execute_tool_search_products(self, tools):
        """Test executing search_products tool"""
        tools.vector_db.search_products = Mock(return_value=[])
        
        result = await tools.execute_tool(
            tool_name='search_products',
            arguments={'query': 'test', 'category': 'all', 'limit': 5}
        )
        
        assert 'products' in result
        assert 'count' in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_get_product(self, tools):
        """Test executing get_product_by_part_number tool"""
        mock_product = {'part_number': 'PS11752778'}
        tools.vector_db.get_product_by_part_number = Mock(return_value=mock_product)
        
        result = await tools.execute_tool(
            tool_name='get_product_by_part_number',
            arguments={'part_number': 'PS11752778'}
        )
        
        assert 'product' in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_check_compatibility(self, tools):
        """Test executing check_compatibility tool"""
        tools.vector_db.check_compatibility = Mock(return_value=True)
        tools.vector_db.get_product_by_part_number = Mock(return_value={'compatibility': []})
        
        result = await tools.execute_tool(
            tool_name='check_compatibility',
            arguments={'part_number': 'PS11752778', 'model_number': 'WDT780SAEM1'}
        )
        
        assert 'compatible' in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_get_installation(self, tools):
        """Test executing get_installation_instructions tool"""
        tools.vector_db.get_product_by_part_number = Mock(return_value=None)
        
        result = await tools.execute_tool(
            tool_name='get_installation_instructions',
            arguments={'part_number': 'PS11752778'}
        )
        
        assert 'error' in result or 'installation_url' in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_search_troubleshooting(self, tools):
        """Test executing search_troubleshooting tool"""
        tools.vector_db.search_troubleshooting = Mock(return_value=[])
        
        result = await tools.execute_tool(
            tool_name='search_troubleshooting',
            arguments={'problem': 'not working'}
        )
        
        assert 'guides' in result
        assert 'count' in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_unknown_tool(self, tools):
        """Test executing unknown tool returns error"""
        result = await tools.execute_tool(
            tool_name='nonexistent_tool',
            arguments={}
        )
        
        assert 'error' in result
        assert 'Unknown tool' in result['error']
    
    # Singleton Pattern Test
    
    def test_get_agent_tools_singleton(self):
        """Test get_agent_tools returns instance"""
        with patch('app.agent.tools.get_vector_db_service'):
            tools = get_agent_tools()
            assert tools is not None
            assert isinstance(tools, AgentTools)


class TestToolsIntegration:
    """Integration tests for tools with realistic scenarios"""
    
    @pytest.fixture
    def configured_tools(self):
        """Create tools with configured mocks"""
        with patch('app.agent.tools.get_vector_db_service'):
            tools = AgentTools()
            # Setup realistic vector DB mock
            tools.vector_db.search_products = Mock()
            tools.vector_db.get_product_by_part_number = Mock()
            tools.vector_db.check_compatibility = Mock()
            tools.vector_db.search_troubleshooting = Mock()
            return tools
    
    @pytest.mark.asyncio
    async def test_complete_product_search_flow(self, configured_tools):
        """Test complete flow of searching and getting product details"""
        # Step 1: Search for products
        search_results = [
            {'part_number': 'PS11752778', 'name': 'Ice Maker', 'category': 'refrigerator'}
        ]
        configured_tools.vector_db.search_products = Mock(return_value=search_results)
        
        search_result = await configured_tools._search_products("ice maker")
        assert search_result['count'] == 1
        
        # Step 2: Get detailed info on found product
        detailed_product = {
            'part_number': 'PS11752778',
            'name': 'Ice Maker Assembly',
            'price': 124.99,
            'compatibility': ['WDT780SAEM1']
        }
        configured_tools.vector_db.get_product_by_part_number = Mock(
            return_value=detailed_product
        )
        
        detail_result = await configured_tools._get_product_by_part_number('PS11752778')
        assert detail_result['product']['price'] == 124.99
        
        # Step 3: Check compatibility
        configured_tools.vector_db.check_compatibility = Mock(return_value=True)
        configured_tools.vector_db.get_product_by_part_number = Mock(
            return_value=detailed_product
        )
        
        compat_result = await configured_tools._check_compatibility(
            'PS11752778',
            'WDT780SAEM1'
        )
        assert compat_result['compatible'] is True