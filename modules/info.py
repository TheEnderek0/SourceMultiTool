import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image 
from . import common_lib as cm
import webbrowser


ghImageFile = False
ghpath = './img/GitHub.png'
ghOpImg = Image.open(ghpath)

default_font = 'Arial'

def Init(container):
    print("Initialising info tab")
    global ghImageFile
    ghImageFile = ResizePicture(ghOpImg, (100, 100))

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
    inFrame = ttk.Frame(container)
    inFrame.grid(column=0, row=0, sticky="nsew")

    inLabel = ttk.Label(inFrame, 
        text = "Amogus amogus amogus amogus amogus amogus amogus Amogus amogus amogus amogus amogus amogus amogus Amogus amogus amogus amogus amogus amogus amogus Amogus amogus amogus amogus amogus amogus amogus",
        wraplength = 300,
        justify = 'center',
        style="BW.TLabel",
        font = (default_font, 15)
        )
    inLabel.pack(fill = 'both', expand = True)
    inFrame.bind('<Configure>', lambda e: ResizeWrapLenght(inLabel, inFrame.winfo_width()))

def GitHubIcon(container):

    ghFrame = ttk.Frame(container)
    ghFrame.grid(column=2, row=0, sticky='nsew')
    ghFrame.columnconfigure(index=0, weight=1)
    ghFrame.rowconfigure(index = 0, weight=1)

    global ghImageFile
    ghButton = ttk.Button(ghFrame,
        image = ghImageFile
        )
    ghButton.grid(column=0, row=0, sticky="nsew")

    #print("Height = " + str(ghButton.winfo_height()))
    #print("Width = " + str(ghButton.winfo_width()))
    ghFrame.grid_propagate(False)
    ghFrame.bind('<Configure>', lambda e: ResizeGhImage(ghButton))
    ghButton.bind('<Button>', lambda e: webbrowser.open(url='https://github.com/TheEnderek0/SourceMultiTool', new=2))


def ResizeGhImage(cont):
    global ghImageFile
    #print("Resizing image!")
    #print("Height = " + str(cont.winfo_height()))
    #print("Width = " + str(cont.winfo_width()))
    width, height = cm.MaximumScale(ghOpImg, (cont.winfo_width(), cont.winfo_height()))
    #print("Resized width = " + str(width))
    #print("Resized height = " + str(height))
    ghImageFile = ResizePicture(ghOpImg, (width - 20, height - 20))
    cont.config(image = ghImageFile)

    

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

def ResizePicture(pic, size: tuple):
    return ImageTk.PhotoImage(pic.resize(size, Image.ANTIALIAS))

def ResizeWrapLenght(ent, lenght: int):
    print("Wrap lenght = " + str(lenght))
    print(ent)
    if 200 > lenght > 120:
        ent.config(wraplength = lenght)
    elif lenght > 200:
        ent.config(wraplenght = 200)
    else:
        ent.config(wraplenght = 120)

