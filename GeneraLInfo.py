import tkinter as tk
from tkinter import ttk, messagebox
from Neo4jSetup import get_driver
import argparse
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
            print(
                {f"Disease Name": result["disease_name"],
                "Drugs": ", ".join(result["drugs"]),
                "Genes": ", ".join(result["genes"]),
                "Locations": ", ".join(result["locations"]),
                })
            return {
                "Disease Name": result["disease_name"],
                "Drugs": ", ".join(result["drugs"]),
                "Genes": ", ".join(result["genes"]),
                "Locations": ", ".join(result["locations"]),
            }
            
        print("nothing")
        return None
#query 2
def run_query():
    query = f"""
    MATCH (c:Compound)-[r:Upregulates]->(g:Gene),
    (d:Disease)-[r3:Localizes]->(a:Anatomy),
          (a:Anatomy)-[r2:Downregulates]->(g:Gene)
    WHERE NOT (c)-[:Treats|Palliates]->(:Disease)
    RETURN c.name
    UNION DISTINCT
    MATCH (c:Compound)-[r:Downregulates]->(g:Gene),
    (d:Disease)-[r3:Localizes]->(a:Anatomy),
        (a:Anatomy)-[r2:Upregulates]->(g:Gene)
    WHERE NOT (c)-[:Treats|Palliates]->(:Disease)
    RETURN c.name
    """
    
    with driver.session() as session:
        results = session.run(query)
        
        compound_names = []
        for record in results:
            compound_name = record["c.name"]
            compound_names.append(compound_name)
        print("\n".join(compound_names) if compound_names else "No new drugs found.")
        return "\n".join(compound_names) if compound_names else "No new drugs found."
# GUI Function
def search():
    disease_id = "Disease::DOID:" + str(entry.get())
    if not disease_id:
        messagebox.showwarning("Input Error", "Please enter a Disease ID.")
        return

    result = query_disease(disease_id)
    
    # Clear the existing content in the Text widget
    output_text.delete(1.0, tk.END)

    if result:
        # Insert the result into the Text widget
        output_text.insert(tk.END, 
            f"Disease Name: {result['Disease Name']}\n"
            f"Drugs: {result['Drugs']}\n"
            f"Genes: {result['Genes']}\n"
            f"Locations: {result['Locations']}"
        )
    else:
        output_text.insert(tk.END, "No data found.")

def new_drugs():
    result = run_query()
    
    # Update the output text label with the results
    output_text.delete(1.0, tk.END)  # Clear the existing content in the Text widget
    all_new_drugs=(f"New drugs for diseases:\n\n{result}")
    output_text.insert(tk.END, all_new_drugs)  # Insert the new drugs into the Text widget
    

# GUI Setup
root = tk.Tk()
root.title("Disease Query")

# Disease ID input
tk.Label(root, text="Enter Disease ID:").pack()
entry = tk.Entry(root)
entry.pack()

# Search button
tk.Button(root, text="Search", command=search).pack()

# New Drugs button
tk.Button(root, text="Find New Drugs", command=new_drugs).pack()

# Frame for the scrollable text area
output_frame = tk.Frame(root)
output_frame.pack(padx=10, pady=10)

# Create a canvas and a scrollbar
canvas = tk.Canvas(output_frame)
scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas to hold the output text
output_container = tk.Frame(canvas)

# Add the frame to the canvas
canvas.create_window((0, 0), window=output_container, anchor="nw")

canvas.pack(side="left", fill="both", expand=True)

# Create a Text widget for displaying the output
output_text = tk.Text(output_container, wrap="word", height=10, width=50)
output_text.pack()

# Update the scroll region when the output text changes


root.mainloop()

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run Neo4j Queries")
parser.add_argument("-q1", action="store_true", help="Run Query 1 (requires -id)")
parser.add_argument("-q2", action="store_true", help="Run Query 2")
parser.add_argument("-id", type=str, help="Disease ID for Query 1")

args = parser.parse_args()

# Execute the selected query
if args.q1 and args.id:
    query_disease(args.id)
elif args.q2:
    run_query()
else:
    print("Usage: script.py -q1 -id <disease_id> OR script.py -q2")