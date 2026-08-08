"""Configuration parser module."""
from __future__ import annotations

import os

from mazegen.types import Algorithm, MazeConfig


def parse_config(filename: str) -> MazeConfig:
    """Parse the configuration file.

    Args:
        filename: Path to the configuration file.

    Returns:
        Parsed MazeConfig dict.

    Raises:
        ValueError: If config is invalid or missing required keys.
    """
    if not os.path.exists(filename):
        raise ValueError(f"File not found: {filename}")

    data: dict[str, str] = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                data[key.strip()] = val.strip()

    required = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
    ]
    for req in required:
        if req not in data:
            raise ValueError(f"Missing required key: {req}")

    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])
    except ValueError as exc:
        raise ValueError("WIDTH and HEIGHT must be integers") from exc

    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive")

    def parse_coord(s: str) -> tuple[int, int]:
        parts = s.split(",")
        if len(parts) != 2:
            raise ValueError("Coordinate must be x,y format")
        return int(parts[0].strip()), int(parts[1].strip())

    try:
        entry = parse_coord(data["ENTRY"])
        exit_pos = parse_coord(data["EXIT"])
    except ValueError as exc:
        raise ValueError("Invalid ENTRY or EXIT format") from exc

    perfect_str = data["PERFECT"].upper()
    if perfect_str not in ("TRUE", "FALSE"):
        raise ValueError("PERFECT must be 'True' or 'False'")
    perfect = perfect_str == "TRUE"

    output_file = data["OUTPUT_FILE"]

    seed_str = data.get("SEED")
    seed: int | None = None
    if seed_str:
        try:
            seed = int(seed_str)
        except ValueError as exc:
            raise ValueError("SEED must be an integer") from exc

    alg_str = data.get("ALGORITHM", "DFS").upper()
    try:
        algorithm = Algorithm(alg_str)
    except ValueError as exc:
        raise ValueError(f"Invalid ALGORITHM: {alg_str}") from exc

    return {
        "width": width,
        "height": height,
        "entry": entry,
        "exit_pos": exit_pos,
        "perfect": perfect,
        "output_file": output_file,
        "seed": seed,
        "algorithm": algorithm,
    }
