from PIL import ImageTk, Image 
from tkinter import filedialog as fd
import json
import tkinter as tk
from tkinter import ttk
import os, stat
import shutil
from sys import platform
import pathlib as pl #I'm are going to replace the os module with this shortly

from threading import Thread, Event
from queue import Queue, Empty
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired


jsonData = None
if 'win' in platform:
    savePath = pl.Path(   "./settings.json"   )

defaultPath = pl.Path('./bin/defaults.json')

configuration = None # A tk.StringVar used to store the current config

default_settings = {} # Dictionary storing default settings, these are appended by modules on startup

load_functions = [] # List of functions, that are called when the app interface is done loading, and we need to load the "APP" block from the settings


def Init(a):
    global configuration
    configuration = tk.StringVar(a) # A string used to store the current config


def AppendLoading(func):
    global load_functions
    load_functions.append(func)

def LOAD():
    global load_functions

    SetGlobal('disable_save', True) # Disable saving for when we load

    for function in load_functions:
        function()

    SetGlobal('disable_save', False)




# GUI
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

def AddConfigPath(name, shownName, extension = '.exe'):
    '''Adds config path to the config tab, returns the a tuple of (ttk.Entry, tk.StringVar) elements'''
    cfgWindow = GetGlobal("ConfigWindow")


    container = cfgWindow[0]
    current_row = cfgWindow[1]
    current_row += 1
    SetGlobal("ConfigWindow", (container, current_row))

    container.rowconfigure(index = current_row, weight = 0)

    label = ttk.Label(container,
        text = shownName,
        style = 'ShortInfo.TLabel',
        justify='center',
        anchor='c',
        padding = (20, 0, 10, 0)
    )

    entryString = tk.StringVar(container)

    entry = ttk.Entry(container,
        style = "Path.TEntry",
        font= (GetGlobal('TEntry_font').get(), GetGlobal('TEntry_font_size').get(), GetGlobal('TEntry_font_style').get()),
        textvariable=entryString
    )

    GetGlobal('TEntry_font').trace_add(      'write', lambda a, b, c: entry.configure(font= (GetGlobal('TEntry_font').get(), GetGlobal('TEntry_font_size').get(), GetGlobal('TEntry_font_style').get()) ))
    GetGlobal('TEntry_font_size').trace_add( 'write', lambda a, b, c: entry.configure(font= (GetGlobal('TEntry_font').get(), GetGlobal('TEntry_font_size').get(), GetGlobal('TEntry_font_style').get()) ))
    GetGlobal('TEntry_font_style').trace_add('write', lambda a, b, c: entry.configure(font= (GetGlobal('TEntry_font').get(), GetGlobal('TEntry_font_size').get(), GetGlobal('TEntry_font_style').get()) ))

    select, goto = AppendButtons(container)

    select.grid(column=2, row=current_row, sticky='ew', padx = 10)
    goto.grid(column=3, row=current_row, sticky='ew')

    label.grid(column=0, row=current_row, sticky='ew')
    entry.grid(column=1, row=current_row, sticky='ew')

    entryString.trace_add("write", lambda a, b, c: SaveForCFG(name, entryString))

    select.bind("<Button>", lambda e: SetPath(entry, [("", extension)]))
    goto.bind("<Button>", lambda e: Goto(entry.get()))
    entryString.trace("w", lambda e, amogus, sus: CheckPathValidity(entry, ext=extension))

    globals()[name] = (entry, entryString) # Add this field to globals, so we can read and write to it
    AppendGlobal("EntryList", name)

    path = pl.Path()
    globals()[name + "_path"] = path

    entryString.trace_add('write', lambda a, b, c: SetGlobal(name + "_path",    pl.Path(entryString.get()))     )
    
    return entry, entryString

def AppendButtons(container):
    Select = ttk.Button(container,
        text= 'Select',
        style = 'Small.TButton',
    )

    Goto = ttk.Button(container,
        text = 'Show',
        style = 'Small.TButton',
    )
    
    return Select, Goto

def Popup(text):
    '''Make a popup with text'''
    window = tk.Toplevel(globals()['root'], 

    )
    label = ttk.Label(window, 
        text=text,
        style='INFO.TLabel'
        )

    label.pack(fill='x', padx=50, pady=25)

    button_close = ttk.Button(window, 
        text="Close", 
        style='Small.TButton',
        command=window.destroy)

    button_close.pack(fill='x', padx=50)
    window.attributes("-topmost", 1)
    window.grab_set()

def ModuleWindow(container):
    container.rowconfigure(index = 0, weight = 1)
    container.rowconfigure(index = 1, weight = 0)
    container.columnconfigure(index = 0, weight = 1)

    WindowFrame = ttk.Frame(container, style='TFrame', padding=(10, 10, 10, 10))
    WindowFrame.grid(column=0, row=0, sticky='nsew')

    BarFrame = ttk.Labelframe(container, style='TLabelframe', labelanchor='n', text='Progress')
    BarFrame.grid(column=0, row=1, sticky='nsew',padx=10,pady=5)
    BarFrame.rowconfigure(index = 0, weight = 1)
    BarFrame.columnconfigure(index = 0, weight = 1)

    Bar = ttk.Progressbar(BarFrame,
                            style='info.Striped.Horizontal.TProgressbar',
                            orient='horizontal',
                            mode='determinate',
                            length=280,
                            value=0
                            
                           )
    Bar.grid(column = 0, row = 0, sticky='ew', padx=10, pady=(0, 5))
    return WindowFrame, Bar

