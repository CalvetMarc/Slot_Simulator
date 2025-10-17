import pandas as pd
from pathlib import Path
from config.base.data_loader import load_game_tables


# ---- Bonus configuration data classes ----

class BonusSpawner:
    """Represents the probabilities of spawning different bonus elements."""
    def __init__(self, df):
        self.data = df
        self.probabilities = {
            col: round(float(df[col].iloc[0]) * 100, 2)
            for col in df.columns
            if str(col).strip().lower() != "columna 1"
        }

    def __repr__(self):
        return f"<BonusSpawner {len(self.probabilities)} entries>"

    def get_probability(self, name):
        """Return the probability for a specific bonus type (%)."""
        return self.probabilities.get(name, 0.0)


class CardMultiplierSpawner:
    """
    Represents the card multiplier probabilities as a dictionary:
        { multiplier: probability%, ... }
    """
    def __init__(self, df):
        self.data = df

        # Normalitzem noms de columnes
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Verifiquem que existeixen les columnes necessàries
        if "card multiplier" not in df.columns or "probability" not in df.columns:
            raise KeyError(f"❌ Expected columns 'Card Multiplier' and 'Probability' not found in {list(df.columns)}")

        # Creem el diccionari {multiplier: probability%}, multiplicant per 100
        self.multipliers = {
            int(row["card multiplier"]): float(row["probability"]) * 100
            for _, row in df.iterrows()
            if not pd.isna(row["card multiplier"])
        }

    def __repr__(self):
        return f"<CardMultiplierSpawner {len(self.multipliers)} entries>"

    def get_probability(self, multiplier):
        """Return the probability % for a given multiplier value."""
        return self.multipliers.get(multiplier, 0.0)



# ---- Bonus Levels ----

class Level:
    """
    Represents one bonus level.
    """
    def __init__(self, level_id, scatters, free_spins, upgrade_required):
        self.level_id = int(level_id)
        self.scatters_required = int(scatters)
        self.start_free_spins = int(free_spins)
        self.upgrade_possible = upgrade_required > 0
        self.bonus_to_upgrade = int(upgrade_required)

    def __repr__(self):
        return (f"<Level {self.level_id}: {self.start_free_spins} FS, "
                f"requires {self.scatters_required} scatters, "
                f"{'upgradeable' if self.upgrade_possible else 'final'}>")


class BonusLevels:
    """
    Contains all bonus levels, ordered by level.
    """
    def __init__(self, df):
        self.data = df
        df.columns = [str(c).strip().lower() for c in df.columns]

        self.levels = []
        for _, row in df.iterrows():
            lvl = Level(
                level_id=row["level"],
                scatters=row["scatters"],
                free_spins=row["start free spins"],
                upgrade_required=row["bonus to upgrade"]
            )
            self.levels.append(lvl)

    def __repr__(self):
        return f"<BonusLevels {len(self.levels)} levels>"

    def get_level(self, level_id):
        """Return the Level object for the given ID."""
        for lvl in self.levels:
            if lvl.level_id == level_id:
                return lvl
        return None

    def get_all(self):
        """Return all levels as a list."""
        return self.levels


# ---- Factory that builds everything ----

class BonusConfigFactory:
    """Loads the Excel tables for a specific slot game and builds the configuration objects for the bonus logic."""
    def __init__(self, game_name, base_dir=None):
        root = Path(__file__).resolve().parents[1]
        self.base_path = Path(base_dir or root / game_name)
        self.file_name = "slot_config.xlsx"
        self.game_name = game_name

    def build(self, table_names, debug = False):
        """Loads all tables listed in table_names and builds config objects."""

        print("Loading Bonus Config...")
        tables = load_game_tables(table_names, self.base_path, self.file_name)

        config = {}

        if "bonus_spawner" in tables:
            config["bonus_spawner"] = BonusSpawner(tables["bonus_spawner"])                

        if "card_multiplier_spawner" in tables:
            config["card_multiplier_spawner"] = CardMultiplierSpawner(tables["card_multiplier_spawner"])                

        if "levels" in tables:
            config["levels"] = BonusLevels(tables["levels"])
                
        
        print("BONUS CONFIG LOADED SUCCESSFULLY ✅\n")

        if(debug):
            print("────────────────────────────────\n")
            print("Debug Loaded Bonus Data")      
            print("\n────────────────────────────────")

            print("\nBONUS SPAWNER DATAFRAME:")
            print(tables["bonus_spawner"].to_string(index=False))
            print("\nBONUS SPAWNER PROBABILITIES (%):")
            print(config["bonus_spawner"].probabilities)
            print("\nCARD MULTIPLIER SPAWNER DATAFRAME:")
            print(tables["card_multiplier_spawner"].to_string(index=False))
            print("\nCARD MULTIPLIER SPAWNER MULTIPLIERS (%):")
            print(config["card_multiplier_spawner"].multipliers)
            print("\nBONUS LEVELS DATAFRAME:")
            print(tables["levels"].to_string(index=False))
            print("\nPARSED BONUS LEVEL OBJECTS:")
            for lvl in config["levels"].levels:
                print(f" - {lvl}")

            print("\n")

        return config
