import tkinter as tk
import os
from tkinter import Listbox 
from tkinter import messagebox, scrolledtext
from projektstruktur import erstelle_struktur
from git_tools import initialisiere_git_und_push
from skript_tools import finde_scripts, run_python_script
from config import CONFIG
    

def erstelle_projekt():
    projekt = entry_name.get()
    nutzer = entry_user.get()
    privat = var_priv.get()
    if not projekt or not nutzer:
        messagebox.showwarning("Fehlende Angaben", "Bitte Projektname und GitHub-Nutzername eingeben.")
        return
    # Projekte immer im festen Zielordner anlegen
    basis_pfad = r"E:\dev\projekt_python_venv"
    pfad = os.path.join(basis_pfad, projekt)
    if os.path.exists(pfad):
        messagebox.showerror("Fehler", "Ordner existiert bereits.")
        return
    erstelle_struktur(projekt, nutzer, privat, basis_pfad)  # basis_pfad ggf. anpassen, siehe Hinweis unten
    initialisiere_git_und_push(projekt, nutzer, privat, basis_pfad)  # basis_pfad ggf. anpassen
    messagebox.showinfo("Fertig", f"Projekt '006_Umweltkontrollsystem' wurde erfolgreich erstellt!")

def on_run_script():
    global listbox, available_scripts, output
    selection = listbox.curselection()
    if not selection:
        messagebox.showinfo("Hinweis", "Bitte ein Skript auswählen.")
        return
    script_name = listbox.get(selection[0])
    script_path = available_scripts[script_name]
    stdout, stderr, error = run_python_script(script_path)

    output.delete(1.0, tk.END)
    if error:
        messagebox.showerror("Fehler", error)
    else:
        output.insert(tk.END, "Script Output:\n")
        output.insert(tk.END, stdout)
        if stderr:
            output.insert(tk.END, "\nScript Errors (if any):\n")
    
def main():
    global entry_name, entry_user, var_priv, listbox, available_scripts, output

    root = tk.Tk()
    root.title("Python-Projekt + GitHub Setup & Skriptstarter")

    # Projektgenerator-Bereich
    frame_proj = tk.LabelFrame(root, text="Neues Projekt erstellen")
    frame_proj.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    tk.Label(frame_proj, text="Projektname:").grid(row=0, column=0, sticky="e")
    entry_name = tk.Entry(frame_proj, width=30)
    entry_name.grid(row=0, column=1)

    tk.Label(frame_proj, text="GitHub Nutzername:").grid(row=1, column=0, sticky="e")
    entry_user = tk.Entry(frame_proj, width=30)
    entry_user.grid(row=1, column=1)
    entry_user.insert(0, "watchkido")  # <-- Hier Standardwert eintragen

    var_priv = tk.BooleanVar(value=True)      # <-- Standardmäßig aktiviert
    tk.Checkbutton(frame_proj, text="Privates Repository", variable=var_priv).grid(row=2, column=1, sticky="w")

    tk.Button(frame_proj, text="Projekt erstellen", command=erstelle_projekt).grid(row=3, column=0, columnspan=2, pady=10)

        # Skriptstarter-Bereich
    frame_scripts = tk.LabelFrame(root, text="Vorhandene Skripte starten")

    frame_scripts.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    
    tk.Label(frame_scripts, text="Gefundene Skripte:").pack(anchor="w")
    
    listbox = tk.Listbox(frame_scripts, width=60)
    listbox.pack(padx=5, pady=5)
    
    available_scripts = finde_scripts()
    for script_name in available_scripts:
        listbox.insert(tk.END, script_name)
    
    output = scrolledtext.ScrolledText(frame_scripts, width=80, height=10)
    output.pack(padx=5, pady=5)
    
    run_button = tk.Button(frame_scripts, text="Skript ausführen", command=on_run_script)
    run_button.pack(pady=5)
    
    root.mainloop()
    
if __name__ == "__main__":
        main()