def IObars(WindowFrame, InputModeTracer: tk.BooleanVar, OutputModeTracer: tk.BooleanVar, output_default_path_r:str, module_prefix, extension_arg='.txt', InputCallback:list = None, OutputCallback:list = None):
    '''
    Adds and configures Input Output entries. This function automatically handles saving/loading data for these bars!
    \n
    WindowFrame - parent window of the bars.\n
    InputModeTracer - Use this to trace the selected input mode (True for File / False for Folder).\n
    OutputModeTracer - Use this to trace the selected output mode (True for default game dir / False for user selected dir).\n
    Output_default_path_r - Path relative to gameinfo, where the default game dir should be located (For example "/resource").\n
    module_prefix - Prefix for the module/tab, used for saving.\n
    extension_arg - Extension for input files.\n
    InputCallback - additional functions to execute when input combobox is selected.\n
    OutputCallback - -||- output combobox.\n
    '''
    WindowFrame.columnconfigure(index = 0, weight = 0)  # For the folder or file radiobutton
    WindowFrame.columnconfigure(index = 1, weight = 0) # For the labels
    WindowFrame.columnconfigure(index = 2, weight = 1) # for the entry box
    WindowFrame.columnconfigure(index = 3, weight = 0) # for select, show buttons
    WindowFrame.columnconfigure(index = 4, weight = 0)
    
    WindowFrame.rowconfigure(index = 0, weight = 0)
    WindowFrame.rowconfigure(index = 1, weight = 0)

    InputLabel = ttk.Label(WindowFrame,
                           style='ShortInfo.TLabel',
                           text = "Input",
                           padding = (10, 10, 10, 10),
                           )
    OutputLabel = ttk.Label(WindowFrame,
                            style='ShortInfo.TLabel',
                            text = "Output",
                            padding = (10, 10, 10, 10),
                            )



    ExtensionSelectorOne = ttk.Combobox(WindowFrame,
                                            state='readonly',
                                            values=(f"File ({extension_arg})", "Folder"),
                                            style='IO.TCombobox'
                                        )
    ExtensionSelectorTwo = ttk.Combobox(WindowFrame,
                                            state='readonly',
                                            values=("Folder", "Default Game Directory"),
                                            style='IO.TCombobox'
                                           )

    ExtensionSelectorOne.grid(column=1, row=0, sticky='ew', padx=5, pady=5)
    ExtensionSelectorTwo.grid(column=1, row=1, sticky='ew', padx=5, pady=5)


    InputLabel.grid(column = 0, row = 0, sticky = 'ew')
    OutputLabel.grid(column = 0, row = 1, sticky='ew')

    InputString = tk.StringVar(WindowFrame)
    OutputString = tk.StringVar(WindowFrame)

    InputEntryBox = ttk.Entry(WindowFrame,
                                style = "Path.TEntry",
                                textvariable=InputString
                              )
    InputEntryBox.config(font=AddFontTraces(InputEntryBox))
    OutputEntryBox = ttk.Entry(WindowFrame,
                                style = "Path.TEntry",
                                textvariable=OutputString
                               )
    OutputEntryBox.config(font=AddFontTraces(OutputEntryBox))

    InputEntryBox.grid(column=2, row=0, sticky='ew', pady = 5)
    OutputEntryBox.grid(column=2, row=1, sticky='ew', pady = 5)

    ISelectButton, IGOTOButton = AppendButtons(WindowFrame)
    IGOTOButton.bind("<Button>", lambda e: GoToAdv(InputEntryBox.get(), ExtensionSelectorOne.get()))
    
    OSelectButton, OGOTOButton = AppendButtons(WindowFrame)
    OSelectButton.bind("<Button>", lambda e: SetPath(OutputEntryBox, [("", 'folder')]))
    OGOTOButton.bind("<Button>", lambda e: Goto(OutputEntryBox.get(),select=False))

    ISelectButton.grid(column = 3, row = 0, sticky='ew', padx=5)
    OSelectButton.grid(column = 3, row = 1, sticky='ew', padx=5)

    IGOTOButton.grid(column = 4, row = 0, sticky='ew')
    OGOTOButton.grid(column = 4, row = 1, sticky='ew')

    InputString.trace_add("write", lambda a, b, c: CheckPathValidity(InputEntryBox, ExtensionSelectorOne.get(), extension_arg))
    OutputString.trace_add("write", lambda e, a, b: CheckPathValidity(OutputEntryBox, 'folder', creatable=True))

    InputModeTracer.trace_add("write", lambda a, b, c: CheckPathValidity(InputEntryBox, ExtensionSelectorOne.get(), extension_arg))
    OutputModeTracer.trace_add("write", lambda e, a, b: CheckPathValidity(OutputEntryBox, 'folder', creatable=True))

    extension = tk.StringVar(WindowFrame)


    ExtensionSelectorOne.bind("<<ComboboxSelected>>", lambda e: ChangeExtension(ExtensionSelectorOne.get(), extension, extension_arg, InputModeTracer)) #Input tracing
    ISelectButton.bind('<Button>', lambda e: SetPath(InputEntryBox, [("", extension.get())]))                                                           #

    ExtensionSelectorTwo.bind("<<ComboboxSelected>>", lambda e: SelectorTwo(OutputEntryBox, OutputString, ExtensionSelectorTwo.get(), output_default_path_r, OutputModeTracer))
    GetGlobal('GameInfo')[1].trace_add('write', lambda a, b, c: SelectorTwo(OutputEntryBox, OutputString, ExtensionSelectorTwo.get(), output_default_path_r, OutputModeTracer)) # We need to trace if user changes gameinfo

    ExtensionSelectorOne.bind("<<ComboboxSelected>>", lambda e: SaveData("cfg", configuration.get(), module_prefix+"InputMode", ExtensionSelectorOne.get()), add=True)
    ExtensionSelectorTwo.bind("<<ComboboxSelected>>", lambda e: SaveData("cfg", configuration.get(), module_prefix+"OutputMode", ExtensionSelectorTwo.get()), add=True)
    InputString.trace_add('write', lambda a, b, c: SaveData('cfg', configuration.get(), module_prefix+'Input', InputString.get()))
    OutputString.trace_add('write', lambda a, b, c: SaveData('cfg', configuration.get(), module_prefix+'Output', OutputString.get()))

    configuration.trace_add('write', lambda a, b, c: ChangeExtension( GetData('cfg', configuration.get(), module_prefix+"InputMode"),  extension, extension_arg, InputModeTracer)) # Add this here instead of module specific Load for loop
    configuration.trace_add('write', lambda a, b, c: SelectorTwo(OutputEntryBox, OutputString, GetData('cfg', configuration.get(), module_prefix+"OutputMode"), output_default_path_r, OutputModeTracer))

    configuration.trace_add('write', lambda a, b, c: ExtensionSelectorOne.set(GetData('cfg', configuration.get(), module_prefix+"InputMode")))
    configuration.trace_add('write', lambda a, b, c: ExtensionSelectorTwo.set(GetData('cfg', configuration.get(), module_prefix+"OutputMode")))
    configuration.trace_add('write', lambda a, b, c: InputString.set(GetData('cfg', configuration.get(), module_prefix+"Input")))
    configuration.trace_add('write', lambda a, b, c: OutputString.set(GetData('cfg', configuration.get(), module_prefix+"Output")))

    normalizedInput = tk.StringVar(WindowFrame)
    normalizedOutput = tk.StringVar(WindowFrame)

    InputString.trace_add('write', lambda a, b, c: normalizedInput.set(os.path.normpath(InputString.get())))
    OutputString.trace_add('write', lambda a, b, c: normalizedOutput.set(os.path.normpath(OutputString.get())))

    if InputCallback:
        for function in InputCallback:
            InputModeTracer.trace_add('write', lambda e, b, c: function())

    if OutputCallback:
        for function in OutputCallback:
            OutputModeTracer.trace_add('write', lambda e, b, c: function())


    return normalizedInput, normalizedOutput

