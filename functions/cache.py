import pickle
import os

class Cache():
    def __init__(self) -> None:
        # on défini un chemin dans le dossier user pour le fichier cache
        self.pathfile = os.environ["USERPROFILE"] + r"\.seago\seago_cache.pkl"
        # si le fichier n'existe pas
        if not os.path.exists(self.pathfile):
            # alors on défini data à vide
            self.data = {}
            try:os.makedirs("\\".join(self.pathfile.split("\\")[:-1]))
            except: pass
        else:
            # sinon on récupère les data déjà enregistrés
            with open(self.pathfile, 'rb') as handle:
                self.data = pickle.load(handle)

    def save(self, **kwargs):
        # le kwargs permet de pouvoir définir n'importe quelle
        # clé avec n'importe quelle valeur dans les paramètres
        # de la fonction
        # pour tous les paramètres de la fonction
        for key in kwargs.keys():
            # puis on ajout ou redéfini les data suivant si la clé était déjà présente ou non
            self.data[key] = kwargs[key]
        # enfin on sauvegarde les data dans le fichier cache
        with open(self.pathfile, 'wb') as handle:
            pickle.dump(self.data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def get(self, key:str) -> any:
        # la clé se trouve dans les data alors on retourne sa valeur sinon on retourne None
        if self.exist(key):
            return self.data[key]
        return None

    def exist(self, key:str) -> bool:
        # la clé se trouve dans les data alors on retourne vrai sinon on retourne faux
        return self.data is not None and key in self.data.keys()