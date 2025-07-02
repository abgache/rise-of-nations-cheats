import pymem
import pymem.process
import psutil
import time

PROCESS_NAME = "Rise.exe"
OFFSET = 0xA000F4
POP_ADDRESS = 0xA00250
USE_LONG = True  # adapte si c’est 8 bytes ou 4 bytes

def main():
    # Trouver process
    proc = None
    for p in psutil.process_iter(['name']):
        if p.info['name'] == PROCESS_NAME:
            proc = p
            break
    if not proc:
        print("Processus non trouvé")
        return

    pm = pymem.Pymem(PROCESS_NAME)
    module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME)

    # Calcul adresses absolues
    limit_addr = module.lpBaseOfDll + OFFSET
    pop_addr = module.lpBaseOfDll + POP_ADDRESS

    # Ecrire la limite à 250
    if USE_LONG:
        pm.write_longlong(limit_addr, 250)
    else:
        pm.write_int(limit_addr, 250)

    try:
        while True:
            # Forcer pop à 190 en boucle
            if USE_LONG:
                pm.write_longlong(pop_addr, 190)
            else:
                pm.write_int(pop_addr, 190)
            time.sleep(0.1)  # 100 ms
    except KeyboardInterrupt:
        print("Stopped by user")

if __name__ == "__main__":
    main()
