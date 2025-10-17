import ctypes
import os

# Absolute path to the shared library (adjust if your layout differs)
_here = os.path.abspath(os.path.dirname(__file__))
lib_path = os.path.join(_here, "libpcg_rng.so")

pcg = ctypes.CDLL(lib_path)

# --- Signatures / restypes ---

# Seeding / state
pcg.set_seed.argtypes   = [ctypes.c_uint64]
pcg.set_seed.restype    = None

pcg.reset_rng.argtypes  = [ctypes.c_uint64]
pcg.reset_rng.restype   = None

pcg.get_state.argtypes  = []
pcg.get_state.restype   = ctypes.c_uint64

pcg.set_state.argtypes  = [ctypes.c_uint64]
pcg.set_state.restype   = None

# Core
pcg.pcg32.argtypes      = []
pcg.pcg32.restype       = ctypes.c_uint32

pcg.pcg_normalized.argtypes = []
pcg.pcg_normalized.restype  = ctypes.c_double

# Helpers
pcg.pcg_between.argtypes    = [ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool]
pcg.pcg_between.restype     = ctypes.c_int

pcg.pcg_between_u32.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_bool, ctypes.c_bool]
pcg.pcg_between_u32.restype  = ctypes.c_uint32

pcg.pcg_between_float.argtypes = [ctypes.c_double, ctypes.c_double]
pcg.pcg_between_float.restype  = ctypes.c_double

pcg.pcg_bool.argtypes   = []
pcg.pcg_bool.restype    = ctypes.c_bool

# --- Python conveniences ---

def set_seed(seed: int) -> None:
    pcg.set_seed(ctypes.c_uint64(seed))

def reset_rng(seed: int) -> None:
    pcg.reset_rng(ctypes.c_uint64(seed))

def get_state() -> int:
    return int(pcg.get_state())

def set_state(s: int) -> None:
    pcg.set_state(ctypes.c_uint64(s))

def get_uint32() -> int:
    return int(pcg.pcg32())

def get_normalized() -> float:
    return float(pcg.pcg_normalized())

def get_int_between(min_val: int, max_val: int, inc_min: bool = True, inc_max: bool = True) -> int:
    return int(pcg.pcg_between(min_val, max_val, inc_min, inc_max))

def get_uint_between(min_val: int, max_val: int, inc_min: bool = True, inc_max: bool = True) -> int:
    # 0..4294967295 range-safe
    return int(pcg.pcg_between_u32(ctypes.c_uint32(min_val), ctypes.c_uint32(max_val), inc_min, inc_max))

def get_float_between(min_val: float, max_val: float) -> float:
    return float(pcg.pcg_between_float(min_val, max_val))

def get_bool() -> bool:
    return bool(pcg.pcg_bool())