def OptionCanvas(container):
    container.columnconfigure(index=0, weight=1)
    container.columnconfigure(index=1, weight=0)
    container.rowconfigure(index=0, weight=1)

    scrollbar = ttk.Scrollbar(container, orient='vertical')
    scrollbar.grid(column=1, row=0, sticky='ns', padx=(0, 5), pady=(0, 5))

    canvas = tk.Canvas(container, yscrollcommand=scrollbar.set, borderwidth=GetGlobal('Canvas_borderwidth').get(), relief=GetGlobal('Canvas_relief').get() )

    GetGlobal('Canvas_borderwidth').trace_add('write', lambda a, b, c: canvas.configure(borderwidth=GetGlobal('Canvas_borderwidth').get())) # Make sure it updates when we change to a different style
    GetGlobal('Canvas_relief').trace_add('write', lambda a, b, c: canvas.configure(relief=GetGlobal('Canvas_relief').get()))

    canvas.grid(column=0, row=0, sticky='nsew', padx=(5, 0), pady=(0, 5))
    scrollbar.configure( command=canvas.yview )
    canvasFrame = ttk.Frame(canvas, padding=(20, 20, 20, 20))
    canvas.create_window((0, 0), window=canvasFrame, anchor='nw')
    container.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvasFrame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")), add='+') # Ensure proper scrolling

    return canvasFrame, canvas

def GoToAdv(path, state):
    if 'File' in state:
        Goto(path, select = True)
    else:
        Goto(path, select = False)

def CompileWindow(frame: ttk.Frame, toolname):

    frame.columnconfigure(index=0, weight=1)
    frame.columnconfigure(index=1, weight=0)
    MainCompileFrame = ttk.Frame(frame)

    frame.rowconfigure(index=0, weight=1)
    frame.rowconfigure(index=1, weight=0)
    frame.rowconfigure(index=2, weight=0)

    MainCompileFrame.grid(row=0, column=0, sticky='nsew')


    yscrollbar = ttk.Scrollbar(frame, orient='vertical')
    yscrollbar.grid(column=1, row=0, sticky='ns', padx=(0, 5), pady=(0, 0))

    xscrollbar = ttk.Scrollbar(frame, orient='horizontal')
    xscrollbar.grid(column=0, row=1, sticky='ew', padx=(0, 0), pady=(0, 5))

    ButtonFrame = ttk.Frame(frame)

    ButtonFrame.grid(column=0, columnspan=2, row=2, sticky='ew')
    ButtonFrame.columnconfigure(index=0, weight=1)
    ButtonFrame.columnconfigure(index=1, weight=1)
    ButtonFrame.columnconfigure(index=2, weight=1)
    ButtonFrame.columnconfigure(index=3, weight=1)
    ButtonFrame.columnconfigure(index=4, weight=1)
    ButtonFrame.columnconfigure(index=5, weight=1)
    ButtonFrame.rowconfigure(index=0, weight=1)

    ClearOnCompile = tk.BooleanVar(ButtonFrame)
    ScrollBool = tk.BooleanVar(ButtonFrame)

    BCompile = ttk.Button(ButtonFrame, style='Small.TButton', text='Compile')
    BStop = ttk.Button(ButtonFrame, style='Small.TButton', text='Stop')
    BNext = ttk.Button(ButtonFrame, style='Small.TButton', text='Next')
    BClear = ttk.Button(ButtonFrame, style='Small.TButton', text='Clear')
    BC = ttk.Checkbutton(ButtonFrame, style='Option.info.Outline.Toolbutton', text='Automatic Clear', onvalue=True, offvalue=False, variable=ClearOnCompile)
    Scroll = ttk.Checkbutton(ButtonFrame, style='Option.info.Outline.Toolbutton', text='Automatic Scroll', onvalue=True, offvalue=False, variable=ScrollBool)


    BCompile.grid(column=0, row=1, sticky='nsew', padx=10, pady=(0, 5))
    BStop.grid(column=1, row=1, sticky='nsew', padx=10, pady=(0, 5))
    BNext.grid(column=2, row=1, sticky='nsew', padx=10, pady=(0, 5))
    BClear.grid(column=3, row=1, sticky='nsew', padx=10, pady=(0, 5))
    BC.grid(column=4, row=1, sticky='nsew', padx=10, pady=(0, 5))
    Scroll.grid(column=5, row=1, sticky='nsew', padx=10, pady=(0, 5))


    ScrollBool.trace_add('write', lambda a, b, c: SaveData('app', toolname, 'auto_scroll', ScrollBool.get()))
    ClearOnCompile.trace_add('write', lambda a, b, c: SaveData('app', toolname, 'auto_clear', ClearOnCompile.get()))

    AppendLoading(  lambda: ClearOnCompile.set(GetData('app', toolname, 'auto_clear'))    )
    AppendLoading(  lambda: ScrollBool.set(GetData('app', toolname, 'auto_scroll'))     )

    return MainCompileFrame, BCompile, BStop, BNext, BClear, ScrollBool, ClearOnCompile, (yscrollbar, xscrollbar)

