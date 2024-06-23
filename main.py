import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os
import yaml

from tkinter import Button, Entry, Label, Canvas, StringVar, END, Tk, Toplevel, Text, messagebox
from tkinter.ttk import Frame, Notebook, Combobox
from tkinter.filedialog import askopenfilename, askdirectory
from functions.cache import Cache
from settings import SettingFrame
from utils import EmptyCombobox, PlaceholderEntry, load_fonts, get_pack_images, clearBox, leave
from functions.environments import get_environments
import subprocess
from utils import str2b64

Cache().save( ### A SUPPRIMER ###
    temp_folder=os.environ["TEMP"],
    base_sealedsecret="apiVersion: v1\nkind: Secret\nmetadata:\n  name: {{sealedmakernamevalue}}\ndata:\n  {{sealedmakervalue}}",
    prefix_sealedmakervalue=" "*2, 
    kubeseal_path="C:/Users/Game_K/Desktop/seago/tools/kubeseal.exe", 
    crtfile_path="C:/Users/Game_K/Desktop/seago/certificate/custom-tls.crt", 
    command="{{kubeseal}} --cert {{crtfile}} --scope cluster-wide < {{inputfile}} -o yaml > {{outputfile}}"
)

ENV_DEV = "C:/Users/Game_K/Desktop/k8s-core-staging-deployment"
ASSETS = "./assets"
CHOSE_PACK = "3D Color"

cache = Cache()

app = Tk()
app.withdraw()
root = Toplevel(app)
root.title("Seago")
geometry = (1080, 500)
root.geometry(f"{geometry[0]}x{geometry[1]}")
root.resizable(False, False)
root.iconbitmap(ASSETS + "/images/logo.ico")

# Récupérer le cache
# TODO
# Charger et récupérer l'environnement
environments = get_environments()
# Charger et récupérer les packs d'images
pack_image = get_pack_images()
# Charger les polices de caractères
load_fonts()

setting_frame = SettingFrame()

cdtval = StringVar()
pvssval = StringVar()
ckval = StringVar()
ccval = StringVar()

Canvas(root, width=10, height=10).grid(row=0, column=0)

frameDict = {}

current_user_pos:tuple[str, str, str] = ()

old = {}

environments_change = {}

def update(env, namespace, project, config, entries):
    global environments_change
    
    if env not in environments_change.keys():
        environments_change[env] = {}
    if namespace not in environments_change[env].keys():
        environments_change[env][namespace] = {}
    if project not in environments_change[env][namespace].keys():
        environments_change[env][namespace][project] = {}

    environments_change[env][namespace][project][config] = {
        "path": environments[env][namespace][project]["Path"], 
        "group": environments[env][namespace][project]["Group"], 
        "value": {e["key"].get():e["value"].get() for e in entries}
    }

def save():
    # Réucpérer les modifications
    data = []
    for e in environments_change.keys():
        for n in environments_change[e].keys():
            for p in environments_change[e][n].keys():
                for c in environments_change[e][n][p].keys():
                    d = environments_change[e][n][p][c]["value"]
                    for key in d.keys():
                        if d[key] != environments[e][n][p]["SealedSecret"][c][key]:
                            data.append(f"{e}__SEP__{n}__SEP__{p}__SEP__{c}__SEP__{key}: {str2b64(d[key])}")
    # Chiffrer
    open(cache.get("temp_folder") + "\\seago.tmp", "w", encoding="utf8").write(f"apiVersion: v1\nkind: Secret\nmetadata:\n  name: seago\ndata:\n  {'\n  '.join(data)}")
    cmd = cache.get("command").replace("{{kubeseal}}", cache.get("kubeseal_path")).replace("{{crtfile}}", cache.get("crtfile_path")).replace("{{inputfile}}", cache.get("temp_folder") + "\\seago.tmp").replace("{{outputfile}}", cache.get("temp_folder") + "\\seago.secret.tmp")
    out = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if out.stderr != "":
        print(out.stderr)
        return
    data = [i for i in yaml.load_all(open(cache.get("temp_folder") + "\\seago.secret.tmp"), Loader=yaml.FullLoader)][0]
    for key in data["spec"]["encryptedData"].keys():
        e, n, p, c, k = key.split("__SEP__")
        environments_change[e][n][p][c]["value"][k] = data["spec"]["encryptedData"][key]
    # Modifier les fichiers
    for e in environments_change.keys():
        for n in environments_change[e].keys():
            for p in environments_change[e][n].keys():
                for c in environments_change[e][n][p].keys():
                    environments[e][n][p]["SealedSecret"][c] = environments_change[e][n][p][c]["value"]
                    environments[e][n][p]["Data"][list(environments[e][n][p]["SealedSecret"].keys()).index(c)]["spec"]["encryptedData"] = environments_change[e][n][p][c]["value"]
                data = [yaml.safe_dump(d, sort_keys=False) for d in environments[e][n][p]["Data"]]
                open(environments[e][n][p]["Path"], "w", encoding="utf8").write("\n---\n".join(data))
    # Pull
    # TODO

    # Commit
    # TODO

def checker():
    save()

