from importlib import import_module
import json
import random
from pathlib import Path
from config.base.base_config_factory import BaseConfigFactory
from src.game.BaseSlotGame import BaseSlotGame


class GameManager:
    """
    Loads configuration and runs the slot game.
    """

    def __init__(self):
        # 🔹 Load global settings
        settings_path = Path(__file__).resolve().parent / "settings.json"
        with open(settings_path, "r", encoding="utf-8") as f:
            self.settings = json.load(f)

        self.game_name = self.settings.get("game_name")
        if self.game_name is None:
            print("⚠️ Warning: 'game_name' not found in settings.json. Defaulting to 'mysterious_night'.")
            self.game_name = "mysterious_night"

        # 🔹 Load per-game settings
        project_path = Path(__file__).resolve().parents[1] / "config" / "projects" / self.game_name
        game_settings_path = project_path / "game_settings.json"

        if not game_settings_path.exists():
            raise FileNotFoundError(f"❌ Missing game_settings.json for {self.game_name}")

        with open(game_settings_path, "r", encoding="utf-8") as f:
            self.game_settings = json.load(f)

        # Get table names from the file
        base_tables = self.game_settings.get("base_data", [])
        bonus_tables = self.game_settings.get("bonus_data", [])       

        # 🔹 Load Excel config via the factory
        base_factory = BaseConfigFactory(self.game_name)
        base_config = base_factory.build(base_tables)
        # 🔹 Initialize the base game
        self.game = BaseSlotGame(**base_config)

        # --- Load BONUS configuration dynamically ---
        try:
            bonus_module_path = f"config.projects.{self.game_name}.bonus_config_factory"
            bonus_module = import_module(bonus_module_path)
            BonusConfigFactory = getattr(bonus_module, "BonusConfigFactory")

            # Build bonus configuration
            bonus_factory = BonusConfigFactory(self.game_name)
            bonus_config = bonus_factory.build(bonus_tables)

            # Import BonusSlotGame dynamically
            bonus_game_path = f"config.projects.{self.game_name}.BonusSlotGame"
            bonus_game_module = import_module(bonus_game_path)
            BonusSlotGame = getattr(bonus_game_module, "BonusSlotGame")

            # 🧩 Ajustem els noms de claus per coincidir amb el constructor
            self.bonus = BonusSlotGame(
                elementsSpawnrate=bonus_config.get("bonus_spawner"),
                multipliersSpawnrate=bonus_config.get("card_multiplier_spawner"),
                bonusLevels=bonus_config.get("levels")
            )

            print(f"✅ Bonus configuration loaded for '{self.game_name}'")

        except ModuleNotFoundError:
            self.bonus = None
            print(f"⚠️ No bonus_config_factory found for '{self.game_name}'. Skipping bonus setup.")

    def test(self):
        """Runs a basic demo spin for the current game."""
        print("\n🚀 Running game demo...")
        self.game.spin(True)
        self.game.evaluate_spin(1, True)

    def simulate_rtp(self, total_spins=1000000, bet=1.0):
        """Runs a full RTP simulation for the base game."""
        total_bet = 0.0
        total_win = 0.0

        for spin_index in range(total_spins):
            self.game.spin()
            win = self.game.evaluate_spin(bet)
            total_bet += bet
            total_win += win            

        rtp = (total_win / total_bet) * 100 if total_bet > 0 else 0
        print("\n📊 Simulation complete!")
        print(f"Total spins: {total_spins}")
        print(f"Total bet: {total_bet:.2f}")
        print(f"Total win: {total_win:.2f}")
        print(f"🎯 Observed RTP: {rtp:.2f}%")
        return rtp