def AdditionalParameters(frame: ttk.Frame, column_, row_, toolname):

    textvar = tk.StringVar(frame)

    POLabel = ttk.Label(frame, text='Additional parameters:', style='ShortInfo.TLabel')
    ParamOverrideFrame = ttk.Labelframe(frame, style='TLabelframe', labelwidget=POLabel)
    ParamOverrideFrame.grid(column=column_, row=row_, sticky='nsew',pady=20)
    ParamOverrideFrame.columnconfigure(index=0, weight=1)
    ParamOverrideFrame.rowconfigure(index=1, weight=1)
    Entry = ttk.Entry(ParamOverrideFrame, style='Other.TEntry', textvariable=textvar)
    Entry.config(font=AddFontTraces(Entry))
    Entry.grid(column=0,row=1, sticky='nsew', padx=5, pady=5)

    textvar.trace_add('write', lambda a, b, c: SaveData('app', toolname, 'additional_params', textvar.get()))
    AppendLoading( lambda: textvar.set(     GetData('app', toolname, 'additional_params')       ) )

    return textvar

# MISC
def SetPath(field: ttk.Entry, filetype: str):
    '''Used in Select path buttons'''
    field.delete(0, tk.END)
    field.insert(0, Select(filetype))

def Goto(path: str, select = True):
    '''Shows the file/folder in explorer'''
    path = path.replace("/", '\\')
    if select:
        openstr = f'explorer /select,"{path}"'
    else:
        openstr = f'explorer "{path}"'
    os.system(openstr)

def Select(type:list):
    """ Opens up file dialog\ntype - extension of the file, pass 'folder' to for folder selection."""

    if type[0][1] == 'folder':
        return fd.askdirectory()
    else:
        return fd.askopenfilename(filetypes=type)
    
def GetHighestDLC(game: pl.Path):

    game_folder_name = game.stem # Get the game folder name
    game_f_path = game.parent # Path to the game folder

    game_folder_name = StripString(game_folder_name, "_dlc", Rl=True, include_phrase=True) # If the game folder is a dlc folder, strip the dlc out of the name
    print("AMOGUS WILD" + game_folder_name)
    dlc_list = game_f_path.glob(f"{game_folder_name}_dlc*")

    dlc_list = list(dlc_list) # Convert generator into list
    
    max_dlc_lvl = 0

    if len(dlc_list) == 0: # No dlcs found for this game
        return -1
    
    for path in dlc_list: # TODO
        
        path_ = str(path)
        path_ = StripString(path_, "_dlc", Rl=False, include_phrase=True) # Strip everything excluding the dlc number
        print("STRIPPED PATH " + path_)
        try:
            let = path_[1] # It means this has a suffix, if this doesn't error
            path_ = StripString(path_, let)

        except IndexError:
            pass
        dlc_lvl = int(path_)
        if dlc_lvl > max_dlc_lvl:
            print("Changing dlc level to " + str(max_dlc_lvl))
            max_dlc_lvl = dlc_lvl

        #except ValueError:
        #    return 0
        
    return max_dlc_lvl

def StripString(string: str, strip_phrase: str, Rl:bool = True, include_phrase:bool=False):
    '''
        Strips string by searching for the strip_phrase in the string.\n
        Rl - Right - true, left - False | Strip the left or right part of the string.\n
        include_phrase - Strip the phrase (true) or leave it (false)?\n
    '''


    ind = 0
    found_ind = 0 # Ending index of the search

    for let_ind in range(len(string)):
        let = string[let_ind]

        if let == strip_phrase[ind]:

            ind += 1
            found_ind = let_ind

            if ind == len(strip_phrase):
                break
    
    if ind != len(strip_phrase): # We didn't find the phrase
        return string


    if not include_phrase and Rl: # Right, don't include
        return string[:found_ind]
    
    elif include_phrase and not Rl: # Left, include
        return string[found_ind+1:]

    elif not include_phrase and not Rl: # Left, don't include
        i_ = found_ind - len(strip_phrase)
        return string[i_:]
    
    elif include_phrase and Rl: # Right, include
        i_ = found_ind - len(strip_phrase)
        return string[:i_-1]




