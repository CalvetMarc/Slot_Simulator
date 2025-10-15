import random

class BonusSlotGame:
    """
    Represents the bonus game engine for 'Mysterious Night'.
    Handles bonus spawning, multipliers, and level progression.
    """

    def __init__(self, elementsSpawnrate, multipliersSpawnrate, bonusLevels):
        self.elementsSpawnrate = elementsSpawnrate          # BonusSpawner instance
        self.multipliersSpawnrate = multipliersSpawnrate    # CardMultiplierSpawner instance
        self.bonusLevels = bonusLevels                      # BonusLevels instance

        # Variables d’estat
        self.current_level = None
        self.grid = None
        self.grid_rows = 0
        self.grid_cols = 0
        self.free_spins = 0
        self.bonus_symbols_collected = 0
        self.total_multiplier = 0


    # --------------------------------------------------------------
    def start(self, scatters, bet, gridSize):
        """
        - Assigna el nivell inicial segons els scatters d’entrada.
        - Inicia la grid i variables de control.
        - Executa els spins fins que s’acabin els Free Spins.
        - Retorna el guany total del bonus.
        """
        # 🧩 Assignar nivell segons els scatters
        self.current_level = None
        for level in self.bonusLevels.levels:
            if scatters >= level.scatters_required:
                self.current_level = level

        if self.current_level is None:
            print("⚠️ No matching bonus level found for scatters =", scatters)
            return 0.0

        # 🧩 Iniciar estat del bonus
        self.free_spins = self.current_level.start_free_spins
        self.bonus_symbols_collected = 0
        self.total_multiplier = 0

        # 🧩 Iniciar mida de la grid
        self.grid_rows, self.grid_cols = gridSize
        self.grid = [["" for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]

        if bet <= 0:
            print("⚠️ Invalid bet value.")
            return 0.0

        if self.free_spins <= 0:
            print("⚠️ Bonus started with 0 free spins.")
            return 0.0

        print(f"\n🎯 Starting Bonus at Level {self.current_level.level_id} ({self.free_spins} Free Spins)")
        print(f"Grid size: {self.grid_rows}x{self.grid_cols}")

        # 🌀 Bucle principal de spins
        while self.free_spins > 0:
            spin_multiplier = self.spin(debug=True)
            self.evaluate_spin(spin_multiplier)

        # Si no hi ha multiplicador acumulat, el posem a 1
        if self.total_multiplier == 0:
            self.total_multiplier = 1

        # 🏁 Càlcul final
        total_win = bet * self.total_multiplier
        print(f"\n🏁 BONUS FINISHED! Total Multiplier: x{self.total_multiplier} → WIN: {total_win:.2f}")
        return total_win


    # --------------------------------------------------------------
    def spin(self, debug=False):
        """
        Executa un spin del bonus:
        - Genera contingut de la grid segons probabilitats.
        - Calcula el multiplicador del spin.
        - Redueix els Free Spins restants.
        """
        current_spin_multiplier = 0
        grid = []

        # 🔁 Generem la grid
        for r in range(self.grid_rows):
            fila = []
            for c in range(self.grid_cols):
                rand_value = random.uniform(0, 100)
                selected_element = None

                # Seleccionem element segons probabilitat acumulada
                cumulative = 0
                for element, prob in self.elementsSpawnrate.probabilities.items():
                    cumulative += prob
                    if rand_value <= cumulative:
                        selected_element = element
                        break

                # Si és "Card Front" → aplicar multiplicador
                if selected_element and selected_element.lower() == "card front":
                    rand_multi = random.uniform(0, 100)
                    cumulative_multi = 0
                    for multi, prob in self.multipliersSpawnrate.multipliers.items():
                        cumulative_multi += prob
                        if rand_multi <= cumulative_multi:
                            current_spin_multiplier += multi
                            break

                fila.append(selected_element or "Empty")

            grid.append(fila)

        self.grid = grid
        self.free_spins -= 1

        if debug:
            print("\n🎰 BONUS SPIN RESULT:")
            for fila in grid:
                print(" | ".join(fila))
            print(f"🎯 Spin Multiplier: +{current_spin_multiplier}")
            print(f"🔁 Free Spins Left: {self.free_spins}")

        return current_spin_multiplier


    # --------------------------------------------------------------
    def evaluate_spin(self, multiplier):
        """
        - Si hi ha almenys un Chest a la grid → es guarda el multiplicador.
        - Si no hi ha cap Chest → multiplier es perd (es posa a 0).
        - Comprova si es pot pujar de nivell segons Bonus Symbols.
        """
        # Comprovar cofres
        chest_found = any("chest" in (cell or "").lower() for row in self.grid for cell in row)
        if not chest_found:
            multiplier = 0
            print("❌ No chest found — multiplier lost!")

        # Comptar Bonus Symbols
        bonus_count = sum(1 for row in self.grid for cell in row if "bonus" in (cell or "").lower())
        self.bonus_symbols_collected += bonus_count

        # Intentar pujar de nivell
        if self.current_level.upgrade_possible and \
           self.bonus_symbols_collected >= self.current_level.bonus_to_upgrade:
            next_level = self.bonusLevels.get_level(self.current_level.level_id + 1)
            if next_level:
                overflow = self.bonus_symbols_collected - self.current_level.bonus_to_upgrade
                self.current_level = next_level
                self.free_spins += next_level.start_free_spins
                self.bonus_symbols_collected = overflow
                print(f"⬆️ Upgraded to Level {self.current_level.level_id}! Added {next_level.start_free_spins} FS.")

        # Sumar al total
        self.total_multiplier += multiplier
        print(f"💰 Total Multiplier: x{self.total_multiplier}")

        return self.total_multiplier


    # --------------------------------------------------------------
    def __repr__(self):
        if not self.current_level:
            return "<BonusSlotGame (inactive)>"
        return f"<BonusSlotGame Level {self.current_level.level_id}, {self.free_spins} FS>"
