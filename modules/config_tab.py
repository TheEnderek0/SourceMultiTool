import tkinter as tk
from tkinter import ttk
from . import common_lib as cm

PATH_INFO_TEXT = "Here you can setup paths to executables and other crucial files.\n If you are using a default mod structure, setting the gameinfo.txt should also setup all of the other paths."
DFONT = ("Arial", 12)
COLUMNS = ("1", "2", "3")

def Init(container):
    print("Initialising Configuration tab")

    frame = ttk.Frame(container)
    frame.grid(column=0, row=0, sticky="nsew")
    container.add(frame, text = 'Configuration')

    frame.rowconfigure(index=0, weight=1)
    frame.columnconfigure(index=0, weight=1)
    frame.columnconfigure(index=1, weight=2)

    PathSelect(frame)

def PathSelect(container):
    mainFrame = ttk.Frame(container, borderwidth=5, relief='groove')
    mainFrame.grid(column=0, row=0, sticky='nsew')

    mainFrame.columnconfigure(index=0, weight=1)
    mainFrame.rowconfigure(index=0, weight=0)
    mainFrame.rowconfigure(index=1, weight=0)
    mainFrame.rowconfigure(index=2, weight=2)

    label = ttk.Label(mainFrame, 
        text=PATH_INFO_TEXT,
        wraplength=1200,
        font = DFONT,
        justify='left',
        anchor='w',
        )
    label.bind('<Configure>', lambda e: cm.ResizeWrapLength(label, mainFrame.winfo_width(), max=400, min=120, multiplier=0.7, endmultiplier=2))
    label.grid(column=0, row=0, sticky='nsew')
    
    scrollFrame = ttk.Frame(mainFrame)
    scrollFrame.grid(column=0, row=2, sticky='nsew')

    scrollFrame.columnconfigure(index=0, weight=1)
    scrollFrame.columnconfigure(index=1, weight=0)
    scrollFrame.rowconfigure(index=0, weight=1)

    scrollbar = ttk.Scrollbar(scrollFrame, orient='vertical')
    scrollbar.grid(column=1, row=0, sticky='ns')

    tree = ttk.Treeview(scrollFrame, yscrollcommand=scrollbar.set, columns=COLUMNS, show='')
    tree.grid(column=0, row=0, sticky='nsew')
    scrollbar.configure( command=tree.yview )

