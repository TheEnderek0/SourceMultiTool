import tkinter as tk
from tkinter import ttk
import os
import json ##TEMP
import ttkbootstrap as bs

from modules import (
    common_lib as cm,
    info, # Info tab
    config_tab, #Configuraton tab, important that it is here

    cc # Caption Compiler
    )


FONT = 'Verdana'
TITLE_FONT = 'Arial'
FONT_SIZE = 12


root = tk.Tk()
root.minsize(1280, 720)
cm.SetGlobal("root", root)

#root.tk.call("source", "./breeze/breeze.tcl")# Load the theme


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
    style = bs.Style(theme='darkly')

    # Everything #
    style.configure(".")

    style.configure("TNotebook", )

    # Labels #

    style.configure("TLabel", font = (FONT, FONT_SIZE, 'normal')) 
    style.configure("Error.TLabel", foreground = 'red', font = (FONT, FONT_SIZE, 'bold')) # label for displaying errors
    style.configure("ShortInfo.TLabel", font = (TITLE_FONT, FONT_SIZE, 'bold')) # Short info, like "Paths:", "Options:"
    style.configure("LongInfo.TLabel", font = (FONT, FONT_SIZE-2, 'normal')) # Long info, like the description of options and so on
    style.configure("Border.LongInfo.TLabel", borderwidth=3, relief='groove', background="#e6e6e6", foreground='black', font = (FONT, FONT_SIZE, 'normal'))
    style.configure("Small.LongInfo.TLabel", font = (FONT, FONT_SIZE - 4, 'normal')) # A variant of LongInfo.TLabel with much smaller font

    style.configure("Compile.TLabel") # Labels showing compile log output
    
    # Label frames #
    style.configure("Big.TLabelframe.Label")

    # Buttons #
    style.configure("Small.TButton", font = (TITLE_FONT, FONT_SIZE-2, 'bold')) # Used for small buttons
    style.configure("INFO.TButton") # Used for big info buttons, like the ones in the info tab

    # Check Buttons #
    style.configure("Option.info.TCheckbutton", font = (TITLE_FONT, FONT_SIZE, 'bold')) # Used for option checkbuttons, in specific tabs
    style.configure("Option.info.Outline.Toolbutton")

    # Frames #
    style.configure("Card.TFrame", padding=(10, 10, 10, 10))
    style.configure("Border.TFrame", borderwidth=5, relief='groove') # Normal bordered Tframe
    style.configure("GrayField.TFrame", background="#e6e6e6") # Used for gray-er fields
    style.configure("Border.GrayField.TFrame", borderwidth=5, relief='groove') # Gray field with frame

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
    cm.SetGlobal('Canvas_borderwidth', tk.IntVar(root, 0, "Canvas_borderwidth"))
    cm.SetGlobal('Canvas_relief', tk.StringVar(root, "sunken", "Canvas_relief"))

    # Spinbox #
    style.configure('Option.TSpinbox') # Spinboxes in option panels

    print("THEME NAMES " + str(style.theme_names()))


main()

root.mainloop()