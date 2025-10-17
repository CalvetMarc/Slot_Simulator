from src.GameManager import GameManager
import os

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    manager = GameManager()
    manager.simulate_rtp(True)

if __name__ == "__main__":
    main()
