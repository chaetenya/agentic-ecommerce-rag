import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

def build_knowledge_graph():
    print("Connecting to Neo4j AuraDB")
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    # Read the structured CSV data we generated earlier
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, "raw_data", "product_catalog.csv")
    df = pd.read_csv(csv_path)
    
    # The Cypher Query
    cypher_query = """
    UNWIND $rows AS row
    
    // Create the Core Nodes
    MERGE (c:Category {name: row.category})
    MERGE (b:Brand {name: row.brand})
    MERGE (p:Product {id: row.product_id})
    
    // Set the properties on the Product Node
    SET p.name = row.name, 
        p.price = toFloat(row.price), 
        p.specs = row.specs, 
        p.rating = toFloat(row.avg_rating)
        
    // Create the Relationships (The Edges)
    MERGE (p)-[:BELONGS_TO]->(c)
    MERGE (p)-[:PRODUCED_BY]->(b)
    """
    
    # Execute the pipeline
    print("Building Graph Nodes and Relationships")
    with driver.session() as session:
        session.run(cypher_query, rows=df.to_dict('records'))
    
    print("Knowledge Graph successfully populated")
    driver.close()

if __name__ == "__main__":
    build_knowledge_graph()
