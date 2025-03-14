import os
import pandas as pd
from Neo4jSetup import get_driver

driver = get_driver()
BATCH_SIZE = 10000

nodes_file = "data/nodes.tsv"  
edges_file = "data/edges.tsv"  

def insert_nodes():
    nodes_file = "data/sample_nodes.tsv"  
    nodes_df = pd.read_csv(nodes_file, sep="\t", skiprows=1, header=None, names=["full_id", "name", "kind"])

    with driver.session() as session:
        for _, row in nodes_df.iterrows():
            full_id = row["full_id"]
            name = row["name"]
            kind = row["kind"]

            # detect n determine the id
            category, node_id = full_id.split("::", 1)  

            # Validate and assign proper labels
            if category == "Anatomy":
                label = "Anatomy"
            elif category == "Disease":
                label = "Disease"
            elif category == "Gene":
                label = "Gene"
            elif category == "Compound":
                label = "Compound"

            # Insert into Neo4j
            session.run(
                f"""
                MERGE (n:{label} {{id: $id, name: $name}})
                """,
                id=node_id, name=name
            )
    
    print("Inserted nodes successfully.")

def insert_edges():
    edges_file = "data/sample_edges.tsv"

    if not os.path.exists(edges_file):
        print(f"Error: File {edges_file} not found!")
        return

    edges_df = pd.read_csv(edges_file, sep="\t", skiprows=1, header=None, names=["full_source", "metaedge", "full_target"])
    
    with driver.session() as session:
        batch = []
        for _, row in edges_df.iterrows():
           
            source_category, source_id = row["full_source"].split("::", 1)
            target_category, target_id = row["full_target"].split("::", 1)
            relation_type = row["metaedge"]

            batch.append({"source_id": source_id, "target_id": target_id, "relation_type": relation_type})

            
            if len(batch) >= BATCH_SIZE:
                session.run(
                    """
                    UNWIND $batch AS edge
                    MATCH (a {id: edge.source_id})
                    MATCH (b {id: edge.target_id})
                    MERGE (a)-[r:RELATIONSHIP {type: edge.relation_type}]->(b)
                    """,
                    batch=batch
                )
                batch = []  # Clear batch

        # Insert remaining edges if any
        if batch:
            session.run(
                """
                UNWIND $batch AS edge
                MATCH (a {id: edge.source_id})
                MATCH (b {id: edge.target_id})
                MERGE (a)-[r:RELATIONSHIP {type: edge.relation_type}]->(b)
                """,
                batch=batch
            )

    print("Edges inserted successfully.")
if __name__ == "__main__":
    #insert_nodes()
    insert_edges()
    print("Data insertion completed successfully!")
