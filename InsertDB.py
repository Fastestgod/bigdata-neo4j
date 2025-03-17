import os
import pandas as pd
from Neo4jSetup import get_driver

driver = get_driver()
BATCH_SIZE = 10000

nodes_file = "data/nodes.tsv"  
edges_file = "data/edges.tsv"  

metaedge_to_relationship = {
    'CrC': 'Resembles',
    'CtD': 'Treats',
    'CpD': 'Palliates',
    'CbG': 'Binds',
    'CuG': 'Upregulates',
    'CdG': 'Downregulates',
    'DrD': 'Resembles',
    'DuG': 'Upregulates',
    'DdG': 'Downregulates',
    'DaG': 'Associates',
    'DlA': 'Localizes',
    'AuG': 'Upregulates',
    'AdG': 'Downregulates',
    'AeG': 'Expresses',
    'Gr>G': 'Regulates',
    'GcG': 'Covariates',
    'GiG': 'Interacts'
}

def insert_nodes():
    nodes_df = pd.read_csv(nodes_file, sep="\t", skiprows=1, header=None, names=["full_id", "name", "kind"])
    with driver.session() as session:
        # batch = []
        for _, row in nodes_df.iterrows():
            node_id = row["full_id"]
            name = row["name"]
            kind = row["kind"]

            # Validate and assign proper labels
            if kind == "Anatomy":
                label = "Anatomy"
            elif kind == "Disease":
                label = "Disease"
            elif kind == "Gene":
                label = "Gene"
            elif kind == "Compound":
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
    if not os.path.exists(edges_file):
        print(f"Error: File {edges_file} not found!")
        return

    edges_df = pd.read_csv(edges_file, sep="\t", skiprows=1, header=None, names=["full_source", "metaedge", "full_target"])
    with driver.session() as session:
        batch = []
        for _, row in edges_df.iterrows():
            # Extract source and target categories and IDs
            source_id = row["full_source"]
            target_id = row["full_target"]
            metaedge = row["metaedge"]

            # Determine the appropriate relationship type from metaedge
            if metaedge in metaedge_to_relationship:
                relation_type = metaedge_to_relationship[metaedge]
            else:
                raise Exception(f"Warning: Metaedge {metaedge} not recognized!")
            # Append the edge data to the batch
            batch.append({
                "source_id": source_id, 
                "target_id": target_id, 
                "relation_type": relation_type,
                "metaedge": metaedge
            })
            
            # Once batch size exceeds limit, insert the batch into Neo4j
            if len(batch) >= BATCH_SIZE:
                query = """
                UNWIND $batch AS edge
                MATCH (a {id: edge.source_id})
                MATCH (b {id: edge.target_id})
                CALL apoc.create.relationship(a, edge.relation_type, {metaedge: edge.metaedge}, b) YIELD rel
                RETURN rel
                """

                session.run(
                    query,
                    batch=batch
                )
                batch = []  # Clear batch after insertion

        # Insert any remaining edges if the batch is not empty
        if batch:  
            query = """
            UNWIND $batch AS edge
            MATCH (a {id: edge.source_id})
            MATCH (b {id: edge.target_id})
            CALL apoc.create.relationship(a, edge.relation_type, {metaedge: edge.metaedge}, b) YIELD rel
            RETURN rel
            """
            session.run(
                query,
                batch=batch
            )
    print("Edges inserted successfully.")
if __name__ == "__main__":
    # insert_nodes()
    # insert_edges()
    # print("Data insertion completed successfully!")
