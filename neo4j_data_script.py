from neo4j import GraphDatabase

# --- Configuration (Update with your actual credentials) ---
URI = "neo4j://localhost:7687"
USER = "neo4j"
# NOTE: Use the new password you set in the previous step!
PASSWORD = "MySecureNewPassword123" 

# Initialize the driver
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def add_graph_data(tx):
    """
    Creates 10 Movie nodes, 4 Person nodes, and their relationships.
    Uses a single MERGE/CREATE statement for efficiency.
    """
    # Cypher query to create a small sample graph for a movie database
    # MERGE is used to ensure we don't duplicate People/Actors.
    # CREATE is used for Movies and Relationships (since we want unique relationships per run).
    query = """
    MERGE (a:Person {name: 'Tom Hanks'}) 
    MERGE (b:Person {name: 'Meryl Streep'})
    MERGE (c:Person {name: 'Viola Davis'})
    MERGE (d:Person {name: 'Denzel Washington'})
    
    // 1. Forrest Gump (1994)
    CREATE (m1:Movie {title: 'Forrest Gump', released: 1994, tagline: 'Life is like a box of chocolates.'})
    CREATE (a)-[:ACTED_IN {role: 'Forrest'}]->(m1)
    
    // 2. The Post (2017)
    CREATE (m2:Movie {title: 'The Post', released: 2017, tagline: 'The truth belongs to us.'})
    CREATE (a)-[:ACTED_IN {role: 'Ben Bradlee'}]->(m2)
    CREATE (b)-[:ACTED_IN {role: 'Kay Graham'}]->(m2)
    
    // 3. The Devil Wears Prada (2006)
    CREATE (m3:Movie {title: 'The Devil Wears Prada', released: 2006, tagline: 'Hell on heels.'})
    CREATE (b)-[:ACTED_IN {role: 'Miranda Priestly'}]->(m3)
    
    // 4. Fences (2016)
    CREATE (m4:Movie {title: 'Fences', released: 2016, tagline: 'Some walls are built to keep people out. And some walls are built to keep people in.'})
    CREATE (c)-[:ACTED_IN {role: 'Rose Maxson'}]->(m4)
    CREATE (d)-[:ACTED_IN {role: 'Troy Maxson'}]->(m4)

    // 5. Training Day (2001)
    CREATE (m5:Movie {title: 'Training Day', released: 2001, tagline: 'The only thing more dangerous than the street is the man who swore to protect it.'})
    CREATE (d)-[:ACTED_IN {role: 'Alonzo Harris'}]->(m5)

    // 6. Sleepless in Seattle (1993)
    CREATE (m6:Movie {title: 'Sleepless in Seattle', released: 1993, tagline: 'What if they just met?'})
    CREATE (a)-[:ACTED_IN]->(m6)
    
    // 7. Into the Woods (2014)
    CREATE (m7:Movie {title: 'Into the Woods', released: 2014, tagline: 'Be careful what you wish for.'})
    CREATE (b)-[:ACTED_IN]->(m7)

    // 8. Ma Rainey's Black Bottom (2020)
    CREATE (m8:Movie {title: "Ma Rainey's Black Bottom", released: 2020, tagline: 'The mother of the Blues.'})
    CREATE (c)-[:ACTED_IN]->(m8)
    
    // 9. Flight (2012)
    CREATE (m9:Movie {title: 'Flight', released: 2012, tagline: 'The pilot everyone thought was a hero.'})
    CREATE (d)-[:ACTED_IN]->(m9)
    
    // 10. Cast Away (2000)
    CREATE (m10:Movie {title: 'Cast Away', released: 2000, tagline: 'An adventure on an island.'})
    CREATE (a)-[:ACTED_IN]->(m10)
    
    // Count the created nodes and relationships for confirmation
    RETURN count(m1)+count(m2)+count(m3)+count(m4)+count(m5)+count(m6)+count(m7)+count(m8)+count(m9)+count(m10) AS movies_created
    """
    
    # Run the transaction
    result = tx.run(query)
    # The result contains one record with the count of movies
    return result.single()["movies_created"]

def get_schema_summary(tx):
    """
    Retrieves and summarizes the labels and relationship types in the database.
    This mimics showing the basic schema (or "schematic").
    """
    # Cypher query to get all distinct node labels
    label_query = "CALL db.labels() YIELD label RETURN collect(label) AS labels"
    
    # Cypher query to get all distinct relationship types
    rel_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS rels"
    
    # Execute both queries in read transactions
    labels = tx.run(label_query).single()["labels"]
    rels = tx.run(rel_query).single()["rels"]
    
    return labels, rels


# --- Main Execution Logic ---
def main():
    try:
        print(f"Connecting to Neo4j at {URI}...")
        
        # 1. Add Data Transaction
        with driver.session() as session:
            # Clear existing data first for a clean run (optional, but good practice for testing)
            session.run("MATCH (n) DETACH DELETE n")
            print("Cleared existing graph data.")
            
            # Execute the write transaction to add the new data
            movies_created = session.execute_write(add_graph_data)
            print(f"\nSuccessfully added {movies_created} Movie nodes and associated relationships.")
            
        # 2. Schema Summary Transaction
        with driver.session() as session:
            # Execute the read transaction to get schema info
            labels, rels = session.execute_read(get_schema_summary)

            print("\n--- Graph Schema Summary (Schematic) ---")
            print(f"Node Labels Found: {', '.join(labels)}")
            print(f"Relationship Types Found: {', '.join(rels)}")
            print("-" * 35)

    except Exception as e:
        print(f"\nAn error occurred during script execution. Check credentials and container status.")
        print(f"Error: {e}")
        
    finally:
        driver.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()
