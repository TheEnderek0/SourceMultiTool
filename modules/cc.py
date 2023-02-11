import tkinter as tk
from tkinter import ttk
from . import common_lib as cm
import os

MODULE_PREFIX = 'CaptionCompile-'

EntryBox, EntryVar = None, None
extension = '',
outputstate = False # True - defaultgame dir, False - userdir

InputString, OutputString = None, None
ExtensionSelectorOne, ExtensionSelectorTwo = None, None
InputEntryBox, OutputEntryBox = None, None

current_config = ''
ParameterGUILabel = None
InputMode = False #True - file, False - folder

#OPTIONS
OVerbose = None
ODLC_st = None
ODLC_val = None
LOG_file = None
LOG_st = None
Additional_parameters = None


def Init(container):
    global EntryBox, EntryVar
    print("Initialising Caption Compile tab")
    global InputString, OutputString
    global ExtensionSelectorOne, ExtensionSelectorTwo
    global InputEntryBox, OutputEntryBox
    # Initialise the main frame
    frame = ttk.Frame(container, style='Card.TFrame')
    frame.grid(column = 0, row = 0, sticky='nsew')
    container.add(frame, text = 'Caption Compile')

    # Initialise the default scheme
    WindowFrame, ProgressBar = cm.ModuleWindow(frame)
    WindowFrame.columnconfigure(index=0, weight=1)
    WindowFrame.rowconfigure(index=0, weight=0) # IO
    WindowFrame.rowconfigure(index=1, weight=5) # Options
    WindowFrame.rowconfigure(index=2, weight=0) # Additional params
    WindowFrame.rowconfigure(index=3, weight=0) # Params
    WindowFrame.rowconfigure(index=4, weight=3) # Compile

    PathFrame = ttk.Frame(WindowFrame)
    PathFrame.grid(column=0, row=0, sticky='nsew')
    # Add a config bar for captioncompiler
    EntryBox, EntryVar = cm.AddConfigPath('captioncompiler', "Caption Compiler")
    
    InputString, OutputString, ExtensionSelectorOne, ExtensionSelectorTwo, ISelectButton, InputEntryBox, OutputEntryBox = cm.IObars(PathFrame)

    ExtensionSelectorOne.bind("<<ComboboxSelected>>", lambda e: ChangeExtension(ExtensionSelectorOne.get(), '.txt'))
    ISelectButton.bind('<Button>', lambda e: cm.SetPath(InputEntryBox, [("", extension)]))
    ExtensionSelectorTwo.bind("<<ComboboxSelected>>", lambda e: SelectorTwo(OutputEntryBox, OutputString, ExtensionSelectorTwo.get()))
    cm.GetGlobal('GameInfo')[1].trace_add('write', lambda a, b, c: SelectorTwo(OutputEntryBox, OutputString, ExtensionSelectorTwo.get())) # We need to trace if user changes gameinfo

    ExtensionSelectorOne.bind("<<ComboboxSelected>>", lambda e: cm.SaveData("cfg", current_config, MODULE_PREFIX+"InputMode", ExtensionSelectorOne.get()))
    ExtensionSelectorTwo.bind("<<ComboboxSelected>>", lambda e: cm.SaveData("cfg", current_config, MODULE_PREFIX+"OutputMode", ExtensionSelectorTwo.get()), add=True)
    InputString.trace_add('write', lambda a, b, c: cm.SaveData('cfg', current_config, MODULE_PREFIX+'Input', InputString.get()))
    OutputString.trace_add('write', lambda a, b, c: cm.SaveData('cfg', current_config, MODULE_PREFIX+'Output', OutputString.get()))
    cm.GetGlobal('configuration').trace_add('write', lambda a, b, c: LoadFor(cm.GetGlobal('configuration')))

    OptionLabel = ttk.Label(WindowFrame, style = 'ShortInfo.TLabel', text='Options')

    OptionFrame = ttk.Labelframe(WindowFrame, style = 'Big.TLabelframe', labelwidget=OptionLabel, height=100)
    OptionFrame.grid(column=0, row=1, sticky='nsew')

    MainOptionFrame = cm.OptionCanvas(OptionFrame)
    OptionGUI(MainOptionFrame)

    POLabel = ttk.Label(WindowFrame, text='Additional parameters:', style='ShortInfo.TLabel')
    ParamOverrideFrame = ttk.Labelframe(WindowFrame, style='TLabelframe', labelwidget=POLabel)
    ParamOverrideFrame.grid(column=0, row=2, sticky='nsew',pady=20)
    ParamOverrideFrame.columnconfigure(index=0, weight=1)
    ParamOverrideFrame.rowconfigure(index=1, weight=1)

    Entry = ttk.Entry(ParamOverrideFrame, style='Other.TEntry')
    Entry.config(font=cm.AddFontTraces(Entry))

    Entry.grid(column=0,row=1, sticky='nsew', padx=5, pady=5)

    Paramname = ttk.Label(WindowFrame, text="Launch Parameters", style='ShortInfo.TLabel')
    ParamFrame = ttk.Labelframe(WindowFrame, style = 'secondary.TLabelframe', labelwidget=Paramname)
    ParamFrame.grid(column=0, row=3, sticky='nsew')
    ParameterGUI(ParamFrame)

    CFLabel = ttk.Label(WindowFrame, text='Compile', style='ShortInfo.TLabel')
    CompileFrame = ttk.Labelframe(WindowFrame, style='TLabelframe', labelwidget=CFLabel)
    CompileFrame.grid(column=0, row=4, sticky='nsew')

    cm.CompileWindow(CompileFrame)

    EntryVar.trace_add('write', lambda a, b, c: UpdateParameters())
    InputString.trace_add('write', lambda a, b, c: UpdateParameters())
    OutputString.trace_add('write', lambda a, b, c: UpdateParameters())
    OVerbose.trace_add('write', lambda a, b, c: UpdateParameters())
    ODLC_st.trace_add('write', lambda a, b, c: UpdateParameters())
    ODLC_val.trace_add('write', lambda a, b, c: UpdateParameters())
    LOG_file.trace_add('write', lambda a, b, c: UpdateParameters())
    LOG_st.trace_add('write', lambda a, b, c: UpdateParameters())

    OVerbose.trace_add('write', lambda a, b, c: cm.SaveData('app', 'captioncompile', 'verbose', OVerbose.get()))
    ODLC_st.trace_add('write', lambda a, b, c: cm.SaveData('app', 'captioncompile', 'auto_dlc', ODLC_st.get()))
    ODLC_val.trace_add('write', lambda a, b, c: cm.SaveData('app', 'captioncompile', 'manual_dlc', ODLC_val.get()))
    LOG_st.trace_add('write', lambda a, b, c: cm.SaveData('app', 'captioncompile', 'log', LOG_st.get()))
    LOG_file.trace_add('write', lambda a, b, c: cm.SaveData('app', 'captioncompile', 'log_path', LOG_file.get()))
    