def callback(env, namespace, event):
    global current_user_pos
    if len(event.widget.curselection()) == 0: # si il n'y a pas de projet sélectionné
        return EmptyCombobox()
    
    project = event.widget.get(event.widget.curselection()[0])
    frame:Frame = frameDict[env][namespace]
    data:dict = environments[env][namespace][project]

    if current_user_pos == (env, namespace, project): # si l'utilisateur n'a pas changé de projet
        return EmptyCombobox()

    current_user_pos = (env, namespace, project)

    clearBox(frameDict)

    if "SealedSecret" in data.keys():

        tk.Label(frame, text=data["Group"], font=(15)).grid(row=1, column=3, columnspan=2, sticky=tk.NE)

        state = "disabled" if len(list(data["SealedSecret"].keys())) < 2 else "readonly"

        config_text = tk.StringVar()
        config = Combobox(frame, textvariable=config_text, width=60, state=state)
        config["values"] = list(data["SealedSecret"].keys())
        config_text.set(list(data["SealedSecret"].keys())[0])
        config.grid(row=1, column=1, columnspan=3, sticky=tk.W)
        # config.bind("<<ComboboxSelected>>", month_changed)

        tk.Canvas(frame, width=10, height=10).grid(row=2, column=0)

        for conf in data["SealedSecret"].keys():
            secret_values = data["SealedSecret"][conf]

            secret_entry = []
            start_pos = 3
            for i, key in enumerate(secret_values.keys()):
                key_value = tk.StringVar(value=key)
                val_value = tk.StringVar()

                key_value.trace("w", lambda name, index, mode: update(env, namespace, project, config_text.get(), secret_entry))
                val_value.trace("w", lambda name, index, mode: update(env, namespace, project, config_text.get(), secret_entry))

                tk.Entry(frame, textvariable=key_value, width=40).grid(row=start_pos*(i+2), column=1)
                tk.Label(frame, text="=", width=3).grid(row=start_pos*(i+2), column=2)
                # PlaceholderEntry(frame, textvariable=val_value, width=80, placeholder=secret_values[key]).grid(row=start_pos*(i+2), column=3)
                val_value.set(secret_values[key])
                tk.Entry(frame, textvariable=val_value, width=80).grid(row=start_pos*(i+2), column=3)
                tk.Button(frame, text="❌", font=(10), borderwidth=0).grid(row=start_pos*(i+2), column=4)

                secret_entry.append({
                    "key": key_value,
                    "value": val_value,
                    "position": start_pos
                })

        return config
    else:
        tk.Canvas(frame, width=50).grid(row=1, column=1)
        tk.Label(frame, text="Pas de secret trouvé", font="Helvetica 10 italic").grid(row=1, column=2)
        return EmptyCombobox()

tabEnvs = Notebook(root, width=geometry[0]-10-(10*2)-(1*2)) # -10 = ? & -10*2 = espace gauche et droite & -1*2 = bordure gauche et droite
for env in environments.keys():
    frameDict[env] = {}

    frameEnv = Frame(tabEnvs, width=500, height=100)
    tabEnvs.add(frameEnv, text=env)

    tk.Canvas(frameEnv, width=10, height=10).grid(row=0, column=0)

    tabNamespaces = Notebook(frameEnv, width=geometry[0]-20-(10*4)-(1*4)) # -20 = ? & -10*4 = -10*2*2 & -1*4 = -1*2*2
    for namespace in environments[env].keys():
        frameNamespace = Frame(tabNamespaces, width=500, height=100)
        tabNamespaces.add(frameNamespace, text=namespace)

        tk.Canvas(frameNamespace, width=10, height=10).grid(row=0, column=0)

        listbox = tk.Listbox(frameNamespace, width=30, height=20, activestyle="none")
        for i, v in enumerate(environments[env][namespace].keys()):
            listbox.insert(i, v)
        listbox.grid(row=1, column=1)
        listbox.bind("<<ListboxSelect>>", lambda event: callback(
            tabEnvs.tab(tabEnvs.select(), "text"), 
            tabNamespaces.tab(tabNamespaces.select(), "text"), 
            event
        ).current(0))

        tk.Canvas(frameNamespace, width=10, height=10).grid(row=0, column=2)

        frameDict[env][namespace] = Frame(frameNamespace)
        frameDict[env][namespace].grid(row=1, column=2, sticky=tk.N)

        tk.Canvas(frameNamespace, width=10, height=10).grid(row=999, column=999)

    tabNamespaces.grid(row=1, column=1)

    tk.Canvas(frameEnv, width=10, height=10).grid(row=999, column=999)

tabEnvs.grid(row=1, column=1, columnspan=3)

tk.Canvas(root, width=10, height=10).grid(row=2, column=1)

ttk.Button(root, text=" Quitter", width=10, image=pack_image[CHOSE_PACK]["exit"], command=leave, compound=tk.LEFT).grid(row=3, column=1, sticky=tk.W, rowspan=2)
ttk.Button(root, text=" Paramètre", width=12, image=pack_image[CHOSE_PACK]["settings"], command=setting_frame.deiconify, compound=tk.LEFT).grid(row=4, column=2, sticky=tk.E)
ttk.Button(root, text=" Chiffrer & Commit", width=20, image=pack_image[CHOSE_PACK]["save"], command=checker, compound=tk.LEFT).grid(row=4, column=3, sticky=tk.E)

tk.Canvas(root, width=10, height=10).grid(row=999, column=999)

setting_frame.protocol("WM_DELETE_WINDOW", setting_frame.withdraw)
setting_frame.withdraw()

app.mainloop()
