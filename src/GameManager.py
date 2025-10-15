import json
from pathlib import Path
from config.base.slot_config_factory import SlotConfigFactory
from src.game.BaseSlotGame import BaseSlotGame


class GameManager:
    """
    Loads configuration and runs the slot game.
    """

    def __init__(self):
        settings_path = Path(__file__).resolve().parent / "settings.json"
        with open(settings_path, "r", encoding="utf-8") as f:
            self.settings = json.load(f)

        self.game_name = self.settings.get("game_name")

        if self.game_name is None:
            print("⚠️ Warning: 'game_name' not found in settings.json. Defaulting to 'mysterious_night'.")


        # Load Excel config via the factory
        self.game = BaseSlotGame(**SlotConfigFactory(self.game_name).build())


    def run(self):
        """
        Runs a basic demo spin for the current game.
        """

        print("\n🚀 Running game demo...")

        self.game.spin(True)
        self.game.evaluate_spin(1, True)

    def simulate_rtp(self, total_spins=1000000, bet=1.0):
        """
        Runs a full RTP simulation for the base game.
        """
        total_bet = 0.0
        total_win = 0.0

        for spin_index in range(total_spins):
            # Spin + evaluate
            self.game.spin()
            win = self.game.evaluate_spin(bet)

            total_bet += bet
            total_win += win            

        # Càlcul final
        rtp = (total_win / total_bet) * 100 if total_bet > 0 else 0
        print("\n📊 Simulation complete!")
        print(f"Total spins: {total_spins}")
        print(f"Total bet: {total_bet:.2f}")
        print(f"Total win: {total_win:.2f}")
        print(f"🎯 Observed RTP: {rtp:.2f}%")

        return rtp

    import random
