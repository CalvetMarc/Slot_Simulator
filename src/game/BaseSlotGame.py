import random

class BaseSlotGame:
    """
    Represents the slot game engine for 'Mysterious Night'.
    Handles the grid, strips, paylines, and paytable directly.
    """

    def __init__(self, grid, strips, paylines, paytable):
        self.grid = grid
        self.strips = strips
        self.paylines = paylines
        self.paytable = paytable

    def spin(self, debug = False):
        """
        Performs a professional-style spin:
        - For each reel, picks a random starting index.
        - Takes as many symbols as there are rows in the grid.
        - Wraps around the strip if needed.
        """
        if debug:
            print("\n🔄 Performing spin...")

        num_rows = self.grid.rows
        num_reels = self.grid.columns
        spin_result = [[] for _ in range(num_rows)]

        # For each reel (strip)
        for reel_index in range(num_reels):
            reel = self.strips.reels[reel_index]
            start_index = random.randint(0, len(reel) - 1)

            # Get visible symbols (wrap around if needed)
            visible = [reel[(start_index + i) % len(reel)] for i in range(num_rows)]

            # Place vertically into the grid
            for row in range(num_rows):
                spin_result[row].append(visible[row])

        if debug:
            print("🎯 Spin result (grid):")

        # Calculem l'ample màxim de cada columna
        col_widths = [max(len(row[col]) for row in spin_result) for col in range(len(spin_result[0]))]

        # Printem cada fila amb alineació
        for row in spin_result:
            formatted_row = " | ".join(f"{symbol:<{col_widths[i]}}" for i, symbol in enumerate(row))
            if debug:
                print(formatted_row)


        # Update the internal grid to reflect the spin
        self.grid.grid = spin_result
        return spin_result

    def evaluate_spin(self, bet=1.0, debug = False):
        """
        Evaluates the current grid according to paylines and paytable.
        Wilds substitute for any symbol (except Scatter).
        Returns total win amount.
        """
        total_win = 0.0
        if debug:
            print("\n💰 Evaluating spin...")

        for i, line in enumerate(self.paylines.lines, start=1):
            symbols = [self.grid.get_symbol(row, col) for col, row in enumerate(line)]

            # Busquem el primer símbol no-wild ni scatter
            first_symbol = next((s for s in symbols if s not in ["Wild", "Scatter"]), None)
            if not first_symbol or first_symbol not in self.paytable.table:
                continue

            count = 0
            for sym in symbols:
                if sym == first_symbol or sym == "Wild":
                    count += 1
                else:
                    break

            # Si tenim 3 o més consecutius, premi
            if count >= 3:
                payout = self.paytable.get_payout(first_symbol, count)
                win_amount = payout * bet
                total_win += win_amount
                if debug:
                    print(f"✅ Line {i}: {count}x {first_symbol} (with Wilds) → {win_amount:.2f}")

        if debug:
            print(f"\n🏆 Total Win: {total_win:.2f}\n")
            
        return total_win


    def show_summary(self):
        """
        Prints a quick summary of the game configuration.
        """
        print("\n📊 Game Summary:")
        print(f"Grid size: {int(self.grid.data.loc[0, 'Rows'])}x{int(self.grid.data.loc[0, 'Columns'])}" if self.grid.data is not None else "Grid size: Unknown")
        print(f"Strips: {len(self.strips.reels)} reels")
        print(f"Paylines: {len(self.paylines.lines)} lines")
        print(f"Paytable symbols: {len(self.paytable.table)} symbols")
