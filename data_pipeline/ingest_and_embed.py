import os
import uuid
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

def process_and_embed_policies():
    print("Starting local vectordb pipeline")

    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "raw_data", "company_policies.txt")
    db_path = os.path.join(os.path.dirname(base_dir), "indexing", "qdrant_db")


    print("GPU check, loading 'all-MiniLM-L6-v2' onto CUDA")

    model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
    embedding_size = model.get_sentence_embedding_dimension()

    print("Reading and chunking policy document") 
    with open(data_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, 
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_text(raw_text)
    # print(f"Created {len(chunks)} chunks from the policy text.")

    # Generate Embeddings using the GPU
    # print("Generating dense vector embeddings")
    embeddings = model.encode(chunks, show_progress_bar=True)

    # Initialize Local Qdrant Vector Database
    print("Connecting to local Qdrant Vector DB")
    client = QdrantClient(path=db_path)
    collection_name = "ecommerce_policies"

    # Create collection if it doesn't exist
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_size, distance=Distance.COSINE),
        )

    # Insert Data into Vector DB
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()), 
                vector=embedding.tolist(), 
                payload={"source": "company_policies.txt", "content": chunk}
            )
        )
    
    client.upsert(collection_name=collection_name, points=points)
    print(f"Successfully inserted {len(points)} vectors into Qdrant at {db_path}!")

if __name__ == "__main__":
    process_and_embed_policies()
