from importlib import import_module
import json
import random
from pathlib import Path
from config.base.base_config_factory import BaseConfigFactory
from src.game.BaseSlotGame import BaseSlotGame
import os


class GameManager:
    """
    Loads configuration files and manages the full slot game lifecycle (base + bonus).
    Handles initialization, simulation, and debug reporting.
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

        # Retrieve table names from the JSON
        base_tables = self.game_settings.get("base_data", [])
        bonus_tables = self.game_settings.get("bonus_data", [])

        # 🔹 Load Excel configuration via the factory
        base_factory = BaseConfigFactory(self.game_name)
        base_config = base_factory.build(base_tables)

        # 🔹 Initialize the base game
        self.game = BaseSlotGame(**base_config)

        # --- Dynamically load BONUS configuration ---
        try:
            bonus_module_path = f"config.projects.{self.game_name}.bonus_config_factory"
            bonus_module = import_module(bonus_module_path)
            BonusConfigFactory = getattr(bonus_module, "BonusConfigFactory")

            # Build bonus configuration
            bonus_factory = BonusConfigFactory(self.game_name)
            bonus_config = bonus_factory.build(bonus_tables)

            # Dynamically import BonusSlotGame class
            bonus_game_path = f"config.projects.{self.game_name}.BonusSlotGame"
            bonus_game_module = import_module(bonus_game_path)
            BonusSlotGame = getattr(bonus_game_module, "BonusSlotGame")

            # 🧩 Match config keys with constructor arguments
            self.bonus = BonusSlotGame(
                elementsSpawnrate=bonus_config.get("bonus_spawner"),
                multipliersSpawnrate=bonus_config.get("card_multiplier_spawner"),
                bonusLevels=bonus_config.get("levels")
            )

        except ModuleNotFoundError:
            self.bonus = None
            print(f"⚠️ No bonus_config_factory found for '{self.game_name}'. Skipping bonus setup.")


    # ---------------------------------------------------------------------
    def test(self):
        """Runs a single test spin to verify that the game loads correctly."""
        print("\n🚀 Running game demo...")
        self.game.spin(True)
        self.game.evaluate_spin(1, True)


    # ---------------------------------------------------------------------
    def simulate_rtp(self, debug=False, total_spins=2000000, bet=1.0):
        """
        Executes a full RTP simulation for both base and bonus games.
        Calculates total RTP, base RTP, bonus RTP, and provides debug analytics.

        Args:
            debug (bool): If True, prints detailed simulation data.
            total_spins (int): Number of spins to simulate.
            bet (float): The bet amount per spin.
        """
        print("────────────────────────────────\n")
        print("RTP Simulation In Progress...")

        total_bet = 0.0
        total_win = 0.0
        base_win_total = 0.0
        bonus_win_total = 0.0
        bonus_triggers = 0
        bonus_total_spins = 0  # Total spins within all bonus rounds

        # --- Global debug counters ---
        total_cf_count = 0
        total_bonus_spins = 0
        total_chest_spins = 0
        total_bonus_multiplier_sum = 0
        total_bonus_multi_when_chest = 0
        total_bonus_multiplier_final = 0        

        for spin_index in range(total_spins):
            # --- Base spin ---
            spin_result = self.game.spin(debug=False)
            win = self.game.evaluate_spin(bet)
            base_win_total += win

            total_bet += bet
            total_win += win

            # --- Check for bonus trigger ---
            scatter_count = sum(
                1
                for row in self.game.grid.grid
                for symbol in row
                if str(symbol).lower() == "scatter"
            )

            if scatter_count >= 3 and self.bonus:
                bonus_triggers += 1
                grid_size = (self.game.grid.rows, self.game.grid.columns)
                
                # Reset bonus debug counters
                self.bonus.debug_spins = 0
                self.bonus.debug_cf_count = 0
                self.bonus.debug_spins_with_chest = 0
                self.bonus.debug_multi_sum = 0
                self.bonus.debug_multi_when_chest = 0
                self.bonus.spins_played = 0

                # Execute bonus round
                bonus_win = self.bonus.start(scatters=scatter_count, bet=bet, gridSize=grid_size)
                bonus_win_total += bonus_win
                total_win += bonus_win                

                # Retrieve debug info from the bonus round
                spins_done = getattr(self.bonus, "spins_played", 0)
                cf_count = getattr(self.bonus, "debug_cf_count", 0)
                chest_spins = getattr(self.bonus, "debug_spins_with_chest", 0)
                multi_sum = getattr(self.bonus, "debug_multi_sum", 0)
                multi_when_chest = getattr(self.bonus, "debug_multi_when_chest", 0)
                total_multi_final = getattr(self.bonus, "total_multiplier", 0)

                bonus_total_spins += spins_done
                total_cf_count += cf_count
                total_bonus_spins += spins_done
                total_chest_spins += chest_spins
                total_bonus_multiplier_sum += multi_sum
                total_bonus_multi_when_chest += multi_when_chest
                total_bonus_multiplier_final += total_multi_final

        # --- Final RTP results ---
        base_rtp = (base_win_total / total_bet) * 100 if total_bet > 0 else 0
        bonus_rtp = (bonus_win_total / total_bet) * 100 if total_bet > 0 else 0
        total_rtp = base_rtp + bonus_rtp
        avg_bonus_spins = (bonus_total_spins / bonus_triggers) if bonus_triggers > 0 else 0

        # --- Global debug calculations ---
        avg_cf_per_spin = total_cf_count / total_bonus_spins if total_bonus_spins > 0 else 0
        chest_prob_per_spin = total_chest_spins / total_bonus_spins if total_bonus_spins > 0 else 0
        avg_multi_per_spin = total_bonus_multiplier_sum / total_bonus_spins if total_bonus_spins > 0 else 0
        avg_total_multi_per_bonus = total_bonus_multiplier_final / max(1, bonus_triggers)

        print("Simulation complete! ✅")
        print("\n────────────────────────────────")

        if debug:           
            print("\nDebug Analytics\n")
            print(f"🎯 Base RTP:  {base_rtp:.2f}%")
            print(f"🎯 Bonus RTP: {bonus_rtp:.2f}%")
            print(f"🏁 TOTAL RTP: {total_rtp:.2f}%")

            print(f"\nBonus Played: {bonus_triggers:,}")
            print(f"Avg spins per bonus: {avg_bonus_spins:.2f}")            
            print(f"Avg multiplier per spin: {avg_multi_per_spin:.3f}")
            print(f"Avg total multiplier per bonus: {avg_total_multi_per_bonus:.3f}")
            print(f"Avg Card Front per spin: {avg_cf_per_spin:.3f}")
            print(f"Chest probability per spin: {chest_prob_per_spin*100:.2f}%")
            print("\n────────────────────────────────")
            
        return total_rtp
