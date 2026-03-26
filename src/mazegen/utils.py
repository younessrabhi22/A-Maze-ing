"""
utils.py - Configuration file parser and validator.

Place this file at: src/mazegen/utils.py
"""

from typing import Any, Dict


def parse_config(filepath: str) -> Dict[str, str]:
    """
    Parse a KEY=VALUE configuration file safely.

    Lines starting with '#' are treated as comments and ignored.

    Args:
        filepath: Path to the configuration file.

    Returns:
        A dictionary mapping string keys to string values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If a non-comment line is not in KEY=VALUE format.
    """
    settings: Dict[str, str] = {}
    try:
        with open(filepath, "r") as fh:
            for line in fh:
                clean = line.strip()
                if not clean or clean.startswith("#"):
                    continue
                if "=" not in clean:
                    raise ValueError(
                        f"Invalid format (missing '='): '{clean}'"
                    )
                key, _, value = clean.partition("=")
                settings[key.strip()] = value.strip()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Configuration file not found: '{filepath}'"
        )
    return settings


def validate_config(raw: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate and convert raw configuration strings to typed values.

    Args:
        raw: Dictionary of raw string key/value pairs.

    Returns:
        A clean dictionary with proper Python types.

    Raises:
        ValueError: If any required key is missing or invalid.
    """
    cfg: Dict[str, Any] = {}

    mandatory_keys = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
    ]
    for key in mandatory_keys:
        if key not in raw:
            raise ValueError(
                f"Missing mandatory config key: '{key}'"
            )

    # --- WIDTH / HEIGHT ---
    try:
        cfg["WIDTH"] = int(raw["WIDTH"])
        cfg["HEIGHT"] = int(raw["HEIGHT"])
    except ValueError:
        raise ValueError(
            "WIDTH and HEIGHT must be valid integers."
        )

    w, h = cfg["WIDTH"], cfg["HEIGHT"]
    if w < 3 or h < 3:
        raise ValueError(
            "WIDTH and HEIGHT must each be at least 3."
        )

    # --- SEED (optional) ---
    if "SEED" in raw:
        try:
            cfg["SEED"] = int(raw["SEED"])
        except ValueError:
            raise ValueError("SEED must be a valid integer.")
    else:
        cfg["SEED"] = None

    # --- ENTRY / EXIT ---
    try:
        ep = raw["ENTRY"].split(",")
        xp = raw["EXIT"].split(",")
        if len(ep) != 2 or len(xp) != 2:
            raise ValueError()
        cfg["ENTRY"] = (int(ep[0]), int(ep[1]))
        cfg["EXIT"] = (int(xp[0]), int(xp[1]))
    except (ValueError, IndexError):
        raise ValueError(
            "ENTRY and EXIT must be in the format X,Y (e.g., 0,0)."
        )

    ex, ey = cfg["ENTRY"]
    xx, xy = cfg["EXIT"]
    if not (0 <= ex < w and 0 <= ey < h):
        raise ValueError(
            f"ENTRY ({ex},{ey}) is out of bounds for {w}x{h} maze."
        )
    if not (0 <= xx < w and 0 <= xy < h):
        raise ValueError(
            f"EXIT ({xx},{xy}) is out of bounds for {w}x{h} maze."
        )
    if cfg["ENTRY"] == cfg["EXIT"]:
        raise ValueError(
            "ENTRY and EXIT must be different coordinates."
        )

    # --- PERFECT ---
    perfect_str = raw["PERFECT"].strip().lower()
    if perfect_str not in ("true", "false"):
        raise ValueError("PERFECT must be 'True' or 'False'.")
    cfg["PERFECT"] = (perfect_str == "true")

    # --- OUTPUT_FILE ---
    cfg["OUTPUT_FILE"] = raw["OUTPUT_FILE"].strip()
    if not cfg["OUTPUT_FILE"]:
        raise ValueError("OUTPUT_FILE must not be empty.")

    # --- ALGO (optional, default DFS) ---
    valid_algos = {"PRIM", "DFS"}
    raw_algo = raw.get("ALGO", "DFS").strip().upper()
    if raw_algo not in valid_algos:
        raise ValueError(
            f"Unsupported ALGO '{raw_algo}'. "
            f"Supported: {sorted(valid_algos)}."
        )
    cfg["ALGO"] = raw_algo

    return cfg
