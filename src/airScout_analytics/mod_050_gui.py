import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DatenGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Daten-Coach GUI")
        self.geometry("1400x800")
        self.df = None

        self.create_sidebar()
        self.create_notebooks()

    def create_sidebar(self):
        sidebar = tk.Frame(self, width=250, bg="#f0f0f0")
        sidebar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(sidebar, text="☕ Kaffee gefällig?", font=("Arial", 12)).pack(pady=10)
        tk.Button(
            sidebar,
            text="Kaffee ausgeben",
            command=lambda: messagebox.showinfo("Kaffee", "Kaffee kommt sofort!")
        ).pack(pady=5)

        tk.Label(sidebar, text="📚 Buchwerbung", font=("Arial", 12, "bold")).pack(pady=20)
        for i in range(1, 6):
            tk.Button(
                sidebar,
                text=f"Buch {i}",
                command=lambda i=i: self.buchwerbung(i)
            ).pack(pady=2)

    def buchwerbung(self, nummer):
        messagebox.showinfo("Buchwerbung", f"Buch {nummer}: Bald im Handel!")

    def create_notebooks(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        daten_tabs = ttk.Notebook(notebook)
        praes_tabs = ttk.Notebook(notebook)

        notebook.add(daten_tabs, text="📊 Datenbearbeitung")
        notebook.add(praes_tabs, text="🖥 Präsentation")

        daten_funcs = [
            self.tab_csv_laden,
            self.tab_nullwerte,
            self.tab_grundinfo,
            self.tab_korrelation,
            self.tab_statistik,
            self.tab_filter,
            self.tab_sortieren,
            self.tab_speichern
        ]

        praes_funcs = [
            self.tab_histogramm,
            self.tab_korrelation_praes,
            self.tab_liniendiagramm,
            self.tab_boxplot,
            self.tab_balken,
            self.tab_pie,
            self.tab_scatter,
            self.tab_datenblick
        ]

        for i, func in enumerate(daten_funcs):
            frame = ttk.Frame(daten_tabs)
            daten_tabs.add(frame, text=f"Schritt {i+1}")
            func(frame)

        for i, func in enumerate(praes_funcs):
            frame = ttk.Frame(praes_tabs)
            praes_tabs.add(frame, text=f"Visual {i+1}")
            func(frame)

    def tab_csv_laden(self, frame):
        btn = tk.Button(frame, text="CSV Datei laden", command=self.load_csv)
        btn.pack(pady=20)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Dateien", "*.csv")])
        if path:
            self.df = pd.read_csv(path)
            messagebox.showinfo("Erfolg", f"{path} erfolgreich geladen")

    def tab_nullwerte(self, frame):
        btn = tk.Button(
            frame,
            text="Nullwerte anzeigen",
            command=lambda: self.show_text(frame, self.df.isnull().sum() if self.df is not None else "Keine Daten")
        )
        btn.pack(pady=10)

    def tab_grundinfo(self, frame):
        btn = tk.Button(
            frame,
            text="Grundinfos anzeigen",
            command=lambda: self.show_text(frame, self.df.info(buf=None) if self.df is not None else "Keine Daten")
        )
        btn.pack(pady=10)

    def tab_korrelation(self, frame):
        btn = tk.Button(
            frame,
            text="Korrelation berechnen",
            command=lambda: self.show_text(frame, self.df.corr(numeric_only=True) if self.df is not None else "Keine Daten")
        )
        btn.pack(pady=10)

    def tab_statistik(self, frame):
        btn = tk.Button(
            frame,
            text="Deskriptive Statistik",
            command=lambda: self.show_text(frame, self.df.describe() if self.df is not None else "Keine Daten")
        )
        btn.pack(pady=10)

    def tab_filter(self, frame):
        tk.Label(frame, text="Filter nach Spalte und Wert folgt...").pack()

    def tab_sortieren(self, frame):
        tk.Label(frame, text="Sortierfunktion folgt...").pack()

    def tab_speichern(self, frame):
        btn = tk.Button(
            frame,
            text="Daten als CSV speichern",
            command=self.save_csv
        )
        btn.pack(pady=10)

    def save_csv(self):
        if self.df is not None:
            path = filedialog.asksaveasfilename(defaultextension=".csv")
            if path:
                self.df.to_csv(path, index=False)
                messagebox.showinfo("Gespeichert", f"Datei gespeichert unter: {path}")

    def tab_histogramm(self, frame):
        self.plot_diagram(frame, kind="hist")

    def tab_korrelation_praes(self, frame):
        self.plot_diagram(frame, kind="heatmap")

    def tab_liniendiagramm(self, frame):
        self.plot_diagram(frame, kind="line")

    def tab_boxplot(self, frame):
        self.plot_diagram(frame, kind="box")

    def tab_balken(self, frame):
        self.plot_diagram(frame, kind="bar")

    def tab_pie(self, frame):
        self.plot_diagram(frame, kind="pie")

    def tab_scatter(self, frame):
        self.plot_diagram(frame, kind="scatter")

    def tab_datenblick(self, frame):
        self.show_text(frame, self.df.head() if self.df is not None else "Keine Daten")

    def show_text(self, frame, content):
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Text):
                widget.destroy()
        output = tk.Text(frame, height=25, width=120)
        output.insert(tk.END, str(content))
        output.pack()

    def plot_diagram(self, frame, kind="hist"):
        for widget in frame.winfo_children():
            widget.destroy()

        if self.df is None:
            tk.Label(frame, text="Keine Daten geladen.").pack()
            return

        fig, ax = plt.subplots(figsize=(6, 4))
        try:
            if kind == "hist":
                self.df.select_dtypes("number").hist(ax=ax)
            elif kind == "heatmap":
                pd.plotting.scatter_matrix(self.df.select_dtypes("number"), ax=ax)
            elif kind == "line":
                self.df.plot(ax=ax)
            elif kind == "box":
                self.df.plot(kind="box", ax=ax)
            elif kind == "bar":
                self.df.select_dtypes("number").mean().plot(kind="bar", ax=ax)
            elif kind == "pie":
                self.df.select_dtypes("number").mean().plot(kind="pie", ax=ax, ylabel="")
            elif kind == "scatter":
                num_cols = self.df.select_dtypes("number").columns
                if len(num_cols) >= 2:
                    self.df.plot(kind="scatter", x=num_cols[0], y=num_cols[1], ax=ax)
        except Exception as e:
            tk.Label(frame, text=f"Fehler beim Plotten: {e}").pack()
            return

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()


if __name__ == "__main__":
    app = DatenGUI()
    app.mainloop()
