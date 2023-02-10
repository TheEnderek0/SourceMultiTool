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


FONT = 'Verdana'
FONT_SIZE = 13


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
    style = ttk.Style(root)

    # Everything #
    style.configure(".")

    # Labels #
    style.configure("TLabel") 
    style.configure("Error.TLabel") # label for displaying errors
    style.configure("ShortInfo.TLabel") # Short info, like "Paths:", "Options:"
    style.configure("LongInfo.TLabel") # Long info, like the description of options and so on
    style.configure("Small.LongInfo.TLabel") # A variant of LongInfo.TLabel with much smaller font

    # Buttons #
    style.configure("Small.TButton") # Used for small buttons
    style.configure("INFO.TButton") # Used for big info buttons, like the ones in the info tab

    # Check Buttons #
    style.configure("OptionCheck.TCheckbutton") # Used for option checkbuttons, in specific tabs

    # Frames #
    style.configure("Border.TFrame", borderwidth=5, relief='groove') # Normal bordered Tframe
    style.configure("GrayField.TFrame") # Used for gray-er fields
    style.configure("Border.GrayField.TFrame") # Gray field with frame

    # Dropdowns #
    style.configure("CFG.TCombobox") # Only used for the config selection box in the Configuration tab
    style.configure("IO.TCombobox") # Used for the Input/Output comboboxes in tabs

    # Entries #
    style.configure("Path.TEntry") # Entries for paths and files
    style.configure("Other.TEntry") # Other TEntries
    cm.SetGlobal('TEntry_font_size', tk.IntVar(root, FONT_SIZE, "TEntry_font_size"))
    cm.SetGlobal('TEntry_font', tk.StringVar(root, 'Consolas', "TEntry_font"))
    cm.SetGlobal('TEntry_font_style', tk.StringVar(root, 'normal', "TEntry_font_style"))

    # Scrollbars #
    style.configure('Scrollbar')

    # Canvas #
    #We have to do this by tkvars since canvases are widgets of only tk, not ttk
    cm.SetGlobal('Canvas_borderwidth', tk.IntVar(root, 5, "Canvas_borderwidth"))
    cm.SetGlobal('Canvas_relief', tk.StringVar(root, "sunken", "Canvas_relief"))

    # Spinbox #
    style.configure('Option.TSpinbox') # Spinboxes in option panels

    #style.configure("BW.TLabel", foreground="black", background="#e6e6e6")
    ##style.configure("CFG.TEntry", foreground="black", background="#e6e6e6", font = ("Consolas", cm.GetGlobal("font")[1], 'normal'))
    #style.configure("CFG.TButton", foreground="black", background="#e6e6e6")
    #style.configure("OPTIONS.TCheckbutton", font=(cm.GetGlobal('font')[0], cm.GetGlobal('font')[1], 'bold'))
    #style.configure("NL.TLabel", font=cm.GetGlobal('font')) #Normal label
    #style.configure("Param.TLabel", font=(cm.GetGlobal('font')[0], cm.GetGlobal('font')[1] - 3), background="#e6e6e6") #Label used to display compile parameters
    #style.configure("Param.TFrame", borderwidth=5, relief='groove')
    #style.configure("TEntry", font=('Helvetica', 16))



main()

root.mainloop()