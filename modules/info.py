import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image 
from . import common_lib as cm
import webbrowser


INFO_MESSAGE = ("Source MultiTool is an open-source software developed by Enderek0, available on GitHub. \n\n" + 
                "It's designed to make compiling various files easier, having an user interface and more. \n\n" +
                "Tutorial on usage is available on the wiki!")







GHPATH = './img/GitHub.png'
ghOPIMG = Image.open(GHPATH)
WIKPATH = './img/wiki.png'
wikOPIMG = Image.open(WIKPATH)

GITHUB_URL = 'https://github.com/TheEnderek0/SourceMultiTool'
WIKI_URL = 'https://github.com/TheEnderek0/SourceMultiTool/wiki'

default_font = 'Arial'

def Init(container):
    print("Initialising info tab")


    frame = ttk.Frame(container)
    frame.grid(column=0, row=0, sticky="nsew")
    container.add(frame, text = 'Info')

    ConfigureCR(frame)
    InfoFrame(frame)
    GitHubIcon(frame)
    WikiButton(frame)


def InfoFrame(container):
    inFrame = ttk.Frame(container, padding=(50, 50, 15, 15))
    inFrame.grid(column=0, row=0, sticky="nsew")

    inLabel = ttk.Label(inFrame, 
        text = INFO_MESSAGE,
        wraplength = 300,
        anchor='c',
        justify = 'center',
        style="BW.TLabel",
        font = (default_font, 15),
        border=5,
        relief='groove'
        )
    inLabel.pack(fill = 'both', expand = True)
    inFrame.bind('<Configure>', lambda e: cm.ResizeWrapLength(inLabel, inFrame.winfo_width(), 400, 120, 0.7))

def GitHubIcon(container):

    ghFrame = ttk.Frame(container, padding = (100, 100, 100, 100))
    ghFrame.grid(column=2, row=0, sticky='nsew')
    ghFrame.columnconfigure(index=0, weight=1)
    ghFrame.rowconfigure(index = 0, weight=1)

    ghButton = ttk.Button(ghFrame)
    ghButton.grid(column=0, row=0, sticky="nsew")

    ghFrame.grid_propagate(False)
    ghFrame.bind('<Configure>', lambda e: cm.ApplyResizeImage(ghButton, ghOPIMG, "ghImageFile"))
    ghButton.bind('<Button>', lambda e: webbrowser.open(url=GITHUB_URL, new=2))

def WikiButton(container):

    wikiFrame = ttk.Frame(container, padding = (50, 50, 50, 50))
    wikiFrame.grid(column=2, row=1, sticky='nsew')
    wikiFrame.columnconfigure(index = 0, weight = 1)
    wikiFrame.rowconfigure(index = 0, weight = 1)
    wikiFrame.grid_propagate(False)

    wikiButton = ttk.Button(wikiFrame)
    wikiButton.grid(column=0, row=0, sticky='nsew')

    wikiFrame.bind('<Configure>', lambda e: cm.ApplyResizeImage(wikiButton, wikOPIMG, "wikiImageFile"))
    wikiButton.bind('<Button>', lambda e: webbrowser.open(url=WIKI_URL, new=2))



def CreateTestButton(row1, column1, container):
    button = tk.Button(container)
    button.grid(column=column1, row=row1, sticky="nsew")


def ConfigureCR(frame):
    frame.columnconfigure(index=0, weight=1)
    frame.columnconfigure(index=1, weight=2)
    frame.columnconfigure(index=2, weight=3)
    frame.rowconfigure(index=0, weight=1)
    frame.rowconfigure(index=1, weight=1)

def SaveDefault():
    pass

def Load(firstLoad = False):
    pass