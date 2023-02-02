from PIL import ImageTk, Image 
from tkinter import filedialog as fd
import json
import tkinter as tk
from tkinter import ttk
import os

jsonData = {}
savePath = ''

default_settings = {} # Dictionary storing default settings, these are appended by modules on startup

def CalculateAspectRatio(img):
    '''Calculates aspect ratio of an image'''
    width, height = img.size
    return width / height

def MaximumScale(img, size: tuple):
    '''Calculates the maximum size this pic can be, with the current aspect ratio.'''
    aspect = CalculateAspectRatio(img)
    size_aspect = size[0] / size[1]
    width = 0
    height = 0

    if size[0] < 100 or size[1] < 100:
        return 100, 100

    if size_aspect < aspect:
        width = size[0]
        height = int(width / aspect)
    elif size_aspect >= aspect:
        height = size[1]
        width = int(height * aspect)

    return width, height

def ResizeWrapLength(ent, length: int, max: int = 300, min: int = 1, multiplier: float = 0.9, endmultiplier = 1):
    '''Dynamically resizes wrap lenght for ttk.Label'''
    #print("Resizing Wrap lenght for " + str(ent))

    length *= multiplier #Snap multiplier
    if max > length > min:
        ent.config(wraplength = length * endmultiplier)
    elif length > max:
        ent.config(wraplength = max)
    else:
        ent.config(wraplength = min)

def ResizePicture(pic, size: tuple):
    return ImageTk.PhotoImage(pic.resize(size, Image.ANTIALIAS))

def ApplyResizeImage(cont, var, storage):
    '''Applies the resized image to the element\n
        var - opened picture file\n
        storage - name for the file to be in global scope
    '''
    width, height = MaximumScale(var, (cont.winfo_width(), cont.winfo_height()))
    globals()[storage] = ResizePicture(var, (width - 20, height - 20))
    cont.config(image = globals()[storage])

def SetPath(field: ttk.Entry, filetype: str):
    '''Used in Select path buttons'''
    field.delete(0, tk.END)
    field.insert(0, Select(filetype))

def Goto(path: str):
    '''Shows the file/folder in explorer'''
    path = path.replace("/", '\\')
    openstr = f'explorer /select,"{path}"'
    os.system(openstr)

def Select(type):
    """ Opens up file dialog\ntype - extension of the file, pass 'folder' to for folder selection."""

    if type == 'folder':
        return fd.askdirectory()
    else:
        return fd.askopenfilename(filetypes=[("", type)])

def AddConfigPath(name, extension = '.exe'):
    '''Adds config path to the config tab, returns the a tuple of (ttk.Entry, tk.StringVar) elements'''
    cfgWindow = GetGlobal("ConfigWindow")

    cfgWindow[1] += 1
    SetGlobal("ConfigWindow", (cfgWindow[0], cfgWindow[1]))
    current_row = cfgWindow[1]
    container = cfgWindow[0]

    container.rowconfigure(index = current_row, weight = 0)

    label = ttk.Label(container,
        text = name,
        font = GetGlobal("font"),
        justify='center',
        anchor='c',
        padding = (20, 0, 10, 0)
    )

    entryString = tk.StringVar(container)

    entry = ttk.Entry(container,
        style = "CFG.TEntry",
        font = ("Consolas", GetGlobal("font"), 'normal'),
        textvariable=entryString
    )

    select, goto = AppendButtons(container)

    select.grid(column=2, row=current_row, sticky='ew', padx = 10)
    goto.grid(column=3, row=current_row, sticky='ew')

    label.grid(column=0, row=current_row, sticky='ew')
    entry.grid(column=1, row=current_row, sticky='ew')

    entryString.trace("w", lambda a, b, c: SaveForCFG(name, entryString))

    select.bind("<Button>", lambda e: SetPath(entry, (extension)))
    goto.bind("<Button>", lambda e: Goto(entry.get()))

    globals()[name] = entry # Add this field to globals, so we can read and write to it
    AppendGlobal("EntryList", name)
    return entry, entryString

def AppendButtons(container):
    Select = ttk.Button(container,
        text= 'Select',
        style = 'CFG.TButton',
    )

    Goto = ttk.Button(container,
        text = 'Show',
        style = 'CFG.TButton',
    )

    return Select, Goto

def Popup(text):
    '''Make a popup with text'''
    window = tk.Toplevel(globals()['root'], 

    )
    label = ttk.Label(window, 
        text=text,
        font=globals()['font'],
        borderwidth=5,
        relief='flat'
        )

    label.pack(fill='x', padx=50, pady=25)

    button_close = ttk.Button(window, 
        text="Close", 
        command=window.destroy)

    button_close.pack(fill='x')
    window.attributes("-topmost", 1)
    window.grab_set()


# Save managment


def LoadJson(path: str):
    global jsonData
    global savePath
    savePath = path
    try:
        file = open(path, "r")
        jsonData = json.load(file)
        if not jsonData:
            return False
        return True
    except:
        open(path, "w")
        return False



