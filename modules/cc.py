import tkinter as tk
from tkinter import ttk
from . import common_lib as cm
import os

MODULE_PREFIX = 'CaptionCompile-'

EntryBox, EntryVar = None, None
extension = '',
outputstate = False # True - defaultgame dir, False - userdir

InputString, OutputString = None, None

current_config = ''

ParameterGUILabel = None

#OPTIONS
OVerbose = None
ODLC_st = None
ODLC_val = None
LOG_file = None
LOG_st = None

def Init(container):
    global EntryBox, EntryVar
    print("Initialising Caption Compile tab")
    global InputString, OutputString
    # Initialise the main frame
    frame = ttk.Frame(container)
    frame.grid(column = 0, row = 0, sticky='nsew')
    container.add(frame, text = 'Caption Compile')

    # Initialise the default scheme
    WindowFrame, ErrorLabel = cm.ModuleWindow(frame)
    WindowFrame.columnconfigure(index=0, weight=1)
    WindowFrame.rowconfigure(index=0, weight=0)
    WindowFrame.rowconfigure(index=1, weight=2)
    WindowFrame.rowconfigure(index=2, weight=1)

    PathFrame = ttk.Frame(WindowFrame)
    PathFrame.grid(column=0, row=0, sticky='nsew')
    # Add a config bar for captioncompiler
    EntryBox, EntryVar = cm.AddConfigPath('captioncompiler', "Caption Compiler")
    
    InputString, OutputString, ExtensionSelectorOne, ExtensionSelectorTwo, ISelectButton, InputEntryBox, OutputEntryBox = cm.IObars(PathFrame)

    ExtensionSelectorOne.bind("<<ComboboxSelected>>", lambda e: ChangeExtension(ExtensionSelectorOne.get(), '.txt'))
    ISelectButton.bind('<Button>', lambda e: cm.SetPath(InputEntryBox, [("", extension)]))
    ExtensionSelectorTwo.bind("<<ComboboxSelected>>", lambda e: SelectorTwo(OutputEntryBox, ExtensionSelectorTwo.get()))

    cm.GetGlobal('configuration').trace_add('write', lambda a, b, c: LoadFor(cm.GetGlobal('configuration')))

    OptionFrame = ttk.Frame(WindowFrame)
    OptionFrame.grid(column=0, row=1, sticky='nsew')

    MainOptionFrame = cm.OptionCanvas(OptionFrame)
    OptionGUI(MainOptionFrame)

    ParamFrame = ttk.Frame(WindowFrame)
    ParamFrame.grid(column=0, row=2, sticky='nsew')
    ParameterGUI(ParamFrame)

    