def CheckPathValidity(entrybox: tk.Entry, state='File', ext='', creatable=False):
    '''Checks if a path is valid, and sets the text colour of the entrybox to green/red accordingly'''
    path = pl.Path(entrybox.get())
    correction = False
    Head, Tail = SplitPath(path)
    print("EXTENSION IN CHECK PATH VALIDITY IS " + ext)
    if not Head: # Validate and check if the path is ok
        entrybox.configure(style='danger.TEntry')
        return
    
    print("Checking path for " + str(entrybox))
    if 'File' in state and path.exists():
        if ext != '':
            print("EXTENSION SET")
            if ext in str(Tail):
                correction = path.is_file()
            else:
                correction = False
        else:
            correction = path.is_file()
    elif path.exists() and str(Tail) == '':
        correction = path.is_dir()

    if correction:
        entrybox.configure(style='success.TEntry')
    else:
        if creatable:
            entrybox.configure(style='warning.TEntry')
        else:
            entrybox.configure(style='danger.TEntry')
    print(correction)

def AddFontTraces(entry):
    GetGlobal('TEntry_font').trace_add(      'write', lambda a, b, c: entry.configure(font= (GetGlobal('TEntry_font').get(), GetGlobal('TEntry_font_size').get(), GetGlobal('TEntry_font_style').get()) ))
    GetGlobal('TEntry_font_size').trace_add( 'write', lambda a, b, c: entry.configure(font= (GetGlobal('TEntry_font').get(), GetGlobal('TEntry_font_size').get(), GetGlobal('TEntry_font_style').get()) ))
    GetGlobal('TEntry_font_style').trace_add('write', lambda a, b, c: entry.configure(font= (GetGlobal('TEntry_font').get(), GetGlobal('TEntry_font_size').get(), GetGlobal('TEntry_font_style').get()) ))
    return (GetGlobal('TEntry_font').get(), GetGlobal('TEntry_font_size').get(), GetGlobal('TEntry_font_style').get())

def SelectorTwo(entry: ttk.Entry, string:tk.StringVar, state: str, rel_path:str, outputstate: tk.BooleanVar):
    '''Changes the path of default game directory and user path. Should only be used internally.'''
    outputstate.set("Default" in state)
    if outputstate.get():
        gameinfo = GetGlobal('game_path')
        print("SELE======GAMEINFO IS" + str(gameinfo))
        head = SplitPath(gameinfo)[0]
        entry.configure(state="disabled")
        if not head:
            string.set("<GAMEINFO_PATH_ERROR>")
        else:
            print("HEAD IS " + str(head))
            print("RELPATH " + str(rel_path))
            print(str(head.joinpath(rel_path)))
            string.set(str(head.joinpath(rel_path)))
        CheckPathValidity(entry, 'folder', creatable=True) # This fires before this function, so we need to also check this again
    else:
        entry.configure(state="normal")

def ChangeExtension(state: str, extension: tk.StringVar, arg_ext: str, mode: tk.BooleanVar):
    '''Changes the extension, used for select button in input bar. Should only be used internally.'''
    if 'File' in state:
        extension.set(arg_ext)
        mode.set(True)
    else:
        print("FOLDER!")
        extension.set('folder')
        mode.set(False)

def CheckPathValidityBOOL(pathw: pl.Path, ext=''):
    '''Checks validity of path and returns several booleans:\n
        Bool (1) - Directory exists
        Tuple(Bool, Bool) - (File exists, File was typed in)
        Bool (2) - Correct filetype (Will return False if no file)
    '''
    Head, Tail = SplitPath(pathw)
    print("CHECK ")
    print(Head)
    print(Tail)
    if not Head: # Head
        if type(Tail) == bool:
            if Tail == False:
                return False, (False, False), False
        

    if str(Tail) == '':
        return Head.is_dir(), (False, False), False
    else:
        if ext != '':
            return Head.is_dir(), (pathw.is_file(), True), ext in Tail
        else:    
            return Head.is_dir(), (pathw.is_file(), True), True

def CheckGameInfo(gfPath: pl.Path):
    '''Given a path, checks if gameinfo exists and gives an appropriate error.\n
        No file: game = "<FILE_ERROR>", CompileOverrideError = "Cannot locate gameinfo.txt ..."\n
        Wrong path: game = "<PATH_ERROR>", CompileOverrideError = "Path is incorrect..."\n
        \n
        Returns a tuple of path game, bool True if succeeded, CompileOverrideError.\n
    '''
    game_state = CheckPathValidityBOOL(gfPath)
    CompileOverrideError = ''
    game = ''
    game_success = ''
    if game_state[0]: # Path exists
        if game_state[1]: # File exists
            game, File = SplitPath(gfPath)
            game_success = True
        else: #File does not exist
            CompileOverrideError = '\nCannot locate gameinfo.txt! \nMake sure the path in configuration tab is correct!'
            game = "<FILE_ERROR>"
    else: # The path is incorrect
        CompileOverrideError = '\nThe path for gameinfo.txt is incorrect! \nMake sure you enter the correct path in the configuration tab before proceeding!'
        game = "<PATH_ERROR>"
    return game, game_success, CompileOverrideError

def DetermineDLC(game: pl.Path, is_automatic: bool, manual_val: int):
    '''
    Determines the DLC level for current configuration.
    Returns a tuple of boolean and the dlc
    If boolean is true, we need to set the dlc, if not we don't need to pass the -d parameter
    '''
    HighestDLC = GetHighestDLC(game)
    dlc = ''
    if HighestDLC >= 0: # If DLC is -1, no DLC was detected
        if not is_automatic: # If this is true we are manually setting the DLC
            dlc = str(manual_val)
        else: # We are setting the dlc automatically
            dlc = str(HighestDLC)
    
    if dlc != '-1' and dlc != '': # If true, DLC needs to be set
        return True, dlc
    else:
        return False, dlc #DLC is not required, this game does not have dlc

