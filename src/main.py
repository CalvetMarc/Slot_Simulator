from src.GameManager import GameManager
from src.freeprngLib import pcg
import os
import time

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    pcg.set_seed(int(time.time_ns()))
    manager = GameManager()
    manager.simulate_rtp(True)

if __name__ == "__main__":
    main()
