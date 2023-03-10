import tkinter as tk
from tkinter import ttk
from . import common_lib as cm
import pathlib as pl

MODULE_PREFIX = 'CaptionCompile-'
TOOL_NAME = 'captioncompiler'
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
ProgressBar = None

def Init(container):
    print("Initialising Caption Compile tab")
    
    global ConfigPath

    global IOString

    global input_mode, output_mode
    global ProgressBar
    global CompileOverrideError
    global Additional_parameters
    # Initialise the main frame
    frame = ttk.Frame(container, style='Card.TFrame')
    frame.grid(column = 0, row = 0, sticky='nsew')
    container.add(frame, text = 'Caption Compile')

    # Initialise the default scheme
    WindowFrame, ProgressBar = cm.ModuleWindow(frame)
    WindowFrame.columnconfigure(index=0, weight=1)
    WindowFrame.rowconfigure(index=0, weight=0) # IO
    WindowFrame.rowconfigure(index=1, weight=0) # Options
    WindowFrame.rowconfigure(index=2, weight=0) # Additional params
    WindowFrame.rowconfigure(index=3, weight=0) # Params
    WindowFrame.rowconfigure(index=4, weight=3) # Compile

    PathFrame = ttk.Frame(WindowFrame)
    PathFrame.grid(column=0, row=0, sticky='nsew')

    # Add a config bar for captioncompiler
    ConfigPath = cm.AddConfigPath(TOOL_NAME, "Caption Compiler")
    
    # Add IO bars
    input_mode = tk.BooleanVar(PathFrame, False)
    output_mode = tk.BooleanVar(PathFrame, False)

    IOString = cm.IObars(PathFrame, input_mode, output_mode, 'resource', MODULE_PREFIX, InputCallback=[UpdateParameters]) # Create standard IO input output bars



    OptionLabel = ttk.Label(WindowFrame, style = 'ShortInfo.TLabel', text='Options')
    OptionFrame = ttk.Labelframe(WindowFrame, style = 'Big.TLabelframe', labelwidget=OptionLabel, height=100)
    OptionFrame.grid(column=0, row=1, sticky='nsew')
    MainOptionFrame, OptionCanvas = cm.OptionCanvas(OptionFrame)
    OptionGUI(MainOptionFrame)


    Additional_parameters = cm.AdditionalParameters(WindowFrame, 0, 2, TOOL_NAME)


    Paramname = ttk.Label(WindowFrame, text="Launch Parameters", style='ShortInfo.TLabel')
    ParamFrame = ttk.Labelframe(WindowFrame, style = 'secondary.TLabelframe', labelwidget=Paramname)
    ParamFrame.grid(column=0, row=3, sticky='nsew')
    ParameterGUI(ParamFrame)


    CFLabel = ttk.Label(WindowFrame, text='Compile', style='ShortInfo.TLabel')
    CompileFrame = ttk.Labelframe(WindowFrame, style='TLabelframe', labelwidget=CFLabel)
    CompileFrame.grid(column=0, row=4, sticky='nsew')
    global Compile
    Compile = cm.CompileWindow(CompileFrame, TOOL_NAME)


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
    Additional_parameters.trace_add('write', lambda a, b, c: UpdateParameters())

    OVerbose.trace_add('write', lambda a, b, c: cm.SaveData('app', TOOL_NAME, 'verbose', OVerbose.get()))
    ODLC_st.trace_add('write', lambda a, b, c: cm.SaveData('app', TOOL_NAME, 'auto_dlc', ODLC_st.get()))
    ODLC_val.trace_add('write', lambda a, b, c: cm.SaveData('app', TOOL_NAME, 'manual_dlc', ODLC_val.get()))
    LOG_st.trace_add('write', lambda a, b, c: cm.SaveData('app', TOOL_NAME, 'log', LOG_st.get()))
    LOG_file.trace_add('write', lambda a, b, c: cm.SaveData('app', TOOL_NAME, 'log_path', LOG_file.get()))



    # AFTER GUI HAS BEEN INITIALISED AND WE HAVE EVERY ELEMENT AVAILABLE:
    cm.AppendLoading(Load) # Append the loading function for this module
    
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
    label = ttk.Label(frame, style='Small.LongInfo.TLabel', justify='left', text='', anchor='nw', wraplength=550)
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

    exe = ConfigPath[1].get()
    gameFile = cm.GetGlobal("game_path")
    par_label += exe + B

    
    game, game_success, CompileOverrideErrorString = cm.CheckGameInfo(gameFile)

    CompileOverrideError.set(CompileOverrideError.get() + '\n' + CompileOverrideErrorString)

    par_label += '-game ' + str(game) + B

    if OVerbose.get():
        par_label += '-v' + B


    if game_success: #If determining game was a success, we can determine the DLC now
        dlc_st = cm.DetermineDLC(game, ODLC_st.get(), ODLC_val.get())
        if dlc_st[0]:
            par_label += '-d ' + dlc_st[1] + B
    

    
    if LOG_st.get(): # We are wanting to log
        

        LOG_PathName = cm.SplitPath(pl.Path(LOG_file.get()))
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
    
    par_label += Additional_parameters.get() + B

    input_st = cm.CheckInputValidity(pl.Path(IOString[0].get()), '.txt', input_mode.get())
    par_label += str(input_st[2]) + B
    
    outPath = IOString[1].get()
    par_label += f"<Transfer file(s) to {outPath}>" + B

    ParameterGUILabel.configure(text = par_label)
    
        

