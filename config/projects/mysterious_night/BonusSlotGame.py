from src.freeprngLib import pcg

class BonusSlotGame:
    """
    Represents the bonus game engine for 'Mysterious Night'.
    Handles bonus spawning, multipliers, and level progression.
    """

    def __init__(self, elementsSpawnrate, multipliersSpawnrate, bonusLevels):
        self.elementsSpawnrate = elementsSpawnrate          # BonusSpawner instance
        self.multipliersSpawnrate = multipliersSpawnrate    # CardMultiplierSpawner instance
        self.bonusLevels = bonusLevels                      # BonusLevels instance

        # Estat general del bonus
        self.current_level = None
        self.grid = None
        self.grid_rows = 0
        self.grid_cols = 0
        self.free_spins = 0
        self.bonus_symbols_collected = 0
        self.total_multiplier = 0

        # 🔹 Variables de debug per al GameManager (no eliminar)
        self.spins_played = 0
        self.debug_cf_count = 0
        self.debug_spins_with_chest = 0
        self.debug_multi_sum = 0
        self.debug_multi_when_chest = 0


    # --------------------------------------------------------------
    def start(self, scatters, bet, gridSize):
        """
        Inicia el bonus, executa spins i recull estadístiques.
        """
        # Assignar nivell segons els scatters
        self.current_level = None
        for level in self.bonusLevels.levels:
            if scatters >= level.scatters_required:
                self.current_level = level

        if self.current_level is None or bet <= 0:
            return 0.0

        # Iniciar estat del bonus
        self.free_spins = self.current_level.start_free_spins
        if self.free_spins <= 0:
            return 0.0

        self.bonus_symbols_collected = 0
        self.total_multiplier = 0
        self.grid_rows, self.grid_cols = gridSize
        self.grid = [["" for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]

        # Reiniciar comptadors per al GameManager
        self.spins_played = 0
        self.debug_cf_count = 0
        self.debug_spins_with_chest = 0
        self.debug_multi_sum = 0
        self.debug_multi_when_chest = 0

        # Bucle principal del bonus
        while self.free_spins > 0:
            self.spins_played += 1
            spin_multiplier = self.spin(debug=False)

            # Comptar símbols rellevants
            cf_this_spin = sum(1 for row in self.grid for cell in row if "card front" in str(cell).lower())
            chest_found = any("chest" in str(cell).lower() for row in self.grid for cell in row)

            # Actualitzar comptadors per al GameManager
            self.debug_cf_count += cf_this_spin
            self.debug_multi_sum += spin_multiplier
            if chest_found:
                self.debug_spins_with_chest += 1
                self.debug_multi_when_chest += spin_multiplier

            self.evaluate_spin(spin_multiplier)

        # Si no hi ha multiplicador acumulat, assignem x1
        if self.total_multiplier == 0:
            self.total_multiplier = 1

        # Càlcul final del premi
        total_win = bet * self.total_multiplier
        return total_win


    # --------------------------------------------------------------
    def spin(self, debug=False):
        """Genera la grid i calcula el multiplicador d’un spin del bonus (usant PCG RNG)."""
        current_spin_multiplier = 0
        grid = []

        # Exemple: inicialitza la llavor (pots fer-ho un cop globalment fora d'aquí)        

        for _ in range(self.grid_rows):
            fila = []
            for _ in range(self.grid_cols):
                # --- Usa el teu RNG natiu ---
                rand_value = pcg.get_float_between(0.0, 100.0)
                selected_element = None
                cumulative = 0

                # Selecció d'element segons probabilitats
                for element, prob in self.elementsSpawnrate.probabilities.items():
                    cumulative += prob
                    if rand_value <= cumulative:
                        selected_element = element
                        break

                # Si és "Card Front", afegir multiplicador
                if selected_element and selected_element.lower() == "card front":
                    rand_multi = pcg.get_float_between(0.0, 100.0)
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
        return current_spin_multiplier



    # --------------------------------------------------------------
    def evaluate_spin(self, multiplier):
        """Guarda el multiplicador si hi ha un chest i gestiona upgrades."""
        chest_found = any("chest" in (cell or "").lower() for row in self.grid for cell in row)
        if not chest_found:
            multiplier = 0

        bonus_count = sum(1 for row in self.grid for cell in row if "bonus" in (cell or "").lower())
        self.bonus_symbols_collected += bonus_count

        # Gestió de pujada de nivell
        if self.current_level.upgrade_possible and \
           self.bonus_symbols_collected >= self.current_level.bonus_to_upgrade:
            next_level = self.bonusLevels.get_level(self.current_level.level_id + 1)
            if next_level:
                overflow = self.bonus_symbols_collected - self.current_level.bonus_to_upgrade
                previous_level = self.current_level
                self.current_level = next_level
                extra_fs = max(0, next_level.start_free_spins - previous_level.start_free_spins)
                self.free_spins += extra_fs
                self.bonus_symbols_collected = overflow

        self.total_multiplier += multiplier
        return self.total_multiplier


    def __repr__(self):
        if not self.current_level:
            return "<BonusSlotGame (inactive)>"
        return f"<BonusSlotGame Level {self.current_level.level_id}, {self.free_spins} FS>"
