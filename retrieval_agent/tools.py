import os
from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()



bi_encoder = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')

cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cuda')


base_dir = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "indexing", "qdrant_db")
qdrant_client = QdrantClient(path=db_path)
print("Models and Database Loaded successfully!")


@tool
def search_policies(query: str) -> str:
    """
    Use this tool to answer questions about company policies, return rules, 
    refunds, shipping SLAs, or warranty information. 
    
    CRITICAL INSTRUCTION FOR AGENT: 
    The policy document uses broad categories like 'Electronics', 'Peripherals', and 'Groceries'. 
    If the user asks about a specific item (e.g., 'headphones', 'mouse', 'avocados'), 
    you MUST generalize the query to its broad category before searching. 
    
    Examples: 
    - If user asks "refund for headphones", your query MUST be "refund policy for Electronics".
    - If user asks "shipping for mouse", your query MUST be "shipping policy for Peripherals".
    """
    print(f"\n[Agent Routing] Accessing Vector DB for policy info: '{query}'")
    
    query_vector = bi_encoder.encode(query).tolist()
    
    response = qdrant_client.query_points(
        collection_name="ecommerce_policies",
        query=query_vector,
        limit=20
    )
    
    if not response.points:
        return "No relevant policy found."


    chunks = [hit.payload['content'] for hit in response.points]

    pairs = [[query, chunk] for chunk in chunks]
    

    scores = cross_encoder.predict(pairs)
    
    scored_chunks = list(zip(scores, chunks))
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    top_3_chunks = [chunk for score, chunk in scored_chunks[:3]]
    
    return "\n\n---\n\n".join(top_3_chunks)


# --- Tool 2: The Structured Graph Database (Product Catalog) ---

@tool

def search_catalog(search_term: str) -> str:

    """
    Use this tool to answer questions about specific products, pricing,
    specifications, ratings, categories, or brands.
   

    CRITICAL INSTRUCTION FOR AGENT:
    The Graph Database requires strict keyword matching.
    You MUST extract a single, broad keyword (like a brand name or category) to use as the search_term.
    - If the user asks for "Sony headphones", the search_term MUST be exactly "Sony".
    - If the user asks for "Apple wireless earbuds", the search_term MUST be exactly "Apple".
    Do NOT pass multi-word conversational phrases.
    """
    print(f"\n[Agent Routing] Accessing Graph DB for product info: '{search_term}'")
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USERNAME")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    cypher_query = """
    MATCH (p:Product)-[:BELONGS_TO]->(c:Category)
    MATCH (p)-[:PRODUCED_BY]->(b:Brand)
    WHERE toLower(p.name) CONTAINS toLower($search_term)
       OR toLower(c.name) CONTAINS toLower($search_term)
       OR toLower(b.name) CONTAINS toLower($search_term)
    RETURN p.name AS name, p.price AS price, p.rating AS rating,
           p.specs AS specs, b.name AS brand, c.name AS category
    LIMIT 5
    """

    with driver.session() as session:
        result = session.run(cypher_query, search_term=search_term)
        records = result.data()

    driver.close()
   
    if not records:
        return f"No products found matching keyword '{search_term}'."

    formatted_results = []
    for r in records:
        formatted_results.append(
            f"Product: {r['name']} (Brand: {r['brand']}, Category: {r['category']}) | "
            f"Price: ${r['price']} | Rating: {r['rating']}/5.0 | Specs: {r['specs']}"
        )
    return "\n".join(formatted_results)

# Bundle tools for the agent
ecommerce_tools = [search_policies, search_catalog]
