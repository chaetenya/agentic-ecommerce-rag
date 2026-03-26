import os
import random
from faker import Faker
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

fake = Faker()

# 1. GRAPH DENSITY ENGINEERING: 
# We restrict to 50 Brands and 15 Categories. 
# This forces the 5,000 products to heavily overlap, creating a dense, multi-hop graph.
BRANDS = [fake.company() for _ in range(50)]
# Injecting our known test cases so your previous prompts still work
BRANDS.extend(["Sony", "Logitech", "Apple"]) 

CATEGORIES = [
    "Electronics", "Peripherals", "Audio", "Monitors", "Keyboards", 
    "Mice", "Cables", "Networking", "Storage", "Accessories",
    "Smart Home", "Gaming", "Cameras", "Wearables", "Components"
]

def generate_products(num_products=5000):
    """Generates a list of dictionaries representing synthetic products."""
    print(f"Generating {num_products} synthetic products in memory...")
    products = []
    for _ in range(num_products):
        product = {
            "sku": fake.unique.uuid4()[:8],
            "name": f"{fake.word().capitalize()} {fake.word().capitalize()} {random.randint(10, 900)}",
            "price": round(random.uniform(10.0, 1500.0), 2),
            "rating": round(random.uniform(1.0, 5.0), 1),
            "specs": fake.sentence(nb_words=6),
            "brand": random.choice(BRANDS),
            "category": random.choice(CATEGORIES)
        }
        products.append(product)
        
    # Inject our specific test product so we know the agent still works
    products.append({
        "sku": "WH1000XM4", "name": "Sony WH-1000XM4", "price": 298.0, 
        "rating": 4.8, "specs": "Noise-cancelling, 30-hour battery, over-ear", 
        "brand": "Sony", "category": "Electronics"
    })
    return products

def batch_insert_to_neo4j(products, batch_size=1000):
    """Inserts products into Neo4j using optimized UNWIND batching."""
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    # The Cypher UNWIND command takes a massive JSON array and processes it 
    # directly on the database server, drastically reducing network round-trips.
    cypher_query = """
    UNWIND $batch AS row
    
    // 1. Create or match the parent nodes
    MERGE (c:Category {name: row.category})
    MERGE (b:Brand {name: row.brand})
    
    // 2. Create the specific product
    MERGE (p:Product {sku: row.sku})
    SET p.name = row.name,
        p.price = toFloat(row.price),
        p.rating = toFloat(row.rating),
        p.specs = row.specs
        
    // 3. Draw the relationships (The Edges)
    MERGE (p)-[:BELONGS_TO]->(c)
    MERGE (p)-[:PRODUCED_BY]->(b)
    """
    
    with driver.session() as session:
        # Wipe the database clean before loading to avoid duplicates during testing
        print("Clearing existing database...")
        session.run("MATCH (n) DETACH DELETE n")
        
        print(f"Executing batch inserts (Batch size: {batch_size})...")
        # Split the 5,000 products into chunks to respect cloud memory limits
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            session.run(cypher_query, batch=batch)
            print(f"Inserted records {i} to {i + len(batch)}...")
            
    driver.close()
    print("Database seeding complete!")

if __name__ == "__main__":
    dataset = generate_products(5000)
    batch_insert_to_neo4j(dataset)