def SaveData(type, entry, slot, value):
    '''Used to save the data to json'''
    print("Saving data!")
    global jsonData
    try:#Data exists, modify
        #print("Level 0")
        print(f"Type {type}")
        print(f"entry {entry}")
        print(f"slot {slot}")
        print(f"Value {value}")
        jsonData[type][entry][slot] = value
        print(jsonData)
    except: #Build data from scratch, start at first level
        try:
            #print("Level 1")
            temp = {}
            temp[slot] = value
            jsonData[type][entry] = temp
        except: #Level upward
            #print("Level 2")
            temp = {}
            temp[slot] = value
            temp2 = {}
            temp2[entry] = temp
            jsonData[type] = temp2
            #print("Temp is " + str(temp))
            #print("Temp 2 is " + str(temp2))
            #print("Json Data is " + str(jsonData))

    json.dump(jsonData, open(savePath, "w"), indent=4, sort_keys=True, check_circular=False)
    ReloadJson()



def GetData(type: str, name: str = 'none', config: str = 'none'):
    global jsonData
    to_return = {}

    if type != 'cfg' and type != 'app':
        raise ValueError(f"Type {type} is invalid!")

    if type == 'cfg':
        def_name = 'Configuration'
    else:
        def_name = name


    if name == 'none': #We want the whole app/cfg block
        if config != 'none':
            raise ValueError("Name is not set, but config is!")
        try:
            to_return = jsonData[type]
        except KeyError: # This part doesn't exist, return and save the default one
            
            jsonData[type] = default_settings[type]
            json.dump(jsonData, open(savePath, "w"), indent=4, sort_keys=True, check_circular=False)
            ReloadJson()

        to_return = jsonData[type]

    elif config == 'none': #We want the whole name block
        try:
            to_return = jsonData[type][name]
        except KeyError:
            try:
                jsonData[type] # If this didn't fail, it means we're missing a name or a tab attribute
                if type == 'cfg' and not "New Configuration" in name: # We are only looking at the app part, not the cfg, since names can be customized
                    raise ValueError(f"Invalid name of {name} was passed!")
                
                jsonData[type][name] = default_settings[type][def_name]
                json.dump(jsonData, open(savePath, "w"), indent=4, sort_keys=True, check_circular=False)
                ReloadJson()

            except KeyError: # If even upper code failed, this means we are missing the whole block
                jsonData[type] = default_settings[type]
                json.dump(jsonData, open(savePath, "w"), indent=4, sort_keys=True, check_circular=False)
                ReloadJson()
                
        to_return = jsonData[type][name]
    
    else: #We want a specific element
        try:
            #print("Tried!")
            to_return = jsonData[type][name][config]
            #print("Going further")
        except KeyError: # We don't have this config
            try:
                #print("Trying type name")
                #print(jsonData)
                jsonData[type][name] #Check if we have this name in general
                #print("Going further")
                jsonData[type][name][config] = default_settings[type][def_name][config] # We do, so save for this name, attribute of the default name
                json.dump(jsonData, open(savePath, "w"), indent=4, sort_keys=True, check_circular=False)
                ReloadJson()

            except KeyError:
                try:
                    #print("Trying structure")
                    jsonData[type] # Check if we have the block
                    #print("Passed")
                    if type == 'cfg' and not "New Configuration" in name:
                        #print("Raising error")
                        raise ValueError(f"Invalid name of {name} was passed!") # We only look at the app!

                    jsonData[type][name] = default_settings[type][def_name]
                    json.dump(jsonData, open(savePath, "w"), indent=4, sort_keys=True, check_circular=False)
                    ReloadJson()

                except KeyError: #We don't even have the block
                    jsonData[type] = default_settings[type]
                    json.dump(jsonData, open(savePath, "w"), indent=4, sort_keys=True, check_circular=False)
                    ReloadJson()

        to_return = jsonData[type][name][config]
    #print("To return: " + str(to_return))
    return to_return

def ReloadJson():
    global jsonData
    jsonData = {} #Flush the variable
    LoadJson(savePath)

def SetGlobal(name: str, value):
    '''Set a global, or change its value'''
    globals()[name] = value

def GetGlobal(key: str):
    ''''Get the global from this script's scope'''
    return globals()[key]

def AppendGlobal(key: str, value):
    '''Append value to a global list'''
    globals()[key].append(value)

def SaveRaw(type, save):
    '''Saves raw json data, very dangerous! Should only be used for saving the name for CFG tab'''
    global jsonData
    jsonData[type] = save
    json.dump(jsonData, open(savePath, "w"), indent=4)
    ReloadJson()

def SaveForCFG(name, tkString: tk.StringVar):
    '''Save state for an cfg attribute'''
    if globals()["disable_save"] == True:
        return
    name = name.replace("Entry", '')
    print(f"Saving {name} for " + str(globals()["ConfigDropdown"].get()))
    SaveData("cfg", globals()["ConfigDropdown"].get(), name, tkString.get())

def SaveForAPP(tab: str, name: str, value):
    '''Save state for an app attribute'''
    if globals()["disable_save"] == True:
        return
    print(f"Saving app for {name}")
    SaveData("app", tab, name, value)

