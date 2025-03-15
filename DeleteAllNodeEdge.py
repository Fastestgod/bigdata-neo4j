from neo4j import GraphDatabase
from Neo4jSetup import get_driver

driver = get_driver()

def delete_all_nodes_and_edges():
    with driver.session() as session:
        # Delete all relationships first (Neo4j requires relationships to be deleted before nodes)
        session.run("MATCH ()-[r]->() DELETE r")
        
        # Delete all nodes
        session.run("MATCH (n) DELETE n")
        
        print("All nodes and relationships have been deleted.")

# Call the function
delete_all_nodes_and_edges()
