# gui builder: python gui builder.com
# visualtk.com
#
#
#


from config import CONFIG
import tkinter as tk
# gui/dashboard_gui.py

import tkinter as tk
from PIL import ImageTk, Image
import os

def zeige_dashboard():
    fenster = tk.Tk()
    fenster.title("Umwelt-Dashboard")

    # Textausgabe
    if os.path.exists("plots/temperaturverlauf.png"):
        img1 = Image.open("plots/temperaturverlauf.png")
        img1 = img1.resize((400, 300))
        tk_img1 = ImageTk.PhotoImage(img1)
        label1 = tk.Label(fenster, image=tk_img1)
        label1.image = tk_img1
        label1.pack()

    if os.path.exists("plots/co_verlauf.png"):
        img2 = Image.open("plots/co_verlauf.png")
        img2 = img2.resize((400, 300))
        tk_img2 = ImageTk.PhotoImage(img2)
        label2 = tk.Label(fenster, image=tk_img2)
        label2.image = tk_img2
        label2.pack()

    fenster.mainloop()
