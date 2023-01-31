import tkinter as tk
from tkinter import ttk

N = tk.N
S = tk.S
E = tk.E
W = tk.W

ghImageFile = False
ghpath = './img/GitHub.png'

def Init(container):
    print("Initialising info tab")
    global ghImageFile
    ghImageFile = tk.PhotoImage(file=ghpath)

    frame = ttk.Frame(container)
    frame.grid(column=0, row=0, sticky="nsew")
    container.add(frame, text = 'Info')

    ConfigureCR(frame)
    InfoFrame(frame)
    GitHubIcon(frame)
    CreateTestButton(1, 0, frame)
    CreateTestButton(1, 1, frame)
    CreateTestButton(2, 0, frame)
    CreateTestButton(2, 1, frame)


def InfoFrame(container):
    inFrame = ttk.Frame(container, width=100)
    inFrame.grid(column=0, row=0, sticky="nsew")

    inLabel = ttk.Label(inFrame, 
        text = "Test!wdas dsaawdsadaswdasdaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        wraplength = inFrame.winfo_width(),
        justify = 'center',
        style="BW.TLabel"
        )
    inLabel.pack(fill = 'both', expand = True)
    inFrame.bind('<Configure>', lambda e: inLabel.config(wraplength=inFrame.winfo_width()))

def GitHubIcon(container):
    global ghImageFile
    ghFrame = ttk.Frame(container)
    ghFrame.grid(column=2, row=0, sticky="nsew")

    ghImage = ttk.Label(ghFrame,
        image = ghImageFile,
        #text = "Test amogus goose lol lmao s",
        justify = 'center'
    )

    ghImage.pack(fill = 'both', expand = True)
    ghFrame.bind('<Configure>', ResizeImage(ghFrame, ghImage, ghpath))

def ResizeImage(parent, element, imgPath):
    print("Resizing image!")
    print("Height = " + str(parent.winfo_height()))
    print("Width = " + str(parent.winfo_width()))

    element.configure(image = tk.PhotoImage(imgPath, height = parent.winfo_height(), width=parent.winfo_width()))

def CreateTestButton(row1, column1, container):
    button = tk.Button(container)
    button.grid(column=column1, row=row1, sticky="nsew")


def ConfigureCR(frame):
    frame.columnconfigure(index=0, weight=1)
    frame.columnconfigure(index=1, weight=2)
    frame.columnconfigure(index=2, weight=3)
    frame.rowconfigure(index=0, weight=1)
    frame.rowconfigure(index=1, weight=2)
    frame.rowconfigure(index=2, weight=3)