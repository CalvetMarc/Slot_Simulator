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

        # Comptadors de debug
        self.debug_spins = 0
        self.debug_cf_count = 0
        self.debug_spins_with_chest = 0
        self.debug_multi_sum = 0
        self.debug_multi_when_chest = 0
        self.spins_played = 0
        self.debug_total_bonus_symbols_seen = 0  # 🧩 Comptador global de símbols bonus vistos


    # --------------------------------------------------------------
    def start(self, scatters, bet, gridSize):
        """
        Inicia el bonus, executa spins i recull estadístiques.
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

        # 🧩 Reiniciem debugs
        self.spins_played = 0
        self.debug_spins = 0
        self.debug_cf_count = 0
        self.debug_spins_with_chest = 0
        self.debug_multi_sum = 0
        self.debug_multi_when_chest = 0

        print(f"\n🎯 Starting Bonus at Level {self.current_level.level_id} ({self.free_spins} Free Spins)")
        print(f"Grid size: {self.grid_rows}x{self.grid_cols}")

        # 🌀 Bucle principal de spins
        while self.free_spins > 0:
            self.spins_played += 1
            self.debug_spins += 1

            spin_multiplier = self.spin(debug=True)

            # Comptar "Card Front" i "Chest" en la grid
            cf_this_spin = sum(1 for row in self.grid for cell in row if "card front" in str(cell).lower())
            chest_found = any("chest" in str(cell).lower() for row in self.grid for cell in row)

            # Actualitzar debugs
            self.debug_cf_count += cf_this_spin
            self.debug_multi_sum += spin_multiplier
            if chest_found:
                self.debug_spins_with_chest += 1
                self.debug_multi_when_chest += spin_multiplier

            self.evaluate_spin(spin_multiplier)

        # Si no hi ha multiplicador acumulat, el posem a 1
        if self.total_multiplier == 0:
            self.total_multiplier = 1

        # 🏁 Càlcul final
        total_win = bet * self.total_multiplier
        print(f"\n🏁 BONUS FINISHED! Total Multiplier: x{self.total_multiplier} → WIN: {total_win:.2f}")

        # --- DEBUG STATS DEL BONUS ---
        if self.debug_spins > 0:
            avg_cf_per_spin = self.debug_cf_count / self.debug_spins
            chest_prob = self.debug_spins_with_chest / self.debug_spins
            avg_multi_per_spin = self.debug_multi_sum / self.debug_spins
            avg_multi_when_chest = self.debug_multi_when_chest / max(1, self.debug_spins_with_chest)

            print("\n🧪 BONUS DEBUG STATS")
            print(f"📦 Avg Card Front per spin: {avg_cf_per_spin:.3f}")
            print(f"🧰 Chest probability per spin: {chest_prob*100:.2f}%")
            print(f"🔢 Avg multiplier per spin: {avg_multi_per_spin:.3f}")
            print(f"🎯 Avg multiplier (when chest): {avg_multi_when_chest:.3f}")
            print(f"💰 Total multiplier (this bonus): {self.total_multiplier:.3f}")
            print(f"🏵️ Total BONUS symbols seen (all bonuses): {self.debug_total_bonus_symbols_seen}")


        return total_win


    # --------------------------------------------------------------
    def spin(self, debug=True):
        """Genera la grid i calcula el multiplicador d’un spin del bonus."""
        current_spin_multiplier = 0
        grid = []

        for r in range(self.grid_rows):
            fila = []
            for c in range(self.grid_cols):
                rand_value = random.uniform(0, 100)
                selected_element = None
                cumulative = 0

                # --- 🧪 DEBUG: mostra les probabilitats utilitzades per fer el spawn ---
                if debug and r == 0 and c == 0:  # només mostrem una vegada per spin (primera cel·la)
                    print("\n📊 BONUS ELEMENT PROBABILITIES USADES:")
                    total_prob = 0
                    for element, prob in self.elementsSpawnrate.probabilities.items():
                        total_prob += prob
                        print(f"  {element:<15} → {prob:>6.2f}% (cumulative {total_prob:>6.2f}%)")
                    print(f"  Total probability sum: {total_prob:.2f}%")

                # --- selecció de l'element ---
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
            col_widths = [max(len(row[c]) for row in grid) for c in range(self.grid_cols)]
            for row in grid:
                formatted_row = " | ".join(f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row))
                print(formatted_row)
            print(f"🎯 Spin Multiplier: +{current_spin_multiplier}")
            print(f"🔁 Free Spins Left: {self.free_spins}")

        return current_spin_multiplier


    # --------------------------------------------------------------
    def evaluate_spin(self, multiplier):
        """Guarda el multiplicador si hi ha un chest i gestiona upgrades."""
        chest_found = any("chest" in (cell or "").lower() for row in self.grid for cell in row)
        if not chest_found:
            multiplier = 0
            print("❌ No chest found — multiplier lost!")

        bonus_count = sum(1 for row in self.grid for cell in row if "bonus" in (cell or "").lower())
        self.bonus_symbols_collected += bonus_count
        self.debug_total_bonus_symbols_seen += bonus_count


        # --- Gestió de pujada de nivell ---
        if self.current_level.upgrade_possible and \
           self.bonus_symbols_collected >= self.current_level.bonus_to_upgrade:
            next_level = self.bonusLevels.get_level(self.current_level.level_id + 1)
            if next_level:
                overflow = self.bonus_symbols_collected - self.current_level.bonus_to_upgrade

                # ✅ Guarda el nivell anterior abans d’actualitzar
                previous_level = self.current_level
                self.current_level = next_level

                # ✅ Afegeix només la diferència de FS entre nivells
                extra_fs = max(0, next_level.start_free_spins - previous_level.start_free_spins)
                self.free_spins += extra_fs

                print(f"⬆️ Upgraded to Level {next_level.level_id}! Added {extra_fs} FS (difference).")
                self.bonus_symbols_collected = overflow

        self.total_multiplier += multiplier
        print(f"💰 Total Multiplier: x{self.total_multiplier}")
        return self.total_multiplier


    def __repr__(self):
        if not self.current_level:
            return "<BonusSlotGame (inactive)>"
        return f"<BonusSlotGame Level {self.current_level.level_id}, {self.free_spins} FS>"
