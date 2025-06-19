#Author: WeegeeFR
#Date: 6/19/2025
#Description: Class handling tkinter GUI

from tkinter import *
from tkinter import ttk

class GUI:
    def __init__(self):
        self.gui = Tk()
        self.frm = ttk.Frame(self.gui, padding=10)
        self.frm.grid()
        ttk.Label(self.frm, text="Hello World!").grid(column=0, row=0)
        ttk.Button(self.frm, text="Quit", command=self.gui.destroy).grid(column=1, row=0)
    def start_gui(self):
        self.gui.mainloop()
