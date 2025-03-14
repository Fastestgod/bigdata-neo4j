from neo4j import GraphDatabase

#connect to db
URI = "bolt://localhost:7687"  
AUTH = ("neo4j", "project123")

def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)

if __name__ == "__main__":
    driver = get_driver()
    print("Connected to Neo4j successfully!")