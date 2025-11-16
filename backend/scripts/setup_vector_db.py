"""
Initialize Vector Database with Products and Troubleshooting Guides
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.vector_db import get_vector_db_service


def load_json_file(filepath):
    """Load JSON data from file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def initialize_database():
    """Initialize vector database with products and guides"""
    print("Initializing Vector Database...")
    
    # Get vector DB service
    vector_db = get_vector_db_service()
    
    # Load products
    print("Loading products...")
    products_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'products.json'
    )
    products = load_json_file(products_file)
    
    # Add products to database
    print(f"Adding {len(products)} products to vector database...")
    vector_db.add_products(products)
    print("✓ Products added successfully")
    
    # Load troubleshooting guides
    print("Loading troubleshooting guides...")
    guides_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'troubleshooting.json'
    )
    guides = load_json_file(guides_file)
    
    # Add guides to database
    print(f"Adding {len(guides)} troubleshooting guides to vector database...")
    vector_db.add_troubleshooting_guides(guides)
    print("✓ Troubleshooting guides added successfully")
    
    # Test search
    print("\nTesting vector search...")
    test_results = vector_db.search_products("ice maker", n_results=3)
    print(f"Found {len(test_results)} products for 'ice maker'")
    for product in test_results:
        print(f"  - {product['name']} ({product['part_number']})")
    
    print("\n✓ Vector database initialized successfully!")
    print(f"Database location: {vector_db.persist_directory}")


if __name__ == "__main__":
    initialize_database()