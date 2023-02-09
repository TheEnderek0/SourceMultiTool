import tkinter as tk
from tkinter import ttk
import os
import json ##TEMP
from modules import (
    common_lib as cm,
    info, # Info tab
    config_tab, #Configuraton tab, important that it is here

    cc # Caption Compiler
    )


root = tk.Tk()
root.minsize(1280, 720)
cm.SetGlobal("root", root)


def main():
    DefineStyles()
    root.title("Source MultiTool")
    root.columnconfigure(index=0, weight=1)
    root.rowconfigure(index=0, weight=1)

    selector = ttk.Notebook(root)
    selector.grid(column=0, row=0, sticky="nsew")

    selector.columnconfigure(index=0, weight=1)
    selector.rowconfigure(index=0, weight=1)

    ### Initialise windows
    # These have to be first
    cm.Init(root)
    info.Init(selector)
    config_tab.Init(selector)

    cc.Init(selector)

    ### Load settings
    filew = open(f"{os.getcwd()}/set.json", "r")
    cm.SetGlobal("default_settings", json.load(filew)) #TEMP

    cm.LoadJson(f'{os.getcwd()}/settings.json')

    cm.SetGlobal("disable_save", False) # Create this global, so we can use it later on

    config_tab.Load(opening=True)

    
def DefineStyles():

    cm.SetGlobal("font", ("Arial", 12))

    style = ttk.Style(root)

    style.configure("BW.TLabel", foreground="black", background="#e6e6e6")
    style.configure("CFG.TEntry", foreground="black", background="#e6e6e6", font = ("Consolas", cm.GetGlobal("font")[1], 'normal'))
    style.configure("CFG.TButton", foreground="black", background="#e6e6e6")
    style.configure("OPTIONS.TCheckbutton", font=(cm.GetGlobal('font')[0], cm.GetGlobal('font')[1], 'bold'))
    style.configure("NL.TLabel", font=cm.GetGlobal('font')) #Normal label
    style.configure("Param.TLabel", font=cm.GetGlobal('font'), background="#e6e6e6") #Label used to display compile parameters
    style.configure("Param.TFrame", borderwidth=5, relief='groove')



main()

root.mainloop()