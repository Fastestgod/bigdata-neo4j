import tkinter as tk
from tkinter import ttk, messagebox
from Neo4jSetup import get_driver
from GeneraLInfo import query_disease,run_query


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
tk.Label(root, text="Enter Disease ID:").pack()
entry = tk.Entry(root)
entry.pack()
tk.Button(root, text="Search", command=search).pack()
tk.Button(root, text="Find New Drugs", command=new_drugs).pack()
output_frame = tk.Frame(root)
output_frame.pack(padx=10, pady=10)
canvas = tk.Canvas(output_frame)
scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
output_container = tk.Frame(canvas)
canvas.create_window((0, 0), window=output_container, anchor="nw")
canvas.pack(side="left", fill="both", expand=True)
output_text = tk.Text(output_container, wrap="word", height=10, width=50)
output_text.pack()
root.mainloop()