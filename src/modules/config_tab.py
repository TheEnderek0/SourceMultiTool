import tkinter as tk
from tkinter import ttk
from . import common_lib as cm
import pathlib as pl

PATH_INFO_TEXT = "Path setup"

saveDictionary = {}


configs = []

def Init(container):
    print("Initialising Configuration tab")

    frame = ttk.Frame(container, style='Card.TFrame')                    # ---|
    frame.grid(column=0, row=0, sticky="nsew")      #    | Initialise the main frame for notebook
    container.add(frame, text = 'Configuration')    # ---|

    frame.rowconfigure(index=0, weight=0)           #  
    frame.rowconfigure(index=1, weight=1)           #  Configure the rows for the frame
    frame.columnconfigure(index=0, weight=1)        #
    frame.columnconfigure(index=1, weight=2)        #

    SaveSelector(frame)
    PathSelect(frame)
    OptionMenu(frame)

def OptionMenu(cont):

    label = ttk.Label(cont,    
                        text="Options",
                        wraplength=1200,    
                        justify='center',   
                        anchor='c',
                        style='ShortInfo.TLabel'   
                        )              

    opFrame = ttk.Labelframe(cont, labelwidget=label, labelanchor='n')
    opFrame.grid(column=1, row=1, sticky='nsew', padx=5)

    opFrame.columnconfigure(index=0, weight=0)
    opFrame.columnconfigure(index=1, weight=1)
    opFrame.rowconfigure(index=0, weight=0)




