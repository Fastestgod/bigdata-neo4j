from neo4j import GraphDatabase

# Initialize Neo4j driver
uri = "bolt://localhost:7687"  # Adjust if your Neo4j instance is elsewhere
username = "neo4j"  # Default username for Neo4j
password = "project123"  # Replace with your actual password
driver = GraphDatabase.driver(uri, auth=(username, password))

def delete_all_nodes_and_edges():
    with driver.session() as session:
        # Delete all relationships first (Neo4j requires relationships to be deleted before nodes)
        session.run("MATCH ()-[r]->() DELETE r")
        
        # Delete all nodes
        session.run("MATCH (n) DELETE n")
        
        print("All nodes and relationships have been deleted.")

# Call the function
delete_all_nodes_and_edges()
