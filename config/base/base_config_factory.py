from pathlib import Path
from config.base.data_loader import load_game_tables

# ---- Simple wrapper classes (expandable later) ----
class Grid:
    def __init__(self, df, strips):
        """
        Creates the initial 2D grid (rows x columns) using the first symbols of each strip.
        Args:
            df (DataFrame): Table containing the grid size (Rows, Columns).
            strips (Strips): Strips object containing the reels.
        """
        self.data = df
        self.rows = int(df.loc[0, "Rows"])
        self.columns = int(df.loc[0, "Columns"])

        # Validació bàsica
        if self.columns != len(strips.reels):
            print(f"⚠️ Warning: Grid expects {self.columns} columns but found {len(strips.reels)} strips.")

        # 🔹 Construïm la grid inicial: primer símbol de cada strip
        # Cada columna del slot correspon a un strip (reel)
        self.grid = []
        for row in range(self.rows):
            fila = []
            for col in range(self.columns):
                # agafem símbol de la posició "row" dins del reel (si existeix)
                reel = strips.reels[col]
                symbol = reel[row % len(reel)] if reel else None
                fila.append(symbol)
            self.grid.append(fila)

    def __repr__(self):
        return f"<Grid {self.rows}x{self.columns}>"

    def get_symbol(self, row, col):
        """Return a symbol from the grid (row, column)."""
        return self.grid[row][col]

    def get_all(self):
        """Return the full 2D grid as a list of lists."""
        return self.grid


class Strips:
    def __init__(self, df):
        """
        Converts the strips DataFrame into a 2D list.
        Each sublist corresponds to one reel (column) and contains its symbols in order.
        """
        # Guarda el DataFrame original (opcional per depuració)
        self.data = df

        # Converteix cada columna en una llista de símbols no nuls
        self.reels = [df[col].dropna().tolist() for col in df.columns]

    def __repr__(self):
        return f"<Strips {len(self.reels)} reels>"

    def get_reel(self, index):
        """Returns a specific reel (list of symbols)."""
        if 0 <= index < len(self.reels):
            return self.reels[index]
        raise IndexError("Reel index out of range")

    def get_all(self):
        """Returns the full 2D array of reels."""
        return self.reels


class Paylines:
    def __init__(self, df):
        """
        Converts the Paylines DataFrame into a 2D list.
        Each sublist corresponds to one payline, and each element indicates the row
        index (0 at top) for that reel.
        """
        self.data = df

        # 🧹 Neteja: selecciona només les columnes que comencen amb "Reel"
        reel_columns = [col for col in df.columns if "Reel" in col]

        # 🔹 Converteix cada fila en una llista d'enters
        self.lines = df[reel_columns].astype(int).values.tolist()

    def __repr__(self):
        return f"<Paylines {len(self.lines)} lines>"

    def get_line(self, index):
        """Return a specific payline (list of row indexes per reel)."""
        if 0 <= index < len(self.lines):
            return self.lines[index]
        raise IndexError("Payline index out of range")

    def get_all(self):
        """Return the full 2D array of paylines."""
        return self.lines


class Paytable:
    def __init__(self, df):
        """
        Converts the Paytable DataFrame into a dictionary:
        { symbol: [pay3, pay4, pay5], ... }
        """
        self.data = df

        # 🧹 Normalitza noms de columnes per seguretat (per si hi ha espais o majúscules)
        df.columns = [str(col).strip() for col in df.columns]

        # Detectem automàticament la columna del símbol (la primera)
        symbol_col = df.columns[0]

        # Les columnes de pagament (Pay3, Pay4, Pay5)
        pay_columns = [col for col in df.columns if col.lower().startswith("pay")]

        # 🔹 Creem el diccionari
        self.table = {
            str(row[symbol_col]).strip(): [float(row[pay]) for pay in pay_columns]
            for _, row in df.iterrows()
        }

    def __repr__(self):
        return f"<Paytable {len(self.table)} symbols>"

    def get_payouts(self, symbol):
        """Return the list of payouts [pay3, pay4, pay5] for a symbol."""
        return self.table.get(symbol, [0, 0, 0])

    def get_payout(self, symbol, count):
        """Return the specific payout for a symbol given its count (3, 4, or 5)."""
        if symbol not in self.table:
            return 0
        index = count - 3  # 3→0, 4→1, 5→2
        if 0 <= index < len(self.table[symbol]):
            return self.table[symbol][index]
        return 0

    def get_all(self):
        """Return the full paytable dictionary."""
        return self.table

# ---- Factory that builds everything ----
class BaseConfigFactory:
    """
    Loads the Excel tables for a specific slot game
    and builds the configuration objects (Grid, Strips, Paylines, Paytable).
    """

    def __init__(self, game_name, base_dir=None):
        root = Path(__file__).resolve().parents[2]
        self.base_path = Path(base_dir or root / "config" / "projects" / game_name)
        self.file_name = "slot_config.xlsx"
        self.game_name = game_name

    def build(self, table_names):
        """Loads all tables listed in table_names and builds config objects."""
        tables = load_game_tables(table_names, self.base_path, self.file_name)

        # Create objects conditionally
        config = {}
        if "Grid" in table_names:
            strips = Strips(tables.get("strips"))
            config["grid"] = Grid(tables.get("grid"), strips)
            config["strips"] = strips
        if "Paylines" in table_names:
            config["paylines"] = Paylines(tables.get("paylines"))
        if "Paytable" in table_names:
            config["paytable"] = Paytable(tables.get("paytable"))

        return config