def SaveSelector(cont):

    sFrame = ttk.Frame(cont, style='TFrame')                                                       #   Configure the frame for the selector widget, and selector buttons
    sFrame.grid(column=0, columnspan=2, row=0, sticky='new')                           #

    sFrame.columnconfigure(index = 0, weight = 5)                                       #
    sFrame.columnconfigure(index = 1, weight = 0)                                       #   Configure the grid for the sFrame
    sFrame.columnconfigure(index = 2, weight = 0)                                       #
    sFrame.rowconfigure(index = 0, weight = 0)                                          #

    #################
    # Selector
    selector = ttk.Combobox(sFrame, state='readonly', values=[])                    #   Make the combobox widget, the selector
    selector.grid(column = 0, row = 0, sticky='ew', padx=10, pady=20)                                     #

    selector.bind("<<ComboboxSelected>> ", lambda e: LoadFor(selector.get()))           #   Bind the LoadFor function to the widget, every time user changes the selection load the data for that selection.

    cm.SetGlobal("ConfigDropdown", selector)                                            #   Set the selector as a global value

    # Add, Delete buttons
    addButton = ttk.Button(sFrame,
        text="Add New Configuration",
        style = 'Small.TButton',
    )

    deleteButton = ttk.Button(sFrame,
        text = "Delete Configuration",
        style = "Small.TButton",
    )

    addButton.grid(column=1, row=0, sticky='ew', padx=10, pady=20)
    deleteButton.grid(column=2, row=0, sticky='ew', padx=10, pady=20)

    addButton.bind("<Button>", lambda e: AddConfig())
    deleteButton.bind("<Button>", lambda e: DeleteConfig())



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
        justify='center',                     
        anchor='c',
        style='ShortInfo.TLabel'                           
        )                                     


    #   Create a frame for the scrolling canvas
    scrollFrame = ttk.Labelframe(mainFrame, labelwidget=label, labelanchor='n')
    scrollFrame.grid(column=0, row=2, sticky='nsew', padx=5)

    scrollFrame.columnconfigure(index=0, weight=1)
    scrollFrame.columnconfigure(index=1, weight=0)
    scrollFrame.rowconfigure(index=0, weight=1)

    # Create the scrollbar
    scrollbar = ttk.Scrollbar(scrollFrame, orient='vertical')
    scrollbar.grid(column=1, row=0, sticky='ns')

    # Create the canvas
    canvas = tk.Canvas(scrollFrame, yscrollcommand=scrollbar.set, borderwidth=cm.GetGlobal('Canvas_borderwidth').get(), relief=cm.GetGlobal('Canvas_relief').get())
    cm.GetGlobal('Canvas_borderwidth').trace_add('write', lambda a, b, c: canvas.configure(borderwidth=cm.GetGlobal('Canvas_borderwidth').get())) # Make sure it updates when we change to a different style
    cm.GetGlobal('Canvas_relief').trace_add('write', lambda a, b, c: canvas.configure(relief=cm.GetGlobal('Canvas_relief').get()))

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
        style = 'ShortInfo.TLabel',
        justify="center",
        anchor='c',
        padding = (20, 0, 10, 0)
    )
    nameLabel.grid(column=0, row=0, sticky='ew')


    nameString = tk.StringVar(canvasFrame) #Make a string var for further tracing

    nameBox = ttk.Entry(canvasFrame,
        style = "Other.TEntry",
        textvariable=nameString
    )
    nameBox.config(font = cm.AddFontTraces(nameBox))
    
    nameBox.grid(column=1, row=0, sticky='ew')


    gameinfoLabel = ttk.Label(canvasFrame, 
        text = "GameInfo",
        style = 'ShortInfo.TLabel',
        justify='center',
        anchor='c',
        padding = (20, 0, 10, 0)
    )
    gameinfoLabel.grid(column=0, row=1, sticky="ew", pady=30)


    gameinfoString = tk.StringVar(canvasFrame)

    gameinfoBox = ttk.Entry(canvasFrame,
        style = "Path.TEntry",
        textvariable=gameinfoString
    )
    gameinfoBox.config(font=cm.AddFontTraces(gameinfoBox))

    gameinfoBox.grid(column=1, row=1, sticky='ew')
    gameinfoString.trace_add("write", lambda e, sussycode, w: cm.CheckPathValidity(gameinfoBox, 'File', ext='.txt'))

    cm.SetGlobal("game_path", cm.SplitPath(pl.Path(gameinfoString.get())))
    gameinfoString.trace_add('write', lambda a, b, c: cm.SetGlobal("game_path",    cm.SplitPath(pl.Path(gameinfoString.get()))[0]     )) # Save the path

    nameString.trace_add("write", lambda a, b, c: SaveName(nameString)) #Trace to save when user modifies this
    gameinfoString.trace_add("write", lambda a, b, c: cm.SaveForCFG("GameInfo", gameinfoString))


    giSelect, giGoto = cm.AppendButtons(canvasFrame) # Create the buttons, for GameInfo bar
    giSelect.grid(column=2, row=1, sticky='ew', padx = 10)
    giGoto.grid(column=3, row=1, sticky='ew')

    giSelect.bind("<Button>", lambda e: cm.SetPath(gameinfoBox, [("Text files", ".txt")])) # Bind the Select button, for path selection
    giGoto.bind("<Button>", lambda e: cm.Goto(gameinfoBox.get())) # Bind the Goto/Show button, to show the path 

    separator = ttk.Separator(canvasFrame, orient='horizontal') # Separator for the module dependend Entries
    separator.grid(column=0, row=2, columnspan=4, sticky="ew", pady=10)

    canvasFrame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all"))) # Ensure proper scrolling

    cm.SetGlobal("Name", (nameBox, nameString))                    # Set the values
    cm.SetGlobal("GameInfo", (gameinfoBox, gameinfoString))        #
    cm.SetGlobal("ConfigWindow", (canvasFrame, 2))  # <- Used for module specific fields
    cm.SetGlobal("EntryList", ["GameInfo"])


def AppendConfigName(cfg): #Add this config name to the list of configs and update the ConfigDropdown widget, used for loading
    global configs
    if cfg not in configs:
        configs.append(cfg)
        cm.GetGlobal("ConfigDropdown").config(values=configs)

def SaveDefault(): # Load default state and save, used when settings.json is empty, so only once
    #print("Loading default for config tab!")
    #cm.GetGlobal("ConfigDropdown").config(values = ("New Config"))
    #cm.SaveData("cfg", "NewSave", 'GameInfo', '')
    #cm.SaveData("app", "config_tab", 'cfg_index', 0)
    #cm.SaveData("app", "config_tab", "active_cfg", "NewSave")
    pass

def Load(opening = False): # Loads this module's dependent settings
    #data = cm.RetrieveJson() 
    #configs = list(data["cfg"].keys()) #Get the list of names
    keys = list(cm.GetData('cfg').keys())
    for item in keys: # For every name, append it to the ConfigDropdown
        AppendConfigName(item)
    
    if opening:
        current = cm.GetData("app", "config_tab", "active_cfg") # Load the config from settings.json
        if current not in configs: # Something must have saved wrongly, if this is true
            cm.GetGlobal("ConfigDropdown").set(configs[0])
            LoadFor(configs[0])
        else:
            cm.GetGlobal("ConfigDropdown").set(current)
            LoadFor(current)

