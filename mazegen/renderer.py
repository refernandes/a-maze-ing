"""Interactive ASCII renderer for the maze."""
from __future__ import annotations

import sys
from typing import Any, Callable


class MazeRenderer:
    """Display the maze in a terminal and handle its required controls."""

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
        """Save the maze data and the function used to generate another one.

        Args:
            grid: Maze cells encoded as wall masks.
            width: Number of columns.
            height: Number of rows.
            entry: Start coordinate.
            exit_pos: End coordinate.
            solution_path: Shortest path from entry to exit.
            pattern_cells: Cells that draw the 42 pattern.
            regenerate_callback: Function that returns a new grid and path.
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
        self.theme_idx = 0

    def run(self) -> None:
        """Start the interactive terminal display or print static ASCII."""
        self._run_curses_or_ascii()

    def _run_curses_or_ascii(self) -> None:
        """Use curses for keyboard controls, with a static ASCII fallback."""
        if not sys.stdout.isatty():
            self._ascii_fallback()
            return

        try:
            import curses

            curses.wrapper(self._curses_main)
        except Exception as exc:
            print(
                f"Terminal renderer unavailable ({exc}); "
                "showing a static maze instead.",
                file=sys.stderr,
            )
            self._ascii_fallback()

    def _curses_main(self, stdscr: Any) -> None:
        """Draw the maze and respond to the required keyboard controls."""
        import curses

        try:
            curses.curs_set(0)
        except curses.error:
            pass

        stdscr.keypad(True)
        curses.start_color()
        curses.use_default_colors()

        wall_colors = (
            curses.COLOR_CYAN,
            curses.COLOR_YELLOW,
            curses.COLOR_GREEN,
        )
        curses.init_pair(1, wall_colors[self.theme_idx], -1)
        curses.init_pair(2, curses.COLOR_BLUE, -1)
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)

        def put(row: int, column: int, text: str, attr: int = 0) -> None:
            """Write text and ignore positions outside a small terminal."""
            try:
                stdscr.addstr(row, column, text, attr)
            except curses.error:
                pass

        while True:
            stdscr.clear()
            screen_height, screen_width = stdscr.getmaxyx()
            required_width = self.grid_w * 4 + 4
            required_height = self.grid_h * 2 + 4
            if (
                screen_width < required_width
                or screen_height < required_height
            ):
                messages = (
                    "Terminal too small.",
                    f"Required: {required_width}x{required_height}; "
                    f"current: {screen_width}x{screen_height}.",
                    "Enlarge terminal or reduce maze.",
                    "Q quits; any other key retries.",
                )
                for row, message in enumerate(messages):
                    put(row, 0, message[:max(0, screen_width - 1)])
                stdscr.refresh()
                key = stdscr.getch()
                if key in (ord("q"), ord("Q"), 27):
                    break
                continue

            title = " A-Maze-ing - ASCII Maze "
            controls = "[R]egenerate [S]olution [C]olor [Q]uit"
            put(0, max(0, (screen_width - len(title)) // 2), title,
                curses.A_BOLD)
            put(1, max(0, (screen_width - len(controls)) // 2), controls,
                curses.A_DIM)

            start_row, start_column = 3, 2
            wall_attr = curses.color_pair(1)
            for row, line in enumerate(
                self._ascii_lines(self.show_solution), start=start_row
            ):
                put(row, start_column, line, wall_attr)

            solution = set(self.solution_path) if self.show_solution else set()
            for y in range(self.grid_h):
                for x in range(self.grid_w):
                    marker = self._cell_marker((x, y), solution)
                    if marker == "   ":
                        continue

                    attr = wall_attr
                    if (x, y) == self.entry:
                        attr = curses.color_pair(3) | curses.A_BOLD
                    elif (x, y) == self.exit_pos:
                        attr = curses.color_pair(4) | curses.A_BOLD
                    elif (x, y) in solution:
                        attr = curses.color_pair(2) | curses.A_BOLD

                    put(
                        start_row + 2 * y + 1,
                        start_column + 1 + 4 * x,
                        marker,
                        attr,
                    )

            stdscr.refresh()
            key = stdscr.getch()
            if key in (ord("q"), ord("Q"), 27):
                break
            if key in (ord("r"), ord("R")):
                self.grid, self.solution_path = self.regenerate_callback()
            elif key in (ord("s"), ord("S")):
                self.show_solution = not self.show_solution
            elif key in (ord("c"), ord("C")):
                self.theme_idx = (self.theme_idx + 1) % len(wall_colors)
                curses.init_pair(1, wall_colors[self.theme_idx], -1)

    def _cell_marker(
        self,
        position: tuple[int, int],
        solution: set[tuple[int, int]],
    ) -> str:
        """Return the label for an entry, exit, 42 cell or solution cell."""
        if position == self.entry:
            return " E "
        if position == self.exit_pos:
            return " X "
        if position in self.pattern_cells:
            return " 4 "
        if position in solution:
            return " * "
        return "   "

    def _horizontal_line(self, row: int) -> str:
        """Draw the horizontal walls above the given grid row."""
        pieces = ["+"]
        for x in range(self.grid_w):
            if row == 0:
                closed = bool(self.grid[0][x] & 1)
            elif row == self.grid_h:
                closed = bool(self.grid[self.grid_h - 1][x] & 4)
            else:
                closed = bool(self.grid[row - 1][x] & 4)
            pieces.extend(("---" if closed else "   ", "+"))
        return "".join(pieces)

    def _middle_line(
        self,
        row: int,
        solution: set[tuple[int, int]],
    ) -> str:
        """Draw the cell labels and vertical walls for one grid row."""
        pieces = ["|" if self.grid[row][0] & 8 else " "]
        for x in range(self.grid_w):
            pieces.append(self._cell_marker((x, row), solution))
            if x == self.grid_w - 1:
                closed = bool(self.grid[row][x] & 2)
            else:
                closed = bool(
                    self.grid[row][x] & 2
                    or self.grid[row][x + 1] & 8
                )
            pieces.append("|" if closed else " ")
        return "".join(pieces)

    def _ascii_lines(self, show_solution: bool) -> list[str]:
        """Build the complete ASCII maze, optionally marking its solution."""
        solution = set(self.solution_path) if show_solution else set()
        lines: list[str] = []
        for row in range(self.grid_h):
            lines.append(self._horizontal_line(row))
            lines.append(self._middle_line(row, solution))
        lines.append(self._horizontal_line(self.grid_h))
        return lines

    def _ascii_fallback(self) -> None:
        """Print a static maze and solution when no keyboard is available."""
        print("=== A-Maze-ing ASCII Display ===")
        print("Legend: E=entry  X=exit  *=shortest path  4='42' pattern")
        for line in self._ascii_lines(show_solution=True):
            print(line)
