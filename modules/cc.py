import tkinter as tk
from tkinter import ttk
from . import common_lib as cm


def Init(container):
    print("Initialising Caption Compile tab")

    frame = ttk.Frame(container)
    frame.pack(fill = 'both', expand = True)
    container.add(frame, text = 'Caption Compile')
    