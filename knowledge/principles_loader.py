import weaviate
import os
import json
from typing import List, Dict

class PrinciplesLoader:
    """Handles the ingestion of text principles into the Vector Database."""
    
    def __init__(self):
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        
        # Connect to Weaviate
        self.client = weaviate.connect_to_local(
            host="localhost",
            port=8080
        )

    def create_schema(self):
        """Defines the schema for Principles."""
        try:
             # Check if collection exists
             if self.client.collections.exists("Principle"):
                 print("Collection 'Principle' already exists.")
                 return

             self.client.collections.create(
                name="Principle",
                properties=[
                    weaviate.classes.config.Property(name="content", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="source", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="category", data_type=weaviate.classes.config.DataType.TEXT),
                ],
                vectorizer_config=weaviate.classes.config.Configure.Vectorizer.text2vec_transformers()
            )
             print("Created schema for 'Principle' using Local Transformers.")
        except Exception as e:
            print(f"Error creating schema: {e}")

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Simple paragraph-based chunking."""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for p in paragraphs:
            if len(current_chunk) + len(p) > chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = p
            else:
                current_chunk += "\n\n" + p
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def load_file(self, file_path: str, category: str = "General"):
        """Reads a file, chunks it, and uploads to Weaviate."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        chunks = self.chunk_text(content)
        print(f"Loading {len(chunks)} chunks from {file_path}...")
        
        collection = self.client.collections.get("Principle")
        
        with collection.batch.dynamic() as batch:
            for i, chunk in enumerate(chunks):
                batch.add_object(
                    properties={
                        "content": chunk,
                        "source": os.path.basename(file_path),
                        "category": category
                    }
                )
        
        print("Upload complete.")

    def close(self):
        self.client.close()

if __name__ == "__main__":
    # Test script
    # Create a dummy principle file
    with open("sample_principles.md", "w") as f:
        f.write("# Economic Principles\n\nWhen debt grows faster than income, it is sustainable only if the debt is used to create productivity.\n\nIf the interest rate is lower than the growth rate, you can deleverage beautifully.")
        
    loader = PrinciplesLoader()
    loader.create_schema()
    loader.load_file("sample_principles.md", "Debt Cycles")
    loader.close()
    os.remove("sample_principles.md")
