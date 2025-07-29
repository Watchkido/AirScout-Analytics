try:
    from tkinterweb import HtmlFrame
    HTML_SUPPORT = True
except ImportError:
    HTML_SUPPORT = False
import tkinter as tk
from tkinter import ttk
import os
import glob
from PIL import Image, ImageTk
try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
from context import filename_ohne_ext
# --- Tab-Konfigurationen ---
# Für jeden Haupttab 20 individuelle Variablen für Name, Beschriftung, Datei


# Tab 1
TAB1_TAB_NAMES = [f"DA_{i+1}" for i in range(30)]
TAB1_LABELS = [f"Tab 1 - Ansicht {i+1}" for i in range(30)]
TAB1_FILES = [
    os.path.join("..", "..", "data", "bearbeitet", "*.csv"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_info.txt"),
    os.path.join("..", "..", "data", "bearbeitet0", "*.csv"),
    os.path.join("..", "..", "data", "bearbeitet1", "*.csv"),
    os.path.join("..", "..", "data", "bearbeitet2", "*.csv"), 
    os.path.join("..", "..", "data", "bearbeitet3", "*.csv"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"korrelationsmatrix_{filename_ohne_ext}.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_bild1.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_Humidity_RH.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ2.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ3.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ4.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ5.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ6.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ7.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ8.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ9.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_MQ135.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_Radiation_CPS.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_Temperature_DHT_C.png"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", "umweltbericht.txt"),
    os.path.join("..", "..", "data", "ergebnisse", f"{filename_ohne_ext}", f"{filename_ohne_ext}_Mic2.png"),
    # os.path.join("..", "..", "data", "bearbeitet1", "*.txt"),  # Beispiel für weitere Dateien
]
TAB1_FILES += [os.path.join("..", "..", "data", "bearbeitet", f"Infos{i+1}.txt") for i in range(3, 20)]

# Tab 2
TAB2_TAB_NAMES = [f"Tab2_{i+1}" for i in range(20)]
TAB2_LABELS = [f"Tab 2 - Ansicht {i+1}" for i in range(20)]
TAB2_FILES = [os.path.join("..", "..", "data", "bearbeitet", f"Infos{i+1}.txt") for i in range(20)]

# Tab 3
TAB3_TAB_NAMES = [f"Tab3_{i+1}" for i in range(20)]
TAB3_LABELS = [f"Tab 3 - Ansicht {i+1}" for i in range(20)]
TAB3_FILES = [os.path.join("..", "..", "data", "bearbeitet", f"Infos{i+1}.txt") for i in range(20)]


def show_txt_in_tab(frame, filepath):
    for widget in frame.winfo_children():
        widget.destroy()
    # Relativen Pfad in absoluten Pfad umwandeln (relativ zum Skriptverzeichnis)
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), filepath))
    # Wildcard-Unterstützung: bei *.csv oder *.txt erste passende Datei nehmen
    if '*' in abs_path or '?' in abs_path:
        matches = glob.glob(abs_path)
        if matches:
            abs_path = matches[0]
        else:
            content = f"Keine Datei gefunden für Muster: {abs_path}"
            text_frame = tk.Frame(frame)
            text_frame.pack(expand=True, fill=tk.BOTH)
            text = tk.Text(text_frame, height=30, width=120, wrap=tk.NONE)
            y_scroll = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
            x_scroll = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text.xview)
            text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
            text.insert(tk.END, content)
            text.grid(row=0, column=0, sticky="nsew")
            y_scroll.grid(row=0, column=1, sticky="ns")
            x_scroll.grid(row=1, column=0, sticky="ew")
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)
            return
    # Bildformate, die unterstützt werden
    image_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    pdf_exts = ('.pdf',)
    html_exts = ('.html', '.htm')
    MAX_IMAGE_SIZE = (1920, 1080)  # Größere Darstellung für Bilder
    if abs_path.lower().endswith(html_exts) and HTML_SUPPORT:
        try:
            html_frame = HtmlFrame(frame, horizontal_scrollbar=True)
            html_frame.load_file(abs_path)
            html_frame.pack(expand=True, fill=tk.BOTH)
        except Exception as e:
            content = f"Fehler beim Anzeigen der HTML-Datei: {e}\nPfad: {abs_path}"
            text_frame = tk.Frame(frame)
            text_frame.pack(expand=True, fill=tk.BOTH)
            text = tk.Text(text_frame, height=30, width=120, wrap=tk.NONE)
            y_scroll = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
            x_scroll = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text.xview)
            text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
            text.insert(tk.END, content)
            text.grid(row=0, column=0, sticky="nsew")
            y_scroll.grid(row=0, column=1, sticky="ns")
            x_scroll.grid(row=1, column=0, sticky="ew")
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)
    elif abs_path.lower().endswith(image_exts):
        try:
            img = Image.open(abs_path)
            # Bild wird nicht verkleinert, sondern in voller Größe geladen
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=photo)
            label.image = photo  # Referenz halten!
            label.pack(expand=True, fill=tk.BOTH)
        except Exception as e:
            content = f"Fehler beim Laden des Bildes: {e}\nPfad: {abs_path}"
            text = tk.Text(frame, height=30, width=120)
            text.insert(tk.END, content)
            text.pack(expand=True, fill=tk.BOTH)
    elif abs_path.lower().endswith(pdf_exts):
        if PDF_SUPPORT:
            try:
                images = convert_from_path(abs_path, first_page=1, last_page=1, fmt='png')
                if images:
                    img = images[0]
                    img.thumbnail((1200, 700))
                    photo = ImageTk.PhotoImage(img)
                    label = tk.Label(frame, image=photo)
                    label.image = photo
                    label.pack(expand=True, fill=tk.BOTH)
                else:
                    raise Exception("Keine Seite im PDF gefunden")
            except Exception as e:
                content = f"Fehler beim Anzeigen der PDF-Datei: {e}\nPfad: {abs_path}"
                text = tk.Text(frame, height=30, width=120)
                text.insert(tk.END, content)
                text.pack(expand=True, fill=tk.BOTH)
        else:
            content = ("PDF-Anzeige benötigt das Paket 'pdf2image' und ein installiertes Poppler.\n"
                       f"Dateipfad: {abs_path}")
            text = tk.Text(frame, height=30, width=120)
            text.insert(tk.END, content)
            text.pack(expand=True, fill=tk.BOTH)
    else:
        try:
            with open(abs_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Fehler beim Laden der Datei: {e}\nPfad: {abs_path}"
        text_frame = tk.Frame(frame)
        text_frame.pack(expand=True, fill=tk.BOTH)
        text = tk.Text(text_frame, height=30, width=120, wrap=tk.NONE)
        y_scroll = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
        x_scroll = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text.xview)
        text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        text.insert(tk.END, content)
        text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)


class MultiTabGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("3x20 Tab-Viewer für TXT-Dateien")
        self.geometry("1600x900")
        # Frame für Button oben rechts
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, anchor="ne", fill=tk.X)
        beenden_button = tk.Button(button_frame, text="Beenden", command=self.beenden, bg="#d9534f", fg="white", font=("Arial", 12, "bold"))
        beenden_button.pack(side=tk.RIGHT, padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_tabs()

    def on_close(self):
        """
        Fragt beim Schließen des Fensters nach, ob wirklich beendet werden soll.
        """
        import tkinter.messagebox as mbox
        if mbox.askokcancel("Beenden", "Möchten Sie die Anwendung wirklich beenden?"):
            self.quit()

    def beenden(self):
        """
        Beendet die GUI-Anwendung sauber.
        :returns: None
        """
        # TODO: Hier könnten noch Aufräumarbeiten ergänzt werden
        self.quit()

    def create_tabs(self):
        main_notebook = ttk.Notebook(self)
        main_notebook.pack(fill=tk.BOTH, expand=True)

        # Haupttab 1
        tab1 = ttk.Notebook(main_notebook)
        main_notebook.add(tab1, text="Datenanalyse")
        for i in range(20):
            frame = ttk.Frame(tab1)
            tab1.add(frame, text=TAB1_TAB_NAMES[i])
            label = tk.Label(frame, text=TAB1_LABELS[i], font=("Arial", 12, "bold"))
            label.pack(pady=5)
            show_txt_in_tab(frame, TAB1_FILES[i])

        # Haupttab 2
        tab2 = ttk.Notebook(main_notebook)
        main_notebook.add(tab2, text="Präsentation")
        for i in range(20):
            frame = ttk.Frame(tab2)
            tab2.add(frame, text=TAB2_TAB_NAMES[i])
            label = tk.Label(frame, text=TAB2_LABELS[i], font=("Arial", 12, "bold"))
            label.pack(pady=5)
            show_txt_in_tab(frame, TAB2_FILES[i])

        # Haupttab 3
        tab3 = ttk.Notebook(main_notebook)
        main_notebook.add(tab3, text="Zusammenfassung")
        for i in range(20):
            frame = ttk.Frame(tab3)
            tab3.add(frame, text=TAB3_TAB_NAMES[i])
            label = tk.Label(frame, text=TAB3_LABELS[i], font=("Arial", 12, "bold"))
            label.pack(pady=5)
            show_txt_in_tab(frame, TAB3_FILES[i])


def main() -> None:
    """
    Pipeline-kompatibler Einstiegspunkt: Startet die MultiTab-GUI.
    """
    app = MultiTabGUI()
    app.mainloop()


if __name__ == "__main__":
    main()