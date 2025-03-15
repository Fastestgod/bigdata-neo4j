import os
import tkinter as tk
from tkinter import ttk, messagebox
from neo4j import GraphDatabase
from Neo4jSetup import get_driver
# Create a Neo4j driver instance
driver = get_driver()

def query_disease(disease_id):
    query = """
    MATCH (d:Disease {id: $disease_id})
    OPTIONAL MATCH (d)<-[:Treats|Palliates]-(drug:Compound)
    OPTIONAL MATCH (d)-[:Associates]->(gene:Gene)
    OPTIONAL MATCH (d)-[:Localizes]->(location:Anatomy)
    RETURN d.name AS disease_name, 
           COLLECT(DISTINCT drug.name) AS drugs, 
           COLLECT(DISTINCT gene.name) AS genes,
           COLLECT(DISTINCT location.name) AS locations
    """
    with get_driver().session() as session:
        result = session.run(query, disease_id=disease_id).single()
        if result:
            return {
                "Disease Name": result["disease_name"],
                "Drugs": ", ".join(result["drugs"]),
                "Genes": ", ".join(result["genes"]),
                "Locations": ", ".join(result["locations"]),
            }
        return None

# GUI Function
def search():
    disease_id = "Disease::DOID:" + str(entry.get())
    if not disease_id:
        messagebox.showwarning("Input Error", "Please enter a Disease ID.")
        return

    result = query_disease(disease_id)
    if result:
        output_text.set(
            f"Disease Name: {result['Disease Name']}\n"
            f"Drugs: {result['Drugs']}\n"
            f"Genes: {result['Genes']}\n"
            f"Locations: {result['Locations']}"
        )
    else:
        output_text.set("No data found.")

# GUI Setup
root = tk.Tk()
root.title("Disease Query")

tk.Label(root, text="Enter Disease ID:").pack()
entry = tk.Entry(root)
entry.pack()

tk.Button(root, text="Search", command=search).pack()
output_text = tk.StringVar()
tk.Label(root, textvariable=output_text, wraplength=400, justify="left").pack()

root.mainloop()