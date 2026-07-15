import weaviate
import os
from typing import List, Dict

class Retriever:
    """Retrieves relevant context from the Knowledge Graph / Vector DB."""
    
    def __init__(self):
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.client = None
        
        try:
            self.client = weaviate.connect_to_local(
                host="localhost",
                port=8080
            )
        except Exception as e:
            print(f"WARNING: Could not connect to Weaviate: {e}. Running in MOCK mode.")

    def query(self, query_text: str, limit: int = 3) -> List[Dict]:
        """
        Semantic search for principles relevant to the query.
        """
        if not self.client:
            return [
                {"content": "When debt growth > income growth, the economy is over-leveraged.", "source": "Principles (Mock)", "category": "Debt"},
                {"content": "In a deleveraging, policymakers must print money to bridge the gap.", "source": "Principles (Mock)", "category": "Deleveraging"}
            ]

        collection = self.client.collections.get("Principle")
        
        try:
            # Connect to local transformers
            response = collection.query.near_text(
                query=query_text,
                limit=limit
            )
            
            results = []
            for obj in response.objects:
                results.append({
                    "content": obj.properties["content"],
                    "source": obj.properties["source"],
                    "category": obj.properties["category"]
                })
            
            return results
            
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []

    def close(self):
        if self.client:
            self.client.close()

if __name__ == "__main__":
    ret = Retriever()
    results = ret.query("How to deleverage?")
    for r in results:
        print(f"Found: {r['content'][:50]}...")
    ret.close()
