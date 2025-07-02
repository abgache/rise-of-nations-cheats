import tkinter as tk
from tkinter import messagebox
import pymem
import pymem.process
import psutil
import threading
import time

# ==== CONFIG ====
PROCESS_NAME = "Rise.exe"
OFFSET = 0xA000F4  # Adresse de la limite de pop
POP_ADDRESS = 0xA00250  # Adresse de la population actuelle
USE_LONG = True  # True pour 8 octets, False pour 4 octets
PAGE_TITLE = "Rise of Nations - Population Limit Cheat"
# ================

class RiseCheatApp:
    def __init__(self, root):
        self.root = root
        self.root.title(PAGE_TITLE)

        self.label_status = tk.Label(root, text="🔄 Recherche de rise.exe...")
        self.label_status.pack(pady=5)

        self.label_current = tk.Label(root, text="Valeur actuelle : ???")
        self.label_current.pack(pady=5)

        self.entry = tk.Entry(root)
        self.entry.pack(pady=5)

        self.button = tk.Button(root, text="Appliquer", command=self.set_value)
        self.button.pack(pady=5)

        # --- Forçage de population ---
        self.entry_force = tk.Entry(root)
        self.entry_force.pack(pady=5)
        self.entry_force.insert(0, "190")  # valeur par défaut

        self.force_running = False
        self.button_force = tk.Button(root, text="Forcer la pop (OFF)", command=self.toggle_force_loop)
        self.button_force.pack(pady=5)

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

    def toggle_force_loop(self):
        if not self.pm:
            messagebox.showerror("Erreur", "Processus non connecté")
            return

        if self.force_running:
            self.force_running = False
            self.button_force.config(text="Forcer la pop (OFF)")
        else:
            self.force_running = True
            self.button_force.config(text="Forcer la pop (ON)")
            threading.Thread(target=self.force_loop, daemon=True).start()

    def force_loop(self):
        try:
            module = pymem.process.module_from_name(self.pm.process_handle, PROCESS_NAME)
            pop_addr = module.lpBaseOfDll + 0xA00250
            while self.force_running:
                val = int(self.entry_force.get())
                if USE_LONG:
                    self.pm.write_longlong(pop_addr, val)
                else:
                    self.pm.write_int(pop_addr, val)
                time.sleep(0.1)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.force_running = False
            self.button_force.config(text="Forcer la pop (OFF)")

if __name__ == "__main__":
    root = tk.Tk()
    app = RiseCheatApp(root)
    root.mainloop()
