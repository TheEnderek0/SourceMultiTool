from PIL import ImageTk, Image 

def CalculateAspectRatio(img):
    width, height = img.size
    return width / height

def MaximumScale(img, size: tuple):
    aspect = CalculateAspectRatio(img)
    size_aspect = size[0] / size[1]
    width = 0
    height = 0

    if size_aspect < aspect:
        width = size[0]
        height = int(width / aspect)
    elif size_aspect >= aspect:
        height = size[1]
        width = int(height * aspect)

    return width, height


