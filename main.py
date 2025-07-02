import tkinter as tk
from tkinter import messagebox
import pymem
import pymem.process
import psutil

# ==== CONFIG ====
PROCESS_NAME = "Rise.exe"
OFFSET = 0xA000F4  # offset connu - Rise.exe+A000F4 c'est l'adresse mémoire ou ya la limite de population
USE_LONG = True    # True si 8 bytes, False si 4 bytes
PAGE_TITLE = "Rise of Nations - Population Limit Cheat" # Au cas ou on doit changer le nom de la fênetre - Default : "Rise of Nations - Population Limit Cheat"
# ================

class RiseCheatApp:
    def __init__(self, root):
        self.root = root
        global PAGE_TITLE # recup la variable car elle est pas dans la classe ni dans la fonction
        self.root.title(PAGE_TITLE)

        self.label_status = tk.Label(root, text="🔄 Recherche de rise.exe...")
        self.label_status.pack(pady=5)

        self.label_current = tk.Label(root, text="Valeur actuelle : ???")
        self.label_current.pack(pady=5)

        self.entry = tk.Entry(root)
        self.entry.pack(pady=5)

        self.button = tk.Button(root, text="Appliquer", command=self.set_value)
        self.button.pack(pady=5)

        self.pm = None
        self.base_address = None
        self.connect_to_process()

    def connect_to_process(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == PROCESS_NAME:
                try:
                    self.pm = pymem.Pymem(PROCESS_NAME)
                    module = pymem.process.module_from_name(self.pm.process_handle, PROCESS_NAME)
                    self.base_address = module.lpBaseOfDll + OFFSET
                    self.label_status.config(text="✅ Connecté à rise.exe")
                    self.update_current_value()
                    return
                except Exception as e:
                    self.label_status.config(text=f"❌ Erreur : {e}")
                    return
        self.label_status.config(text="❌ rise.exe non trouvé")

    def update_current_value(self):
        try:
            if USE_LONG:
                value = self.pm.read_longlong(self.base_address)
            else:
                value = self.pm.read_int(self.base_address)
            self.label_current.config(text=f"Valeur actuelle : {value}")
        except Exception as e:
            self.label_current.config(text=f"Erreur lecture : {e}")

    def set_value(self):
        try:
            new_val = int(self.entry.get())
            if USE_LONG:
                self.pm.write_longlong(self.base_address, new_val)
            else:
                self.pm.write_int(self.base_address, new_val)
            self.update_current_value()
            messagebox.showinfo("Succès", f"Nouvelle limite : {new_val}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = RiseCheatApp(root)
    root.mainloop()
