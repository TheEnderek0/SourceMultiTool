import tkinter as tk
from tkinter import ttk
from . import common_lib as cm
import os

PATH_INFO_TEXT = "Path setup:"
DFONT = ("Arial", 12)

saveDictionary = {}

configs = []

def Init(container):
    print("Initialising Configuration tab")

    frame = ttk.Frame(container)                    # ---|
    frame.grid(column=0, row=0, sticky="nsew")      #    | Initialise the main frame for notebook
    container.add(frame, text = 'Configuration')    # ---|

    frame.rowconfigure(index=0, weight=0)           #  
    frame.rowconfigure(index=1, weight=1)           #  Configure the rows for the frame
    frame.columnconfigure(index=0, weight=1)        #
    frame.columnconfigure(index=1, weight=2)        #

    SaveSelector(frame)
    PathSelect(frame)

def SaveSelector(cont):

    sFrame = ttk.Frame(cont, borderwidth=5, relief='groove')                                                       #   Configure the frame for the selector widget, and selector buttons
    sFrame.grid(column=0, columnspan=2, row=0, sticky='new')                           #

    sFrame.columnconfigure(index = 0, weight = 5)                                       #
    sFrame.columnconfigure(index = 1, weight = 1)                                       #   Configure the grid for the sFrame
    sFrame.columnconfigure(index = 2, weight = 1)                                       #
    sFrame.rowconfigure(index = 0, weight = 0)                                          #

    #################
    # Selector
    selector = ttk.Combobox(sFrame, state='read-only', values=[])                    #   Make the combobox widget, the selector
    selector.grid(column = 0, row = 0, sticky='ew', padx=10, pady=20)                                     #

    selector.bind("<<ComboboxSelected>> ", lambda e: LoadFor(selector.get()))           #   Bind the LoadFor function to the widget, every time user changes the selection load the data for that selection.

    cm.SetGlobal("ConfigDropdown", selector)                                            #   Set the selector as a global value

    # Add, Delete buttons
    addButton = ttk.Button(sFrame,
        text="Add new configuration",
        style = 'CFG.TButton',
    )

    deleteButton = ttk.Button(sFrame,
        text = "Delete configuration",
        style = "CFG.TButton",
    )

    addButton.grid(column=1, row=0, sticky='ew', padx=10, pady=20)
    deleteButton.grid(column=2, row=0, sticky='ew', padx=10, pady=20)



