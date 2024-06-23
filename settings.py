import os
from tkinter import Button, Entry, Label, StringVar, END, Toplevel, Text
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from functions.cache import Cache
from tkinter.ttk import Combobox

ASSETS = "./assets"
PACK_IMAGE = ASSETS + "/images/Packs"

class SettingFrame(Toplevel):
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.title("Seago Setting")
        self.resizable(False, False)
        self.iconbitmap(ASSETS + "/images/logo.ico")

        self.cache   = Cache()
        self.cdtval  = StringVar() # Chemin dossier temporaire
        self.bfss: Text            # Base fichier sealed secret
        self.pvssval = StringVar() # Préfix valeur sealed secret
        self.ckval   = StringVar() # Chemin kubesael
        self.ccval   = StringVar() # Chemin certificat
        self.cmd: Text             # Commande
        self.urlrk   = StringVar() # URL Repository Kubeseal
        self.dk      = StringVar() # Dossier Kubeseal
        self.s       = StringVar() # Style
        
        Canvas(self, width=10, height=10).grid(row=0, column=0)
        Canvas(self, width=5, height=5).grid(row=0, column=2)

        Label(self, text="Chemin dossier temporaire:").grid(row=1, column=1, sticky=E)
        Entry(self, textvariable=self.cdtval, width=50).grid(row=1, column=3, sticky=W)
        Button(self, text="Parcourir", width=12, command=lambda: self.setdirpath(self.cdtval)).grid(row=1, column=4, sticky=E)

        Label(self, text="Base fichier sealed secret:").grid(row=2, column=1, sticky=NE)
        self.bfss = Text(self, width=51, height=10)
        self.bfss.grid(row=2, column=3, columnspan=2, sticky=W)

        Label(self, text="Préfix valeur sealed secret:").grid(row=3, column=1, sticky=E)
        Entry(self, textvariable=self.pvssval, width=10).grid(row=3, column=3, sticky=W)

        Label(self, text="Chemin kubesael:").grid(row=4, column=1, sticky=E)
        Entry(self, textvariable=self.ckval, width=50).grid(row=4, column=3, sticky=W)
        Button(self, text="Parcourir", width=12, command=lambda: self.setfilepath(self.ckval)).grid(row=4, column=4, sticky=E)

        Label(self, text="Chemin certificat:").grid(row=5, column=1, sticky=E)
        Entry(self, textvariable=self.ccval, width=50).grid(row=5, column=3, sticky=W)
        Button(self, text="Parcourir", width=12, command=lambda: self.setfilepath(self.ccval)).grid(row=5, column=4, sticky=E)

        Label(self, text="Commande:").grid(row=6, column=1, sticky=NE)
        self.cmd = Text(self, width=51, height=3)
        self.cmd.grid(row=6, column=3, columnspan=2, sticky=W)

        Label(self, text="URL Repository Kubeseal:").grid(row=7, column=1, sticky=E)
        Entry(self, textvariable=self.urlrk, width=68).grid(row=7, column=3, columnspan=2, sticky=W)

        Label(self, text="Dossier Kubeseal:").grid(row=8, column=1, sticky=E)
        Entry(self, textvariable=self.dk, width=50).grid(row=8, column=3, sticky=W)
        Button(self, text="Parcourir", width=12, command=lambda: self.setfilepath(self.ccval)).grid(row=8, column=4, sticky=E)
        
        Label(self, text="Style:").grid(row=9, column=1, sticky=E)
        config = Combobox(self, textvariable=self.s, width=25)
        config["values"] = os.listdir(PACK_IMAGE)
        config.grid(row=9, column=3, sticky=W)
        config.current(0)
        
        Canvas(self, width=5, height=5).grid(row=97, column=0)

        Button(self, text="Annuler", width=10, command=self.cancel).grid(row=98, column=1, sticky=W)
        Button(self, text="Reset", width=10, command=self.reset).grid(row=98, column=3, sticky=E)
        Button(self, text="Enregistrer", width=12, command=self.save).grid(row=98, column=4, sticky=E)
        
        Canvas(self, width=10, height=10).grid(row=99, column=99)

        self.load()

    def setfilepath(self, var:StringVar):
        path = askopenfilename(initialdir = "/", title = "Select a File", filetypes = [("All files", "*.*")])
        var.set("" if path is None else path)

    def setdirpath(self, var:StringVar):
        path = askdirectory(initialdir = "/", title = "Select a Directory")
        var.set("" if path is None else path)

    def reset(self):
        self.cdtval.set(os.environ["TEMP"])
        self.bfss.delete("1.0", END)
        self.bfss.insert(END, "apiVersion: v1\nkind: Secret\nmetadata:\n  name: {{sealedmakernamevalue}}\ndata:\n  {{sealedmakervalue}}")
        self.pvssval.set(" "*2)
        self.ckval.set("kubeseal")
        self.ccval.set("")
        self.cmd.delete("1.0", END)
        self.cmd.insert(END, "{{kubeseal}} --cert {{crtfile}} --scope cluster-wide < {{inputfile}} -o yaml > {{outputfile}}")

    def load(self):
        self.cdtval.set(self.cache.get("temp_folder"))
        self.bfss.insert(END, self.cache.get("base_sealedsecret"))
        self.pvssval.set(self.cache.get("prefix_sealedmakervalue"))
        self.ckval.set(self.cache.get("kubeseal_path"))
        self.ccval.set(self.cache.get("crtfile_path"))
        self.cmd.insert(END, self.cache.get("command"))

    def save(self):
        self.cache.save(
            temp_folder=self.cdtval.get(),
            base_sealedsecret=self.bfss.get("1.0", END),
            prefix_sealedmakervalue=self.pvssval.get(), 
            kubeseal_path=self.ckval.get(), 
            crtfile_path=self.ccval.get(), 
            command=self.cmd.get("1.0", END))
        self.withdraw()

    def cancel(self):
        self.load()
        self.withdraw()