def OptionGUI(frame: ttk.Frame):

    global OVerbose, ODLC_st, ODLC_val, LOG_file, LOG_st

    frame.columnconfigure(index = 0, weight = 0)
    frame.columnconfigure(index = 1, weight = 1)
    
    frame.rowconfigure(index = 0, weight = 0)

    OVerbose = tk.BooleanVar(frame)
    ODLC_st = tk.BooleanVar(frame)
    ODLC_val = tk.IntVar(frame)
    LOG_st = tk.BooleanVar(frame)
    LOG_file = tk.StringVar(frame)

    Verbose = ttk.Checkbutton(frame, text='Verbose', style='Option.info.TCheckbutton', onvalue=True, offvalue=False, variable=OVerbose)
    Verbose.grid(column=0, row=0, sticky='ew', pady=10)

    VerboseLabel = ttk.Label(frame, style='LongInfo.TLabel', justify='left', anchor='w', padding=(20, 0, 0, 0),
                             text='Print out more data about the compile.'
                             )
    VerboseLabel.grid(column=1, row=0, sticky='ew')
    frame.bind('<Configure>', lambda e: cm.ResizeWrapLength(VerboseLabel, frame.winfo_width(), 1200, 120, endmultiplier=1.5))

    frame.rowconfigure(index=1, weight=0)

    DLc = ttk.Checkbutton(frame, text='Automatic DLC', style='Option.info.TCheckbutton', onvalue=True, offvalue=False, variable=ODLC_st)
    DLCLabel = ttk.Label(frame, style='LongInfo.TLabel', justify='left', anchor='w', padding=(20, 0, 0, 0),
                         text = 'Automatically pass the highest dlc level that this game has. You can disable this and set the dlc level yourself below:'
                         )
    frame.bind('<Configure>', lambda e: cm.ResizeWrapLength(DLCLabel, frame.winfo_width(), 1200, 120, 0.7))
    DLc.grid(column=0, row=1, sticky='ew', pady=10)
    DLCLabel.grid(column=1, row=1, sticky='ew')

    frame.rowconfigure(index=2, weight=0)

    ValidateC = frame.register(ValidateSpinbox)

    DLCSpinbox = ttk.Spinbox(frame, from_=0, to=255, textvariable=ODLC_val, validate='all', validatecommand=(ValidateC, '%P'), style='Option.TSpinbox')
    DLCSpinbox.grid(column=1, row=2, sticky='w', padx=20)
    ODLC_st.trace_add('write', lambda a, b, c: ChangeEntryState(DLCSpinbox, ODLC_st.get()))

    frame.rowconfigure(index=3, weight=0)

    LOGButton = ttk.Checkbutton(frame, text='Log To File', style='Option.info.TCheckbutton', onvalue=True, offvalue=False, variable=LOG_st)
    LOGButton.grid(column=0, row=3, sticky='ew', pady=10)

    LogLabel = ttk.Label(frame, style='LongInfo.TLabel', justify='left', anchor='w', padding=(20, 0, 0, 0),
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

    LogFilePathEntry = ttk.Entry(LogFileFrame, style="Path.TEntry", textvariable=LOG_file)
    LogFilePathEntry.grid(column=0,row=0,sticky='ew')

    Select, Goto = cm.AppendButtons(LogFileFrame)
    Select.grid(column=1,row=0,sticky='ew', padx=5)
    Goto.grid(column=2,row=0,sticky='ew')

    Select.bind("<Button>", lambda e: cm.SetPath(LogFilePathEntry, [("Text file", ".txt .log")]))
    Goto.bind("<Button>", lambda e: cm.Goto(LogFilePathEntry.get(),select=True))
    LOG_st.trace_add('write', lambda a, b, c: ChangeEntryState(LogFilePathEntry, not LOG_st.get()))


def ParameterGUI(frame):
    label = ttk.Label(frame, style='Small.LongInfo.TLabel', justify='left', text='', anchor='nw')
    frame.bind('<Configure>', lambda e: cm.ResizeWrapLength(label, frame.winfo_width(), max=1200, endmultiplier=1))
    frame.columnconfigure(index=0, weight=1)
    frame.rowconfigure(index=0, weight=1)
    label.grid(column=0, row=0, sticky='nsew', padx=10)
    global ParameterGUILabel
    ParameterGUILabel = label

def UpdateParameters():
    '''This is just to display the parameters in the param window'''
    exe = str(EntryVar.get())
    game = str(cm.GetGlobal('GameInfo')[1].get())
    dlc = ''
    log = ''
    
    completePar = f"{exe}    -g {game}   "

    if OVerbose.get():
        completePar += "-v \n"

    if not ODLC_st.get():
        dlc = str(ODLC_val.get())
    else:
        dlc = str(cm.GetHighestDLC())
    if dlc != '-1':
        completePar += f"-d {dlc}   "


    if LOG_st.get():
        head, log = os.path.split(LOG_file.get())
        completePar += f'-log {log} (And transfer to "{head}")  '

    input = InputString.get()

    if InputMode:
        completePar += input + "    "
    else:
        completePar += f"(Recursively do this for every file in {input})    "
    
    outPath = OutputString.get()

    completePar += f"(Transfer file to {outPath})   "

    ParameterGUILabel.configure(text = completePar)
    
 
def ChangeExtension(state: str, exten):
    global extension, InputMode
    if 'File' in state:
        extension = exten
        InputMode = True
    else:
        extension = 'folder'
        InputMode = False
    print(extension)

def SelectorTwo(entry: ttk.Entry, string:tk.StringVar, state: str):
    global outputstate
    outputstate = "Default" in state
    print("Selector two with state " + str(outputstate))
    if outputstate:
        print("Something something")
        gameinfo = cm.GetGlobal('GameInfo')[1].get()
        head, tail = os.path.split(gameinfo)
        string.set(head + '/resource')
        entry.configure(state="disabled")
    else:
        entry.configure(state="normal")
    cm.CheckPathValidity(entry, state='folder')
        
 
def LoadFor(stringVar: tk.StringVar):
    
    cm.SetGlobal('disable_save', True)
    global current_config
    current_config = stringVar.get()

    global ODLC_st, OVerbose, ODLC_val, LOG_file, LOG_st

    ExtensionSelectorOne.set(cm.GetData('cfg', current_config, MODULE_PREFIX+"InputMode"))
    ExtensionSelectorTwo.set(cm.GetData('cfg', current_config, MODULE_PREFIX+"OutputMode"))

    InputEntryBox.delete(0, tk.END)
    InputEntryBox.insert(0, cm.GetData('cfg', current_config, MODULE_PREFIX+"Input"))

    OutputEntryBox.delete(0, tk.END)
    OutputEntryBox.insert(0, cm.GetData('cfg', current_config, MODULE_PREFIX+"Output"))

    #App specific loads
    ODLC_st.set(cm.GetData('app', "captioncompile", "auto_dlc"))
    OVerbose.set(cm.GetData('app', "captioncompile", "verbose"))
    ODLC_val.set(cm.GetData('app', "captioncompile", "manual_dlc"))
    LOG_st.set(cm.GetData('app', "captioncompile", "log"))
    LOG_file.set(cm.GetData('app', "captioncompile", "log_path"))
    ChangeExtension(ExtensionSelectorOne.get(), '.txt')
    print("EXTENSION " + extension)
    SelectorTwo(OutputEntryBox, OutputString, ExtensionSelectorTwo.get())

    cm.SetGlobal('disable_save', False)




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