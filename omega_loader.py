import sys
import time

# CONFIG
FPS = 20
DELAY = 1.0 / FPS
COLOR_CYAN = "\033[1;36m"
COLOR_RESET = "\033[0m"

# Základní stavební kámen
BASE = "+×xXx×+"

def get_frames():
    frames = []
    # Generování cesty TAM (Hvězda putuje zleva doprava)
    # Vkládáme '*' mezi znaky
    for i in range(len(BASE) + 1):
        # Rozdělíme string a vložíme hvězdu
        s = BASE[:i] + "*" + BASE[i:]
        frames.append(s)
    
    # Generování cesty ZPĚT (bez prvního a posledního, aby to cuklo plynule)
    frames += frames[-2:0:-1]
    return frames

def animate():
    frames = get_frames()
    idx = 0
    # Skryj kurzor
    sys.stdout.write("\033[?25l")
    
    try:
        while True:
            frame = frames[idx % len(frames)]
            # \r = návrat na začátek řádku, \033[K = vymazat zbytek řádku (prevence smetí)
            output = f"\r{COLOR_CYAN}[ {frame} ]{COLOR_RESET} OMEGA PROCESSING..."
            sys.stdout.write(output)
            sys.stdout.flush()
            time.sleep(DELAY)
            idx += 1
    except KeyboardInterrupt:
        pass
    finally:
        # Úklid po ukončení: Zobraz kurzor a vymaž řádek
        sys.stdout.write("\033[?25h\r\033[K")
        sys.stdout.flush()

if __name__ == "__main__":
    animate()
