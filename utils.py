import os
import base64
import tkinter as tk
import pyglet
from PIL import Image, ImageTk
from tkinter.messagebox import askquestion

ASSETS = "./assets"
PACK_IMAGE_PATH = "./assets/images/packs"

def str2b64(text:str) -> str:
    string_bytes = text.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes) 
    return base64_bytes.decode("ascii")

class EmptyCombobox():
    def current(*args) -> None:
        pass

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder='', cnf={}, fg='black',
                 fg_placeholder='grey50', *args, **kw):
        super().__init__(master, cnf, bg='white', *args, **kw)
        self.fg = fg
        self.fg_placeholder = fg_placeholder
        self.placeholder = placeholder
        self.bind('<FocusOut>', lambda event: self.fill_placeholder())
        self.bind('<FocusIn>', lambda event: self.clear_box())
        self.fill_placeholder()

    def clear_box(self):
        if not self.get() and super().get():
            self.config(fg=self.fg)
            self.delete(0, tk.END)

    def fill_placeholder(self):
        if not super().get():
            self.config(fg=self.fg_placeholder)
            self.insert(0, self.placeholder)
    
    def get(self):
        content = super().get()
        if content == self.placeholder:
            return ''
        return content

def clearBox(frameDict) -> None:
    for env in frameDict.keys():
        for namespace in frameDict[env].keys():
            for widget in frameDict[env][namespace].winfo_children():
                widget.destroy()

def load_fonts() -> None:
    for font in os.listdir(ASSETS + "/fonts"):
        pyglet.font.add_file(ASSETS + "/fonts/" + font)

def get_pack_images() -> dict:
    pack_image = {}
    for pack in os.listdir(PACK_IMAGE_PATH):
        pack_image[pack] = {}
        for image in os.listdir(PACK_IMAGE_PATH + "/" + pack):
            img = Image.open(rf"{PACK_IMAGE_PATH}/{pack}/{image}")
            pack_image[pack][image.split(".")[0]] = ImageTk.PhotoImage(img.resize((20, 20)))

    return pack_image

def leave() -> None:
    res = askquestion("Quitter", "Etes-vous sûr de vouloir quitter ?\n\nToutes les modifications effectué ne seront pas enregistré.")
    if res == "yes":
        quit()
    return
