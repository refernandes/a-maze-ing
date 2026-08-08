"""MiniLibX-based maze renderer."""
from __future__ import annotations

import sys
from typing import Callable, Any


# Palettes: (wall, path, bg, entry, exit)
COLOR_PALETTES: list[tuple[int, int, int, int, int]] = [
    (0xCCCCCC, 0x00AAFF, 0x1A1A2E, 0x00FF00, 0xFF0000),  # Cyberpunk
    (0xFF6B6B, 0xFFE66D, 0x2D3436, 0x55EFC4, 0xFD79A8),  # Sunset
    (0x6C5CE7, 0x00CEC9, 0x0D0D0D, 0xFFC312, 0xED4C67),  # Neon
]

CELL_SIZE = 20  # pixels per cell
PADDING = 40    # pixels padding around maze


class MazeRenderer:
    """Renders a maze using MiniLibX."""

    def __init__(
        self,
        grid: list[list[int]],
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        solution_path: list[tuple[int, int]],
        pattern_cells: set[tuple[int, int]],
        regenerate_callback: Callable[
            [], tuple[list[list[int]], list[tuple[int, int]]]
        ],
    ) -> None:
        """Initialize the maze renderer.

        Args:
            grid: Maze grid layout.
            width: Width of maze.
            height: Height of maze.
            entry: Start coordinate.
            exit_pos: End coordinate.
            solution_path: Path from entry to exit.
            pattern_cells: Cells matching patterns.
            regenerate_callback: Function to generate a new maze.
        """
        self.grid = grid
        self.grid_w = width
        self.grid_h = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.solution_path = solution_path
        self.pattern_cells = pattern_cells
        self.regenerate_callback = regenerate_callback

        self.show_solution = False
        self.palette_idx = 0

        self.win_w = PADDING * 2 + width * CELL_SIZE
        self.win_h = PADDING * 2 + height * CELL_SIZE

        try:
            from mlx import Mlx
        except ImportError as exc:
            raise RuntimeError(
                "MiniLibX not installed. Run: make install"
            ) from exc
        self.m: Any = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr, self.win_w, self.win_h, "A-Maze-ing"
        )
        self.img_ptr: object | None = None

        self.data_view: memoryview | None = None
        self.size_line = 0
        self.bpp = 0

        self._setup_hooks()
        self._render()

    def _setup_hooks(self) -> None:
        """Setup keyboard and window hooks."""
        def close_hook(param: object) -> None:
            self.quit()

        def key_hook(keynum: int, param: object) -> None:
            self._key_handler(keynum, param)

        self.m.mlx_hook(
            self.win_ptr, 33, 0, close_hook, None
        )
        self.m.mlx_hook(
            self.win_ptr, 2, 1, key_hook, None
        )

    def _key_handler(self, keynum: int, param: object) -> None:
        """Handle keyboard input."""
        if keynum in (65307, 113):
            self.quit()
        elif keynum == 114:
            self.grid, self.solution_path = self.regenerate_callback()
            self._render()
        elif keynum == 115:
            self.show_solution = not self.show_solution
            self._render()
        elif keynum == 99:
            self.palette_idx = (self.palette_idx + 1) % len(COLOR_PALETTES)
            self._render()

    def quit(self) -> None:
        """Exit the application cleanly."""
        if self.img_ptr is not None:
            self.m.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.m.mlx_loop_exit(self.mlx_ptr)
        sys.exit(0)

    def run(self) -> None:
        """Start the MLX event loop."""
        self.m.mlx_loop(self.mlx_ptr)

    def _render(self) -> None:
        """Render the maze to an image and put it to window."""
        if self.img_ptr is not None:
            self.m.mlx_destroy_image(self.mlx_ptr, self.img_ptr)

        self.img_ptr = self.m.mlx_new_image(
            self.mlx_ptr, self.win_w, self.win_h
        )
        data, bpp, size_line, fmt = self.m.mlx_get_data_addr(self.img_ptr)

        self.data_view = data
        self.size_line = size_line
        self.bpp = bpp

        palette = COLOR_PALETTES[self.palette_idx]
        bg_color = palette[2]
        self._fill_rect(0, 0, self.win_w, self.win_h, bg_color)

        if self.show_solution:
            path_color = palette[1]
            for x, y in self.solution_path:
                px = PADDING + x * CELL_SIZE
                py = PADDING + y * CELL_SIZE
                self._fill_rect(px, py, CELL_SIZE, CELL_SIZE, path_color)

        entry_color = palette[3]
        exit_color = palette[4]
        ex, ey = self.entry
        self._fill_rect(
            PADDING + ex * CELL_SIZE, PADDING + ey * CELL_SIZE,
            CELL_SIZE, CELL_SIZE, entry_color
        )
        xx, xy = self.exit_pos
        self._fill_rect(
            PADDING + xx * CELL_SIZE, PADDING + xy * CELL_SIZE,
            CELL_SIZE, CELL_SIZE, exit_color
        )

        for y in range(self.grid_h):
            for x in range(self.grid_w):
                self._draw_cell(x, y)

        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        self.m.mlx_do_sync(self.mlx_ptr)

    def _draw_cell(self, x: int, y: int) -> None:
        """Draw a single cell with its walls.

        Bit encoding: bit 0=N, bit 1=E, bit 2=S, bit 3=W.
        A set bit means the wall is CLOSED (draw it).

        Args:
            x: x-coordinate in grid.
            y: y-coordinate in grid.
        """
        palette = COLOR_PALETTES[self.palette_idx]
        wall_color = palette[0]

        px = PADDING + x * CELL_SIZE
        py = PADDING + y * CELL_SIZE
        val = self.grid[y][x]

        wall_t = max(1, CELL_SIZE // 10)

        if (x, y) in self.pattern_cells:
            self._fill_rect(
                px, py, CELL_SIZE, CELL_SIZE, wall_color
            )
            return

        if val & 1:  # North wall closed
            self._fill_rect(px, py, CELL_SIZE, wall_t, wall_color)
        if val & 2:  # East wall closed
            self._fill_rect(
                px + CELL_SIZE - wall_t, py,
                wall_t, CELL_SIZE, wall_color,
            )
        if val & 4:  # South wall closed
            self._fill_rect(
                px, py + CELL_SIZE - wall_t,
                CELL_SIZE, wall_t, wall_color,
            )
        if val & 8:  # West wall closed
            self._fill_rect(px, py, wall_t, CELL_SIZE, wall_color)

    def _fill_rect(self, x: int, y: int, w: int, h: int, color: int) -> None:
        """Fill a rectangle in the image buffer.

        Args:
            x: Top-left x-coordinate.
            y: Top-left y-coordinate.
            w: Width of rectangle.
            h: Height of rectangle.
            color: Color value.
        """
        if self.data_view is None:
            return

        blue = color & 0xFF
        green = (color >> 8) & 0xFF
        red = (color >> 16) & 0xFF

        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(self.win_w, x + w)
        y2 = min(self.win_h, y + h)

        for py in range(y1, y2):
            offset_y = py * self.size_line
            for px in range(x1, x2):
                offset = offset_y + px * (self.bpp // 8)
                self.data_view[offset] = blue
                self.data_view[offset + 1] = green
                self.data_view[offset + 2] = red
                self.data_view[offset + 3] = 255
