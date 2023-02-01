from PIL import ImageTk, Image 

def CalculateAspectRatio(img):
    width, height = img.size
    return width / height

def MaximumScale(img, size: tuple):
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
    print("Resizing Wrap lenght for " + str(ent))

    length *= multiplier #Snap multiplier
    if max > length > min:
        ent.config(wraplength = length * endmultiplier)
    elif length > max:
        ent.config(wraplength = max)
    else:
        ent.config(wraplength = min)

def ResizePicture(pic, size: tuple):
    return ImageTk.PhotoImage(pic.resize(size, Image.ANTIALIAS))

def ApplyResizeImage(cont, var, storage, width = 0, height = 0):
    width, height = MaximumScale(var, (cont.winfo_width(), cont.winfo_height()))
    globals()[storage] = ResizePicture(var, (width - 20, height - 20))
    cont.config(image = globals()[storage])