def OptionGUI(frame: ttk.Frame):

    global OVerbose, ODLC_st, ODLC_val, LOG_file

    frame.columnconfigure(index = 0, weight = 0)
    frame.columnconfigure(index = 1, weight = 1)
    
    frame.rowconfigure(index = 0, weight = 0)

    OVerbose = tk.BooleanVar(frame)
    ODLC_st = tk.BooleanVar(frame)
    ODLC_val = tk.IntVar(frame)
    LOG_st = tk.BooleanVar(frame)
    LOG_file = tk.StringVar(frame)

    Verbose = ttk.Checkbutton(frame, text='Verbose', style='OPTIONS.TCheckbutton', onvalue=True, offvalue=False, variable=OVerbose)
    Verbose.grid(column=0, row=0, sticky='ew', pady=10)

    VerboseLabel = ttk.Label(frame, font=cm.GetGlobal('font'), justify='left', anchor='w', padding=(20, 0, 0, 0),
                             text='Print out more logs and data about the compile.'
                             )
    VerboseLabel.grid(column=1, row=0, sticky='ew')
    frame.bind('<Configure>', lambda e: cm.ResizeWrapLength(VerboseLabel, frame.winfo_width(), 1200, 120, 0.7))

    frame.rowconfigure(index=1, weight=0)

    DLc = ttk.Checkbutton(frame, text='Automatic DLC', style='OPTIONS.TCheckbutton', onvalue=True, offvalue=False, variable=ODLC_st)
    DLCLabel = ttk.Label(frame, font=cm.GetGlobal('font'), justify='left', anchor='w', padding=(20, 0, 0, 0),
                         text = 'Automatically pass the highest dlc level that this game has. You can disable this and set the dlc level yourself below:'
                         )
    frame.bind('<Configure>', lambda e: cm.ResizeWrapLength(DLCLabel, frame.winfo_width(), 1200, 120, 0.7))
    DLc.grid(column=0, row=1, sticky='ew', pady=10)
    DLCLabel.grid(column=1, row=1, sticky='ew')

    frame.rowconfigure(index=2, weight=0)

    ValidateC = frame.register(ValidateSpinbox)

    DLCSpinbox = ttk.Spinbox(frame, from_=0, to=255, textvariable=ODLC_val, validate='all', validatecommand=(ValidateC, '%P'))
    DLCSpinbox.grid(column=1, row=2, sticky='w', padx=20)
    ODLC_st.trace_add('write', lambda a, b, c: ChangeEntryState(DLCSpinbox, ODLC_st.get()))

    frame.rowconfigure(index=3, weight=0)

    LOGButton = ttk.Checkbutton(frame, text='Log To File', style='OPTIONS.TCheckbutton', onvalue=True, offvalue=False, variable=LOG_st)
    LOGButton.grid(column=0, row=3, sticky='ew', pady=10)

    LogLabel = ttk.Label(frame, font=cm.GetGlobal('font'), justify='left', anchor='w', padding=(20, 0, 0, 0),
                         text = "Log output to a file, set the path and the filename below. You can specify a new path, the file will be created."
                         )
    LogLabel.grid(column=1, row=3, sticky='ew')
    frame.bind('<Configure>', lambda e: cm.ResizeWrapLength(LogLabel, frame.winfo_width(), 1200, 120, 0.7))
    frame.rowconfigure(index=4, weight=0)

    LogFileFrame = ttk.Frame(frame)
    LogFileFrame.grid(column=1, row=4, sticky='ew', padx=20)
    LogFileFrame.columnconfigure(index=0, weight=1)
    LogFileFrame.columnconfigure(index=1, weight=0)
    LogFileFrame.columnconfigure(index=2, weight=0)
    LogFileFrame.rowconfigure(index=0,weight=1)

    LogFilePathEntry = ttk.Entry(LogFileFrame, style="CFG.TEntry", textvariable=LOG_file)
    LogFilePathEntry.grid(column=0,row=0,sticky='ew')

    Select, Goto = cm.AppendButtons(LogFileFrame)
    Select.grid(column=1,row=0,sticky='ew')
    Goto.grid(column=2,row=0,sticky='ew')

    Select.bind("<Button>", lambda e: cm.SetPath(LogFilePathEntry, [("Text file", ".txt .log")]))
    Goto.bind("<Button>", lambda e: cm.Goto(LogFilePathEntry.get(),select=True))
    LOG_st.trace_add('write', lambda a, b, c: ChangeEntryState(LogFilePathEntry, not LOG_st.get()))

def ParameterGUI(frame: ttk.Frame):
    name = ttk.Label(frame, text="Launch parameters:", style='NL.TLabel', justify='left', anchor='w')

    secondaryFrame = ttk.Frame(frame, style='Param.TFrame', borderwidth=5, relief='groove')

    label = ttk.Label(secondaryFrame, style='Param.TLabel', justify='left', text='')


    frame.columnconfigure(index=0, weight=1)
    frame.rowconfigure(index=0, weight=0)
    frame.rowconfigure(index=1, weight=1)
    secondaryFrame.columnconfigure(index=0, weight=1)
    secondaryFrame.rowconfigure(index=0, weight=1)
    secondaryFrame.grid(column=0,row=1,sticky='nsew')
    name.grid(column=0, row=0, sticky='nsew')
    label.grid(column=0, row=0, sticky='nsew')

    global ParameterGUILabel
    ParameterGUILabel = label


def ChangeExtension(state: str, exten):
    global extension
    if 'File' in state:
        extension = exten
    else:
        extension = 'folder'
    print(extension)

def SelectorTwo(entry: ttk.Entry, state: str):
    global outputstate
    outputstate = "Default" in state

    if outputstate:
        gameinfo = cm.GetGlobal('GameInfo')[1].get()
        head, tail = os.path.split(gameinfo)
        entry.delete(0, tk.END) # Clear the field
        entry.insert(0, head + '/resource') # Insert the saved setting/path
        entry.configure(state="disabled")
    else:
        entry.configure(state="normal")
        
 
def LoadFor(stringVar: tk.StringVar):
    global current_config
    current_config = stringVar.get()

def ChangeEntryState(entry, state):
    if state:
        entry.config(state='disabled')
    else:
        entry.config(state='normal')

def ValidateSpinbox(valuew):
    if valuew == '':
        return True
    try:
        value = int(valuew)
    except:
        print('Except')
        return False
    #if valuew != value:
    #    return False
    if value > 255:
        return False
    elif value < 0:
        return False
    else:
        return True