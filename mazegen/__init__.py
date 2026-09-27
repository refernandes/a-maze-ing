"""Public API for the reusable ``mazegen`` distribution.

Only the generator class and its small set of supporting enums are exported at
the package boundary.  Internal carving and rendering modules can evolve
without changing the import used by a future project.
"""
from __future__ import annotations

from mazegen.generator import MazeGenerator
from mazegen.types import Algorithm, Direction, MazeConfig

__version__ = "1.0.0"
__all__ = ["MazeGenerator", "Algorithm", "Direction", "MazeConfig"]