def LoadFor(cfg): # Load values for every object
    print("Loading for " + str(cfg))
    #data = cm.RetrieveJson()
    #config_dict = data["cfg"] # Get the CFG dictionary
    #settings = config_dict[cfg] # Now get the dictionary that is bound to this name
    cm.SaveData("app", "config_tab", "active_cfg", cm.GetGlobal("ConfigDropdown").get())
    cm.SetGlobal("disable_save", True)  # Disable saving, so it doesn't clear the field and save it as clear, ruining the save

    for setting in cm.GetGlobal("EntryList"): # For every name in entries, we cannot do keys because user can modify the settings!
        #try:
        entry = cm.GetGlobal(setting)[0] # Retrieve the entry key, it's a tuple of the entry box and stringvar, we only want the box [0]
        entry.delete(0, tk.END) # Clear the field
        entry.insert(0, cm.GetData('cfg', cfg, setting)) # Insert the saved setting/path
        cm.CheckPathValidity(entry)
        #except:
        #print(f"No key for {setting}")
    
    nameField = cm.GetGlobal("Name")[0] #Insert the name, since it's stored differently
    nameField.delete(0, tk.END)
    nameField.insert(0, cfg)
    cm.GetGlobal("configuration").set(cfg) # Set this configuration, this will make a chain reaction for other modules to load the data

    cm.SetGlobal("disable_save", False) # Enable saving again, we're done loading

def SaveName(tkString: tk.StringVar): # Save the name, only used to modify the name, not make a new element
    print("Saving name")

    name = tkString.get()
    data = cm.GetData('cfg')
    state = cm.GetGlobal("disable_save")
    testname = cm.GetGlobal("ConfigDropdown").get()

    print(f"SaveName run with first name, {name}, testname = {testname}, state = {state}")
    if name == cm.GetGlobal("ConfigDropdown").get(): #We just loaded to field, no need to save
        print("We just loaded!")
        return

    if name in list(data.keys()):
        entry = cm.GetGlobal("Name")[0]
        entry.delete(0, tk.END)
        name += "*"
        entry.insert(0, name) # Basically reset the box, and insert the old name
        cm.Popup("You can't have configurations with the same name!")
    
    if cm.GetGlobal("disable_save"):
        print("Disabling name saving!")
        return
    #print(f"Names are {name} and {testname}")

    data[name] = data[cm.GetGlobal("ConfigDropdown").get()]
    del data[cm.GetGlobal("ConfigDropdown").get()]
    #print(data)
    cm.SaveRaw("cfg", data)
    configs.clear()
    Load()
    cm.GetGlobal("ConfigDropdown").set(name)
    cm.SaveData("app", "config_tab", "active_cfg", cm.GetGlobal("ConfigDropdown").get())

def AddConfig():
    global configs
    print("==============================")
    #Ensure we won't have keys with the same name
    cfg_index = cm.GetData("app", "config_tab", "cfg_index")
    
    name = f"New Configuration {cfg_index}"
    cfg_index += 1
    print(f"CFG index after {cfg_index}")
    print(f"New name is {name}")
    cm.SaveData("app", "config_tab", "cfg_index", cfg_index) # Save the index so we won't have to loop again

    # Set the name, GetData should automatically append all of the default values!
    AppendConfigName(name)
    cm.GetGlobal("ConfigDropdown").set(name)
    cm.SaveData("app", "config_tab", "active_cfg", cm.GetGlobal("ConfigDropdown").get())
    LoadFor(name)

def DeleteConfig():
    global configs
    data = cm.GetData("cfg")
    del data[cm.GetGlobal("ConfigDropdown").get()] # Delete the config
    cm.SaveRaw('cfg', data)
    index = configs.index(cm.GetGlobal("ConfigDropdown").get())
    configs.clear()
    Load()
    if len(configs) <= index: # Do this so we don't encounter index out of range
        index = len(configs)
    cm.GetGlobal("ConfigDropdown").set(configs[index])
    cm.SaveData("app", "config_tab", "active_cfg", cm.GetGlobal("ConfigDropdown").get())
    