def PathSelect(container):
    #   Make the frame for the scrolling widget to be in, and configure the grid
    mainFrame = ttk.Frame(container)
    mainFrame.grid(column=0, row=1, sticky='nsew')

    mainFrame.columnconfigure(index=0, weight=1)
    mainFrame.rowconfigure(index=0, weight=0)
    mainFrame.rowconfigure(index=1, weight=0)
    mainFrame.rowconfigure(index=2, weight=2)
    #   Create a simple label to show what this gui is for
    label = ttk.Label(mainFrame,              
        text=PATH_INFO_TEXT,                  
        wraplength=1200,                      
        font = (DFONT[0], DFONT[1], "bold"),  
        justify='center',                     
        anchor='c',                           
        )                                     
    label.grid(column=0, row=0, sticky='nsew', pady=10)


    #   Create a frame for the scrolling canvas
    scrollFrame = ttk.Frame(mainFrame)
    scrollFrame.grid(column=0, row=2, sticky='nsew')

    scrollFrame.columnconfigure(index=0, weight=1)
    scrollFrame.columnconfigure(index=1, weight=0)
    scrollFrame.rowconfigure(index=0, weight=1)

    # Create the scrollbar
    scrollbar = ttk.Scrollbar(scrollFrame, orient='vertical')
    scrollbar.grid(column=1, row=0, sticky='ns')

    # Create the canvas
    canvas = tk.Canvas(scrollFrame, yscrollcommand=scrollbar.set, borderwidth=1, relief='sunken')
    canvas.grid(column=0, row=0, sticky='nsew')
    scrollbar.configure( command=canvas.yview ) # Bind the scrollbar to the canvas

    # Make another frame in the canvas itself
    canvasFrame = ttk.Frame(canvas)
    canvasFrame.pack(fill = 'both', expand = True, padx=20, pady=20)

    canvasFrame.columnconfigure(index=0, weight=0)
    canvasFrame.columnconfigure(index=1, weight=3)
    canvasFrame.columnconfigure(index=2, weight=0)
    canvasFrame.columnconfigure(index=3, weight=0)
    canvasFrame.rowconfigure(index=0, weight=0)
    canvasFrame.rowconfigure(index=1, weight=0)
    canvasFrame.rowconfigure(index=2, weight=0)

    #
    # Frame specifig config, the Name entry widget, and the GameInfo entry
    #

    nameLabel = ttk.Label(canvasFrame,
        text = "Name",
        font = DFONT,
        justify="center",
        anchor='c',
        padding = (20, 0, 10, 0)
    )
    nameLabel.grid(column=0, row=0, sticky='ew')


    nameString = tk.StringVar(canvasFrame) #Make a string var for further tracing

    nameBox = ttk.Entry(canvasFrame,
        style = "CFG.TEntry",
        font = ("Consolas", DFONT[1], 'normal'),
        textvariable=nameString
    )
    nameBox.grid(column=1, row=0, sticky='ew')


    gameinfoLabel = ttk.Label(canvasFrame, 
        text = "GameInfo",
        font = DFONT,
        justify='center',
        anchor='c',
        padding = (20, 0, 10, 0)
    )
    gameinfoLabel.grid(column=0, row=1, sticky="ew", pady=30)


    gameinfoString = tk.StringVar(canvasFrame)

    gameinfoBox = ttk.Entry(canvasFrame,
        style = "CFG.TEntry",
        font = ("Consolas", DFONT[1], 'normal'),
        textvariable=gameinfoString
    )
    gameinfoBox.grid(column=1, row=1, sticky='ew')


    nameString.trace("w", lambda a, b, c: SaveName(nameString)) #Trace to save when user modifies this
    gameinfoString.trace("w", lambda a, b, c: cm.SaveForCFG("GameInfo", gameinfoString))


    giSelect, giGoto = cm.AppendButtons(canvasFrame) # Create the buttons, for GameInfo bar
    giSelect.grid(column=2, row=1, sticky='ew', padx = 10)
    giGoto.grid(column=3, row=1, sticky='ew')

    giSelect.bind("<Button>", lambda e: cm.SetPath(gameinfoBox, (".txt"))) # Bind the Select button, for path selection
    giGoto.bind("<Button>", lambda e: cm.Goto(gameinfoBox.get())) # Bind the Goto/Show button, to show the path 

    separator = ttk.Separator(canvasFrame, orient='horizontal') # Separator for the module dependend Entries
    separator.grid(column=0, row=2, columnspan=4, sticky="ew", pady=10)

    cm.SetGlobal("Name", (nameBox, nameString))                    # Set the values
    cm.SetGlobal("GameInfo", (gameinfoBox, gameinfoString))        #
    cm.SetGlobal("ConfigWindow", (canvasFrame, 2))  # <- Used for module specific fields


def AppendConfigName(cfg): #Add this config name to the list of configs and update the ConfigDropdown widget, used for loading
    global configs
    if cfg not in configs:
        configs.append(cfg)
        cm.GetGlobal("ConfigDropdown").config(values=configs)

def SaveDefault(): # Load default state and save, used when settings.json is empty, so only once
    print("Loading default for config tab!")
    cm.GetGlobal("ConfigDropdown").config(values = ("New Config"))
    cm.SaveData("cfg", "NewSave", 'GameInfo', '')

def Load(): # Loads this module's dependent settings
    data = cm.RetrieveJson() 
    configs = data["cfg"].keys() #Get the list of names
    for item in configs: # For every name, append it to the ConfigDropdown
        AppendConfigName(item)

def LoadFor(cfg): # Load values for every object
    print("Loading for " + str(cfg))
    data = cm.RetrieveJson()
    config_dict = data["cfg"] # Get the CFG dictionary
    settings = config_dict[cfg] # Now get the dictionary that is bound to this name

    cm.SetGlobal("disable_save", True)  # Disable saving, so it doesn't clear the field and save it as clear, ruining the save

    for setting in settings.keys(): # For every name in keys
        entry = cm.GetGlobal(setting)[0] # Retrieve the entry key, it's a tuple of the entry box and stringvar, we only want the box [0]
        entry.delete(0, tk.END) # Clear the field
        entry.insert(0, settings[setting]) # Insert the saved setting/path
    
    nameField = cm.GetGlobal("Name")[0] #Insert the name, since it's stored differently
    nameField.delete(0, tk.END)
    nameField.insert(0, cfg)

    cm.SetGlobal("disable_save", False) # Enable saving again, we're done loading

def SaveName(tkString: tk.StringVar): # Save the name
    print("Saving name")
    
    if tkString.get() == cm.GetGlobal("ConfigDropdown").get(): #We just loaded to field, no need to save
        return

    data = cm.RetrieveJson()["cfg"]
    data[tkString.get()] = data[cm.GetGlobal("ConfigDropdown").get()]
    del data[cm.GetGlobal("ConfigDropdown").get()]
    cm.SaveRaw("cfg", data)
    configs.clear()
    Load()
    cm.GetGlobal("ConfigDropdown").set(tkString.get())