def SplitPath(path: pl.Path): # A better version of os.path.split()
    '''Slices the path into directory and filename, if there is no file specified, filename is empty
    Can return False, False when the filepath is wrong!'''
    name = path.name
    if '.' in name: # Path leads to a file
        return path.parent, name
    else:
        return path, ''
            
def CheckInputValidity(path, ext, mode):
    '''Checks if input path is valid, returns 3 values in a tuple:\n
    boolean - Valid/not valid.\n
    string - Error message for the compile field.\n
    string - Error message for the argument field.
    '''
    input_st = CheckPathValidityBOOL(path, ext)
    print("INPUT " + str(input_st))
    print("INPUT MODE = " + str(mode))
    if input_st[0]: #Path exists
        if input_st[1][1]: # File was specified
            if mode: #File mode is on
                if input_st[1][0]: # File exists
                    if input_st[2]: # File has correct extension
                        return True, '', path
                    else: # File doesn't have a proper extension
                        return False, '\nWrong filetype of input file (must be a .txt file)!', "<WRONG_FILE_TYPE_ERROR>"
                else: # We are in proper mode but file does not exist
                    return False, '\nInput file does not exist!', "<FILE_DOES_NOT_EXIST>"
            else: # We are in folder mode but file specified
                return False, '\nInput mode is incorrect!', "<INPUT_MODE_ERROR>"


        elif not mode: # We are in folder mode and no file was specified
            return True, '', f'<Compile for every file in {path}>'
        else: # We are in file mode and no file was specified
            return False, '\nInput mode is incorrect!', "<INPUT_MODE_ERROR>" 


    elif not mode: # We are in proper mode but the path just doesn't exist
        return False, '\nSpecified path in Input does not exist!', '<PATH_DOESNT_EXIST_ERROR>'
    else:
        return False, '\nInput mode is incorrect!', "<INPUT_MODE_ERROR3>"


# Processes

class CompileTextWidget(tk.Text):
    def __init__(self, window, yscrollbar:ttk.Scrollbar, xscrollbar:ttk.Scrollbar = None, progressbar: ttk.Progressbar = None, scroll: tk.BooleanVar = None,files: int = 1, update_interval_ms = 50, max_lines=25):
        '''Text widget that gets the program output:\n
            window - Parent of this widget. \n
            canvas - The widget must be in a scrollable canvas, this makes it automatically scroll down when new lines are appended. \n
            progressbar - Progress bar to be used for tracking. (optional)\n
            scroll - a booleanVar tracking the state of the automatic scroll button
            files - How much files there are, used for properly showing the progressbar.\n
            update_interval_ms - How often to update the lines. (in miliseconds) (optional)\n
            max_lines - Maximum lines per operation (per update_interval_ms) (optional)\n
            \n
            To stop the updating set <thisobj>.stop = True. You should fire stop to the Program instead, as it also stops this widget.\n
        '''

        font, fsize = GetGlobal("compile_font")

        super().__init__(window, yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set, font= (font.get(), fsize.get()), wrap=tk.NONE  )
        self.config(state='disabled')
        yscrollbar.config(command = self.yview)
        xscrollbar.config(command = self.xview)

        self.ProgressBarActive = False
        self.queue = Queue()
        
        self.update_interval = update_interval_ms
        self.maxlines = max_lines
        self.stop = Event()
        if not scroll:
            self.Scroll = tk.BooleanVar(window, True) # A variable determining if we should stop scrolling
        else:
            self.Scroll = scroll
        self.progressbar = progressbar
        self.progresscount = tk.IntVar(window, 0) # We don't need to use thread safe solutions, since we are only reading here, no modifications are done
        self.filecount = 0 # ^^^


    def update_lines(self):
        print("Update lines called!")
        insertion = False # Used for scrolling
        for _ in range(self.maxlines):
            try:
                line = self.queue.get(block=False)
                #print("LINE is " + line)
            except Empty:
                #print("Line is empty!")
                break
            
            self.config(state='normal')
            self.insert(tk.END, line)
            self.config(state='disabled')
            #self.config(scrollregion=self.bbox("all"))
            self.queue.task_done()
            insertion = True

        print("[p[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]")
        print(self.progresscount.get())
        self.ClearProgressBar()
        self.UpdateProgressBar()
        
        if insertion and self.Scroll.get():
            print("Scrolling!")
            self.after(5, lambda: self.yview_moveto(1)) # Scroll to the end

        if self.stop.isSet() and self.queue.qsize() == 0:
            self.ProgressBarActive = False # Reset the progress bar so it clears on the next compile
            return
        else:
            self.after(self.update_interval, self.update_lines)
    
    def ClearProgressBar(self):
        if not self.ProgressBarActive and self.progressbar:
            self.ProgressBarActive = True

            self.progressbar.config(maximum=1)
            self.progressbar.config(value=0)
    
    def UpdateProgressBar(self):

        if self.ProgressBarActive and self.progressbar:
            self.progressbar.config(maximum=self.filecount)
            if self.progresscount.get() >= self.filecount: # Normal
                self.progressbar.config(value=self.progresscount.get())


            


            




