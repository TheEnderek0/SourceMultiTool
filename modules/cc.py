import tkinter as tk
from tkinter import ttk
from . import common_lib as cm
import os

MODULE_PREFIX = 'CaptionCompile-'

ConfigPath = (None, None)

#----------------------------------------#
IOString = (None, None)                  #
#----------------------------------------#

ParameterGUILabel = None # Used internally

input_mode = None # BoolVar set by Init() ->  True - file, False - folder # Used for tracking the input mode
output_mode = None # BoolVar set by Init() -> True - default game dir, False - folder # Used for tracking the output mode


Loaded = False # It's true when we finished loading

Compile = None 
CompileOverrideError = None

#OPTIONS
OVerbose = None
ODLC_st = None
ODLC_val = None
LOG_file = None
LOG_st = None

LOG_PathName = ('', '')

Additional_parameters = None


def Init(container):
    print("Initialising Caption Compile tab")
    
    global ConfigPath

    global IOString

    global input_mode, output_mode

    global CompileOverrideError
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
    ConfigPath = cm.AddConfigPath('captioncompiler', "Caption Compiler")
    
    # Add IO bars
    input_mode = tk.BooleanVar(PathFrame, False)
    output_mode = tk.BooleanVar(PathFrame, False)

    IOString = cm.IObars(PathFrame, input_mode, output_mode, '/resource', MODULE_PREFIX, InputCallback=[UpdateParameters]) # Create standard IO input output bars
    

    cm.GetGlobal('configuration').trace_add('write', lambda a, b, c: LoadFor(cm.GetGlobal('configuration')))


    OptionLabel = ttk.Label(WindowFrame, style = 'ShortInfo.TLabel', text='Options')
    OptionFrame = ttk.Labelframe(WindowFrame, style = 'Big.TLabelframe', labelwidget=OptionLabel, height=100)
    OptionFrame.grid(column=0, row=1, sticky='nsew')
    MainOptionFrame, OptionCanvas = cm.OptionCanvas(OptionFrame)
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
    global Compile
    Compile = cm.CompileWindow(CompileFrame)

    CompileOverrideError = tk.StringVar(container, '', "CAPTION-CompileOverride")

    cm.GetGlobal('GameInfo')[1].trace_add('write', lambda a, b, c: UpdateParameters()) 
    ConfigPath[1].trace_add('write', lambda a, b, c: UpdateParameters())
    IOString[0].trace_add('write', lambda a, b, c: UpdateParameters())
    IOString[1].trace_add('write', lambda a, b, c: UpdateParameters())
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

    DLCSpinbox = ttk.Spinbox(frame, from_=-1, to=99, textvariable=ODLC_val, validate='all', validatecommand=(ValidateC, '%P'), style='Option.TSpinbox')
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
    label.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)
    global ParameterGUILabel
    ParameterGUILabel = label

def UpdateParameters():
    '''This is just to display the parameters in the param window'''
    global CompileOverrideError
    global LOG_PathName

    B = "   "
    par_label = ''

    exe = str(ConfigPath[1].get())
    gameFile = str(cm.GetGlobal('GameInfo')[1].get())
    par_label += exe + B

    
    game, game_success, CompileOverrideErrorString = cm.CheckGameInfo(gameFile)

    CompileOverrideError.set(CompileOverrideError.get() + '\n' + CompileOverrideErrorString)

    par_label += '-game ' + game + B

    if OVerbose.get():
        par_label += '-v' + B


    if game_success: #If determining game was a success, we can determine the DLC now
        dlc_st = cm.DetermineDLC(game, ODLC_st.get(), ODLC_val.get())
        if dlc_st[0]:
            par_label += '-d ' + dlc_st[1] + B
    

    
    if LOG_st.get(): # We are wanting to log
        if cm.CheckPathSyntax(LOG_file.get()):

            LOG_PathName = cm.SplitPath(LOG_file.get())
            B_st = False
            if LOG_PathName[0] != '' or LOG_PathName[1] != '': #Means the field is not empty
                par_label += '-l'
                B_st = True

            if LOG_PathName[1] != '':
                par_label += f' <Rename file to "{LOG_PathName[1]}"> '

            if LOG_PathName[0] != '':
                par_label += f' <Move file to "{LOG_PathName[0]}">'

            if B_st:
                par_label += B

    input_st = cm.CheckInputValidity(IOString[0].get(), '.txt', input_mode.get())
    par_label += input_st[2] + B
    
    outPath = IOString[1].get()
    par_label += f"<Transfer file(s) to {outPath}>" + B

    ParameterGUILabel.configure(text = par_label)
    
        

