"""Public API for the reusable ``mazegen`` distribution.

The generator class and the types needed to describe its grid are exported at
the package boundary. Internal carving and rendering modules can evolve
without changing the import used by a future project.
"""
from __future__ import annotations

from mazegen.generator import MazeGenerator
from mazegen.types import Direction, MazeConfig

__version__ = "1.0.0"
__all__ = ["MazeGenerator", "Direction", "MazeConfig"]
