"""
Vector Database Service using ChromaDB
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import json
import os
from sentence_transformers import SentenceTransformer


class VectorDBService:
    """Service for managing product embeddings and semantic search"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Use local sentence transformer for embeddings
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        MODEL_PATH = os.path.join(BASE_DIR, "models", "all-MiniLM-L6-v2")

        print("Loading local model from:", MODEL_PATH)
        self.embedding_model = SentenceTransformer(MODEL_PATH)

        # Initialize collections
        self.products_collection = self._get_or_create_collection("products")
        self.guides_collection = self._get_or_create_collection("installation_guides")
        self.troubleshooting_collection = self._get_or_create_collection("troubleshooting")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_products(self, products: List[Dict[str, Any]]):
        """Add products to the vector database"""
        documents = []
        metadatas = []
        ids = []
        
        for product in products:
            # Create searchable text from product
            text = f"{product['name']} {product['description']} {product['part_number']}"
            documents.append(text)
            metadatas.append(product)
            ids.append(product['part_number'])
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()

        # Convert metadata lists/dicts → JSON strings (Chroma requirement)
        safe_metadatas = []
        for meta in metadatas:
            clean_meta = {}
            for k, v in meta.items():
                if isinstance(v, (list, dict)):
                    clean_meta[k] = json.dumps(v)
                else:
                    clean_meta[k] = v
            safe_metadatas.append(clean_meta)

        # Use safe metadata
        self.products_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=safe_metadatas,
            ids=ids
        )

    
    def search_products(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for products using semantic similarity
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of matching products
        """
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.products_collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=filter_dict
        )
        
        products = []
        if results['metadatas']:
            for metadata in results['metadatas'][0]:
                products.append(metadata)
        
        return products
    
    def get_product_by_part_number(self, part_number: str) -> Dict[str, Any]:
        """Get product by exact part number"""
        try:
            result = self.products_collection.get(
                ids=[part_number]
            )
            if result['metadatas']:
                return result['metadatas'][0]
        except:
            pass
        return None
    
    def check_compatibility(
        self,
        part_number: str,
        model_number: str
    ) -> bool:
        """
        Check if a part is compatible with a model
        
        Args:
            part_number: Part number to check
            model_number: Model number to check against
            
        Returns:
            True if compatible, False otherwise
        """
        product = self.get_product_by_part_number(part_number)
        if product and 'compatibility' in product:
            return model_number.upper() in [m.upper() for m in product['compatibility']]
        return False
    
    def add_troubleshooting_guides(self, guides: List[Dict[str, Any]]):
        """Add troubleshooting guides to the database"""
        documents = []
        metadatas = []
        ids = []
        
        for i, guide in enumerate(guides):
            text = f"{guide['problem']} {guide['solution']}"
            documents.append(text)
            metadatas.append(guide)
            ids.append(f"guide_{i}")
        
        embeddings = self.embedding_model.encode(documents).tolist()

        # CLEAN METADATA: convert lists/dicts → JSON strings
        safe_metadatas = []
        for meta in metadatas:
            clean_meta = {}
            for k, v in meta.items():
                if isinstance(v, (list, dict)):
                    clean_meta[k] = json.dumps(v)
                else:
                    clean_meta[k] = v
            safe_metadatas.append(clean_meta)

        self.troubleshooting_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=safe_metadatas,   # ✔ use cleaned metadata
            ids=ids
        )

    
    def search_troubleshooting(
        self,
        problem_description: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for troubleshooting guides"""
        query_embedding = self.embedding_model.encode([problem_description]).tolist()
        
        results = self.troubleshooting_collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        guides = []
        if results['metadatas']:
            for metadata in results['metadatas'][0]:
                guides.append(metadata)
        
        return guides


# Singleton instance
_vector_db_service = None


def get_vector_db_service() -> VectorDBService:
    """Get or create VectorDB service instance"""
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service