import tkinter as tk


def Init(container):
    print("Initialising Caption Compile tab")

    frame = tk.Frame(container)
    frame.pack(fill = 'both', expand = True)
    container.add(frame, text = 'Caption Compile')