def Load():
    global ODLC_st, OVerbose, ODLC_val, LOG_file, LOG_st
    #App specific loads


    ODLC_st.set(cm.GetData('app', TOOL_NAME, "auto_dlc"))
    OVerbose.set(cm.GetData('app', TOOL_NAME, "verbose"))
    ODLC_val.set(cm.GetData('app', TOOL_NAME, "manual_dlc"))
    LOG_st.set(cm.GetData('app', TOOL_NAME, "log"))
    LOG_file.set(cm.GetData('app', TOOL_NAME, "log_path"))

    SetupProgram()




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
    compileB = Compile[1]
    stopB = Compile[2]
    nextB = Compile[3]
    clearB = Compile[4]

    TextWid = cm.CompileTextWidget(rootWindow, yscrollbar = Compile[7][0], xscrollbar = Compile[7][1], scroll=Compile[5], progressbar=ProgressBar)
    CompilerProgram = cm.Compiler(TOOL_NAME, TextWid, CompileOverrideError, file_ext='.txt', game_relative_path='resource', source_extensions=['.txt'], callback=MoveLog)
    TextWid.pack(fill='both', expand=True)
    compileB.bind("<Button>", lambda e: StartCompile(CompilerProgram))
    stopB.bind("<Button>", lambda e: CompilerProgram.Stop())
    clearB.bind("<Button>", lambda e: CompilerProgram.ClearField())



def StartCompile(Compiler: cm.Compiler):
    print("Start compile!")

    global CompileOverrideError

    CompileOverrideError.set('')
    gameFile = cm.GetGlobal("game_path")
    par = []
    errored = False


    game, game_success, Gerror = cm.CheckGameInfo(gameFile)
    input_success, i_error, _ = cm.CheckInputValidity(pl.Path(IOString[0].get()), '.txt', input_mode.get())

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

    if OVerbose.get():
        par.append('-v')

    if not input_success:
        CompileOverrideError.set(CompileOverrideError.get() + i_error)
        errored = True

    par.append(Additional_parameters.get()) # Append the additional params

    if Compile[6].get(): # If the automatic clear is online
        Compiler.ClearField() # Clear the field before compile



    Compiler.Compile(pl.Path(IOString[0].get()), pl.Path(IOString[1].get()), params=par, error=errored, folder=not input_mode.get())

def MoveLog(): # This will be run after the process, in a sepearate thread
    log_path = pl.Path(LOG_file.get())  # We are only reading the value here, should be thread-safe
    log_st = LOG_st.get()

    
    LOG_ORIGINAL = 'log.txt' # Original name of the log file

    if log_st:
        or_path = pl.Path("").joinpath(LOG_ORIGINAL)
        try:
            with open(or_path) as log:
                c_log = log.read()
                log.close()
        except FileNotFoundError:
            return
        
        
        cm.SplitPath(log_path)[0].mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a') as save_dir:
            save_dir.write(c_log + "\n")
            or_path.unlink(missing_ok=True)
            save_dir.close()