class Compiler():
    def __init__(self, cmd:str, TextWidget: CompileTextWidget, ErrorOverride: tk.StringVar, file_ext = '', game_relative_path:str=None, source_extensions:list = [], callback=None):
        '''
        Defines a program to compile files.
        cmd - name of the tool, the program will retrieve the path automatically
        TextWidget - a textwidget to show the compile data, class of cm.CompileTextWidget
        ErrorOverride - Error override message (tk.StringVar)
        file_ext - input file extension
        game_relative_path - if set it means program only allows input relative to the gameinfo, this is the path that sets it, so for example "resource/"
        source_extensions - Extensions of the source files, needed for game_relative_path
        callback - function that is called when the process finished compiling
        '''
        self.queue = TextWidget.queue
        self.program_path = cmd
        self.widget = TextWidget
        self.ErrorOverride = ErrorOverride
        self.extension = file_ext

        self.Pr_transfer = game_relative_path # Transfer this to the program object
        self.Pr_game = GetGlobal("game_path")
        self.Pr_source_extensions = source_extensions
        self.Callback = callback

    def ChangeProgramPath(self, path):
        '''Change the path for the program that is executed.'''
        self.program_path=path

    def ClearField(self):
        '''Clear the compile window'''
        self.widget.config(state='normal')
        self.widget.delete(1.0, tk.END)
        self.widget.config(state='disabled')

    def Compile(self, inputpath: pl.Path, outputpath: pl.Path, params:list=[], error=False, folder=False):
        print("Compiling!")
        self.widget.stop.clear()
        self.widget.update_lines()
        errorString = self.ErrorOverride.get()
        if error:
            errorString = errorString.splitlines(True)
            for line in errorString:
                self.queue.put(line)
            self.widget.stop.set() # Stop, we appended every error line
            return
        if folder:
            print("Compiling folder!")
            folder_path = inputpath
            print(folder_path)
            print(self.extension)
            file_list = folder_path.rglob('*' + self.extension)
            file_list = list(file_list)
            print(file_list)
            self.filecount = len(file_list) # Set the file count for the progressbar
            self.program = Program(GetPathForTool(self.program_path), self.queue, inputpath, outputpath, self.Pr_game, self.widget.stop, params, folder_mode=True, 
                                   files=file_list, gm_rel_path=self.Pr_transfer, source_extensions=self.Pr_source_extensions, file_counter = self.widget.progresscount, callback=self.Callback)
            
        else:
            file = [    inputpath  ]
            self.widget.filecount = 1
            self.program = Program(GetPathForTool(self.program_path), self.queue, inputpath, outputpath, self.Pr_game, self.widget.stop, params, 
                                   files=file, gm_rel_path=self.Pr_transfer, source_extensions=self.Pr_source_extensions, file_counter = self.widget.progresscount, callback=self.Callback)

        self.program.start() # Start the thread
    
    def Stop(self):
        '''Stops the program.'''
        if self.program.is_alive():
            self.program.stop()

class Program(Thread):
    def __init__(self, cmd, queue, inputpath: pl.Path, outputpath: pl.Path, game: pl.Path, terminate_event: Event, param: list=[], folder_mode = False, files=None, gm_rel_path:pl.Path=None, source_extensions=[], file_counter:tk.IntVar=None, callback=None):
        super().__init__(group=None, name=None, daemon=True)

        self.terminate = terminate_event
        self.queue = queue

        self.process = None

        self.need_to_move_file = Event()
        self.extensions = source_extensions

        # Folder specific logic
        self.folder_mode = folder_mode # Are we compiling a folder?
        self.files:list = files # List of files
        self.cmd = cmd # The executable to run
        self.param = param # Paramaters to run with
        self.game = game # Game directory

        self.inputpath = inputpath
        self.outputpath = outputpath

        self.rel_path = gm_rel_path # Set the non-proper one, the proper one is set below

        self.forceTerminate = Event() # Forces the program to quit with no removing files from the queue
        self.Counter = file_counter
        self.Callback = callback

        if self.rel_path: # It means we are dealing with a program that does not like absolute filepaths (not relative to the GAME directory)
            if self.game.is_dir():
                
                self.rel_path = self.game.joinpath(self.rel_path) # Set the proper relative path

                drive = self.game.drive
                dest = self.game.joinpath(self.rel_path, 'temp_smt_symlinks')
                tempfiles = []
                
            
                for file in self.files:
                    
                    if file.drive != drive:
                        this_path = dest.joinpath(file.name) # for creating the symlink, name it as the file
                        this_path.symlink_to(file) # Create the symlink
                        file = this_path
                    try:
                        file = file.relative_to(self.rel_path) # Return the relative path to the game dir
                    except ValueError: # Paths are not relative, we have to use the legacy os module method that actually does /../
                        filepath = str(file)
                        rel_path = str(self.rel_path)
                        file = pl.Path(os.path.relpath(filepath, rel_path))

                    tempfiles.append(file)
                    
                self.relative_files = tempfiles

            else:
                self.queue.put("\nThe path for gameinfo.txt is incorrect! \nMake sure you enter the correct path in the configuration tab before proceeding!")
                self.forceTerminate.set()


    def run(self):
        print("Starting to transfer lines!")
        if self.process: # Check if we started the process, for folder compiling
            for line in self.process.stdout:
                #print(line)
                if self.forceTerminate.is_set():
                    self.InternalDisable()
                    return
                
                if self.terminate.is_set():
                    self.process.terminate() # Terminate if we asked to
                    self.terminate.clear() # Clear after terminating, used for folder compiling, since we are always creating a new class when compiling a single file
                    break

                self.queue.put(line) # put the line in queue for processing

            self.queue.put('\n[==========NEXT PROCESS==========]\n')

        self.AddToCounter()

        
        # give process a chance to exit gracefully
        print("Stopping!")
        #if not self.folder_mode and self.process: # Ensure the process is running
        #    self.MoveFile()
        #    self.InternalDisable()

        #else:
        self.need_to_move_file.set() # We ended this compile, we need to move it now
        if self.Callback:
                self.Callback()

        if self.CompileNextFile(): # Ended this file, compile next one. If we are starting it will automatically default to this one
            print("Running!")
            self.run() # TO CHECK
        else: # No files left, terminate the line appending and stop compiling

            self.InternalDisable()

        print("Shutting down!")
        return 
    
    def AddToCounter(self):
        if self.Counter:
            if self.process:
                c = self.Counter.get()
                self.Counter.set(c+1)
            else:
                self.Counter.set(0) # Fresh start, clear the progressbar


    def MoveFile(self):
        print("+++++++++++++++++MOVING FILES!")
        org_files = self.files.copy()
        
        IHead, _ = SplitPath(self.inputpath)

        for org_file in org_files:
            print(org_file)
            or_path, or_name = SplitPath(org_file)
            or_name = pl.Path(or_name).stem

            input_rel_path = or_path.relative_to(IHead) # Get the relative path from the inputpath (in file mode it will be the same)

            output_path_r = self.outputpath.joinpath(input_rel_path) # Add the relative input path onto the output path
            
            output_path_r.mkdir(parents=True, exist_ok=True) # Create the dir if it wasn't created

            print(f"+++++++{output_path_r}")
            compiled_files = FindFilesByExtension(or_path, self.extensions, filename=or_name) # Find the compiled files if there are multiple
            for file in compiled_files:
                _, newname = SplitPath(file)

                out_path = output_path_r.joinpath(newname)

                shutil.move(file, out_path)
        

    def InternalDisable(self):
        self.terminate.set()
        try:
            try:
                self.process.wait(timeout=3)
            except TimeoutExpired:
                self.process.kill()
        except AttributeError:
            pass
        

    def CompileNextFile(self):
        if self.need_to_move_file.is_set(): # If we processed a file before, move the file
            self.MoveFile()
            self.need_to_move_file.clear()

        try:
            file:pl.Path = self.relative_files.pop(0)
        except IndexError: # No files left to process
            return False 
        
        file = file.as_posix() # Convert the path to string

        print("PATH FILE AMOGUS " + file)
        self.queue.put(f'[ {file} ]\n\n')
        print("Running compiler " + str([str(self.cmd)] + self.param + [file]))
        self.process =  Popen([str(self.cmd)] + self.param + [file], # Compile the first file
                                 stdout=PIPE,
                                 stderr=STDOUT,
                                 universal_newlines=True)
        return True


    def Stop(self):
        '''Stop the process and stop the line appending in the text widget.'''
        
        print("Stopping by user input!")
        self.terminate.set() # If this was called by run this process is already done
        #Empty the queue
        while True:
            try:
                self.queue.get(block=False)
            except Empty:
                break
            self.queue.task_done()  # Acknowledge line has been processed
    
    def Skip(self):
        self.terminate.set() # This will force the program to terminate current process, and initiate the next file


