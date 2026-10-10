"""Parser for the project's KEY=VALUE configuration file."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    """Validated options needed to build and save a maze."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None


def parse_config(filename: str) -> Config:
    """Read required options and optional reproducible seed from a file."""
    values: dict[str, str] = {}
    try:
        with open(filename, encoding="utf-8") as config_file:
            for number, raw_line in enumerate(config_file, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(f"Line {number}: expected KEY=VALUE.")
                key, value = (part.strip() for part in line.split("=", 1))
                if not key or key in values:
                    raise ValueError(f"Line {number}: empty or duplicate key.")
                values[key] = value
    except OSError as error:
        raise ValueError(f"Cannot read configuration: {error}") from error

    required = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")
    missing = [key for key in required if key not in values]
    if missing:
        raise ValueError("Missing required key(s): " + ", ".join(missing))

    try:
        width = int(values["WIDTH"])
        height = int(values["HEIGHT"])
        entry = _coordinate(values["ENTRY"])
        exit_pos = _coordinate(values["EXIT"])
        seed = int(values["SEED"]) if values.get("SEED") else None
    except ValueError as error:
        raise ValueError(f"Invalid number or coordinate: {error}") from error

    perfect_text = values["PERFECT"].lower()
    if perfect_text not in ("true", "false"):
        raise ValueError("PERFECT must be True or False.")
    if not values["OUTPUT_FILE"]:
        raise ValueError("OUTPUT_FILE cannot be empty.")

    return Config(
        width, height, entry, exit_pos,
        values["OUTPUT_FILE"], perfect_text == "true", seed,
    )


def _coordinate(value: str) -> tuple[int, int]:
    """Parse a coordinate written as ``x,y``."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError("coordinates must use x,y format")
    return int(parts[0].strip()), int(parts[1].strip())
