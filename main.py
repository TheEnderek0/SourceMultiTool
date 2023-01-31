import tkinter as tk
from tkinter import ttk

from modules import (
    info, # Info tab
    cc # Caption Compiler
    )



root = tk.Tk()
root.minsize(1280, 720)



def main():
    DefineStyles()
    root.title("Source MultiTool")
    root.columnconfigure(index=0, weight=1)
    root.rowconfigure(index=0, weight=1)

    selector = ttk.Notebook(root)
    selector.grid(column=0, row=0, sticky="nsew")

    selector.columnconfigure(index=0, weight=1)
    selector.rowconfigure(index=0, weight=1)

    info.Init(selector)
    cc.Init(selector)

def DefineStyles():
    style = ttk.Style()

    style.configure("BW.TLabel", foreground="black", background="#e6e6e6")



main()

root.mainloop()