def FindFilesByExtension(directory:pl.Path, filter:list=[], mode:bool=False, filename:str = ''):
    '''\
        Finds files with the same name, but different extensions
        mode - False -> Blacklist, True -> Whitelist
    '''
    files = []

    if mode:
        for ext in filter:
            files.extend(directory.rglob(filename + ext))
            
    else:
        found_f = directory.rglob(filename + ".*")
        for file in found_f:
            _, ext = os.path.splitext(file) # Get the extension
            if not ext in filter:
                files.append(file)
    
    return files



# Save managment

def LoadJson():
    global jsonData

    
    try:
        file = open(savePath, "r")
        jsonData = json.load(file)
        file.close()
        if not jsonData:
            return False
        return True
    except:
        SplitPath(savePath)[0].mkdir(parents=True, exist_ok=True)
        file = open(savePath, "w")
        jsonData = {}
        file.close()
        return False
    
def SaveData(type, entry, slot, value):
    '''Used to save the data to json'''
    print("Saving data!")
    global jsonData
    if globals()['disable_save']:
        print("Tried to save but disable save is online!")
        return

    try:#Data exists, modify
        #print("Level 0")
        jsonData[type][entry][slot] = value
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

    file = open(savePath, "w")
    json.dump(jsonData, file, indent=4, sort_keys=True, check_circular=False)
    file.close()
    ReloadJson()

def GetData(type: str, name: str = 'none', config: str = 'none'):
    global jsonData
    to_return = {}

    if not jsonData:
        LoadJson()

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
            file = open(savePath, "w")
            json.dump(jsonData, file, indent=4, sort_keys=True, check_circular=False)
            file.close()
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
                file = open(savePath, "w")
                json.dump(jsonData, file, indent=4, sort_keys=True, check_circular=False)
                file.close()
                ReloadJson()

            except KeyError: # If even upper code failed, this means we are missing the whole block
                jsonData[type] = default_settings[type]
                file = open(savePath, "w")
                json.dump(jsonData, file, indent=4, sort_keys=True, check_circular=False)
                file.close()
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
                file = open(savePath, "w")
                json.dump(jsonData, file, indent=4, sort_keys=True, check_circular=False)
                file.close()
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
                    file = open(savePath, "w")
                    json.dump(jsonData, file, indent=4, sort_keys=True, check_circular=False)
                    file.close()
                    ReloadJson()

                except KeyError: #We don't even have the block
                    jsonData[type] = default_settings[type]
                    file = open(savePath, "w")
                    json.dump(jsonData, file, indent=4, sort_keys=True, check_circular=False)
                    file.close()
                    ReloadJson()

        to_return = jsonData[type][name][config]
    #print("To return: " + str(to_return))
    return to_return

def ReloadJson():
    global jsonData
    jsonData = {} #Flush the variable
    LoadJson()

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

def GetPathForTool(tool:str):
    return globals()[tool + "_path"]
