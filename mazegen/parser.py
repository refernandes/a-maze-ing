"""Strict parser for the small ``KEY=VALUE`` configuration language.

Parsing is deliberately kept outside :class:`MazeGenerator`.  This gives the
reusable package a clean Python API while the CLI can report line-oriented
syntax errors to a person editing ``config.txt``.
"""
from __future__ import annotations

import os

from mazegen.types import MazeConfig


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
        for number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            # Empty lines and comments are the only lines without '=' that are
            # valid.  Silently ignoring other lines makes configuration typos
            # very difficult to diagnose during the evaluation.
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Invalid syntax on line {number}: expected KEY=VALUE"
                )
            key, val = line.split("=", 1)
            key, val = key.strip().upper(), val.strip()
            if not key:
                raise ValueError(f"Invalid syntax on line {number}: empty key")
            if key in data:
                raise ValueError(f"Duplicate configuration key: {key}")
            data[key] = val

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
        """Convert an ``x,y`` string to an integer coordinate.

        Args:
            s: Coordinate text from the configuration file.

        Returns:
            The parsed ``(x, y)`` integer pair.

        Raises:
            ValueError: If either coordinate is not an integer.
        """
        parts = s.split(",")
        if len(parts) != 2:
            raise ValueError("Coordinate must be x,y format")
        return int(parts[0].strip()), int(parts[1].strip())

    try:
        entry = parse_coord(data["ENTRY"])
        exit_pos = parse_coord(data["EXIT"])
    except ValueError as exc:
        raise ValueError("Invalid ENTRY or EXIT format") from exc
    if entry == exit_pos:
        raise ValueError("ENTRY and EXIT must be different cells")

    perfect_str = data["PERFECT"].upper()
    if perfect_str not in ("TRUE", "FALSE"):
        raise ValueError("PERFECT must be 'True' or 'False'")
    perfect = perfect_str == "TRUE"

    output_file = data["OUTPUT_FILE"]
    if not output_file:
        raise ValueError("OUTPUT_FILE cannot be empty")

    seed_str = data.get("SEED")
    seed: int | None = None
    if seed_str:
        try:
            seed = int(seed_str)
        except ValueError as exc:
            raise ValueError("SEED must be an integer") from exc

    return {
        "width": width,
        "height": height,
        "entry": entry,
        "exit_pos": exit_pos,
        "perfect": perfect,
        "output_file": output_file,
        "seed": seed,
    }
