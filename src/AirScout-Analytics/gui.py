# gui builder: python gui builder.com
# visualtk.com
#
#
#



import tkinter as tk
import os
from tkinter import messagebox, scrolledtext
from funktionen import projekt_anlegen, skript_ausführen, projekt_analyse_starten, finde_alle_scripts


def erstelle_projekt():
    projekt = entry_name.get()
    nutzer = entry_user.get()
    privat = var_priv.get()
    if not projekt or not nutzer:
        messagebox.showwarning("Fehlende Angaben", "Bitte Projektname und GitHub-Nutzername eingeben.")
        return
    basis_pfad = r"E:\dev\projekt_python_venv"
    status = projekt_anlegen(projekt, nutzer, privat, basis_pfad)
    if "erfolgreich" in status:
        messagebox.showinfo("Fertig", status)
    else:
        messagebox.showerror("Fehler", status)

def on_run_script() -> None:
    auswahl = listbox.curselection()
    if not auswahl:
        messagebox.showinfo("Hinweis", "Bitte ein Skript auswählen.")
        return
    skript_name = listbox.get(auswahl[0])
    skript_pfad = available_scripts.get(skript_name)
    if not skript_pfad:
        messagebox.showerror("Fehler", f"Skript '{skript_name}' nicht gefunden.")
        return
    stdout, stderr, fehler = skript_ausführen(skript_pfad)
    output.delete(1.0, tk.END)
    if fehler:
        messagebox.showerror("Fehler", str(fehler))
    else:
        output.insert(tk.END, "Script Output:\n")
        output.insert(tk.END, str(stdout) if stdout is not None else "")
        if stderr:
            output.insert(tk.END, "\nScript Errors (if any):\n")
            output.insert(tk.END, str(stderr))

def run_projekt_analyse():
    projekt_analyse_starten()

def start_gui():
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
    entry_user.insert(0, "watchkido")

    var_priv = tk.BooleanVar(value=True)
    tk.Checkbutton(frame_proj, text="Privates Repository", variable=var_priv).grid(row=2, column=1, sticky="w")

    tk.Button(frame_proj, text="Projekt erstellen", command=erstelle_projekt).grid(row=3, column=0, columnspan=2, pady=10)

    # Skriptstarter-Bereich
    frame_scripts = tk.LabelFrame(root, text="Vorhandene Skripte starten")
    frame_scripts.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    tk.Label(frame_scripts, text="Gefundene Skripte:").pack(anchor="w")

    analyse_button = tk.Button(frame_scripts, text="Projekt-Analyse starten", command=run_projekt_analyse)
    analyse_button.pack(pady=5)

    listbox = tk.Listbox(frame_scripts, width=60)
    listbox.pack(padx=5, pady=5)

    available_scripts = finde_alle_scripts()
    for script_name in available_scripts:
        listbox.insert(tk.END, script_name)

    output = scrolledtext.ScrolledText(frame_scripts, width=80, height=10)
    output.pack(padx=5, pady=5)

    run_button = tk.Button(frame_scripts, text="Skript ausführen", command=on_run_script)
    run_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    start_gui()


# This code is a simple GUI application using Tkinter to create a project setup tool.