def LoadFor(stringVar: tk.StringVar):
    
    cm.SetGlobal('disable_save', True)
    current_config = stringVar.get()

    global ODLC_st, OVerbose, ODLC_val, LOG_file, LOG_st

    #App specific loads
    ODLC_st.set(cm.GetData('app', "captioncompile", "auto_dlc"))
    OVerbose.set(cm.GetData('app', "captioncompile", "verbose"))
    ODLC_val.set(cm.GetData('app', "captioncompile", "manual_dlc"))
    LOG_st.set(cm.GetData('app', "captioncompile", "log"))
    LOG_file.set(cm.GetData('app', "captioncompile", "log_path"))

    cm.SetGlobal('disable_save', False)

    global Loaded
    if not Loaded:
        SetupProgram()
        Loaded = True




def ChangeEntryState(entry, state):
    if state:
        entry.config(state='disabled')
    else:
        entry.config(state='normal')

def ValidateSpinbox(valuew):
    if valuew == '' or '-':
        return True
    try:
        value = int(valuew)
    except:
        print('Except')
        return False
    #if valuew != value:
    #    return False
    if value > 99:
        return False
    elif value < -1:
        return False
    else:
        return True
    
def SetupProgram():
    global Compile
    rootWindow = Compile[0]
    canvas = Compile[1]
    compileB = Compile[2]
    stopB = Compile[3]
    nextB = Compile[4]
    clearB = Compile[5]

    TextWid = cm.CompileTextWidget(rootWindow, canvas, scroll=Compile[6])
    CompilerProgram = cm.Compiler(ConfigPath[1].get(), TextWid, CompileOverrideError, file_ext='.txt', game_relative_path='/resource', source_extensions=['.txt'])
    TextWid.pack(fill='both', expand=True)
    compileB.bind("<Button>", lambda e: StartCompile(CompilerProgram))
    stopB.bind("<Button>", lambda e: CompilerProgram.Stop())
    clearB.bind("<Button>", lambda e: CompilerProgram.ClearField())



def StartCompile(Compiler: cm.Compiler):
    print("Start compile!")

    global CompileOverrideError

    CompileOverrideError.set('')
    gameFile = str(cm.GetGlobal('GameInfo')[1].get())
    par = []
    errored = False


    game, game_success, Gerror = cm.CheckGameInfo(gameFile)
    input_success, i_error, _ = cm.CheckInputValidity(IOString[0].get(), '.txt', input_mode.get())

    if game_success:
        par.append('-game')
        par.append(game)
    else:
        CompileOverrideError.set(Gerror)
        errored = True
    
    if game_success:
        dlc_st = cm.DetermineDLC(game, ODLC_st.get(), ODLC_val.get())
        if dlc_st[0]:
            par.append('-d')
            par.append(dlc_st[1])

    if LOG_st.get():
        par.append('-l')


    if input_success: #Must be last!
        par.append(IOString[0].get())
    else:
        CompileOverrideError.set(CompileOverrideError.get() + i_error)
        errored = True

    if Compile[7].get(): # If the automatic clear is online
        Compiler.ClearField() # Clear the field before compile


    Compiler.Compile(params=par, error=errored, folder=not input_mode.get())
    #Compiler.Compile(['-game', f'C:/Program Files (x86)/Steam/steamapps/common/Portal 2/portal2/', "-d", "0", "-l", 'C:/Program Files (x86)/Steam/steamapps/common/Portal 2/portal2/resource/for-compile/amongus.txt'], error=errored)

