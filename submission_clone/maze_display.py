"""ASCII and curses display with the required keyboard controls."""
from __future__ import annotations

import sys
from typing import Any

from mazegen import MazeGenerator
from mazegen.constants import EAST, NORTH, SOUTH, WEST


class MazeDisplay:
    """Render a maze and handle regenerate, solution and colour controls."""

    def __init__(self, generator: MazeGenerator, output_file: str) -> None:
        """Keep the generator and output path used by the display."""
        self.generator = generator
        self.output_file = output_file
        self.show_solution = False
        self.wall_color = 0
        self.scroll_x = 0
        self.scroll_y = 0

    def run(self) -> None:
        """Use curses in an interactive terminal, otherwise print ASCII."""
        if not sys.stdout.isatty():
            self._print_ascii()
            return
        try:
            import curses

            curses.wrapper(self._run_curses)
        except Exception as error:
            print(f"Interactive display unavailable: {error}")
            self._print_ascii()

    def _run_curses(self, screen: Any) -> None:
        """Draw the visible portion and handle keys until the user quits."""
        import curses

        screen.keypad(True)
        colors = self._initialize_colors(curses)
        while True:
            lines = self._maze_lines()
            screen.erase()
            height, width = screen.getmaxyx()
            rows = max(0, height - 1)
            columns = max(1, width - 1)
            max_y = max(0, len(lines) - rows)
            max_x = max(0, max(map(len, lines)) - columns)
            self.scroll_y = min(self.scroll_y, max_y)
            self.scroll_x = min(self.scroll_x, max_x)

            for screen_y, source_y in enumerate(
                range(self.scroll_y, min(self.scroll_y + rows, len(lines)))
            ):
                visible = lines[source_y][
                    self.scroll_x:self.scroll_x + columns
                ]
                try:
                    screen.addstr(screen_y, 0, visible, curses.color_pair(1))
                except curses.error:
                    pass

            controls = (
                "R regenerate | S solution | C colour | arrows scroll | Q quit"
            )
            try:
                screen.addnstr(height - 1, 0, controls, columns)
            except curses.error:
                pass
            screen.refresh()

            key = screen.getch()
            if key in (ord("q"), ord("Q"), 27):
                return
            if key in (ord("r"), ord("R")):
                self.generator.generate()
                self.generator.save_to_file(self.output_file)
                self.scroll_x = self.scroll_y = 0
            elif key in (ord("s"), ord("S")):
                self.show_solution = not self.show_solution
            elif key in (ord("c"), ord("C")):
                self.wall_color = (self.wall_color + 1) % len(colors)
                self._change_color(curses, colors)
            elif key == curses.KEY_UP:
                self.scroll_y = max(0, self.scroll_y - 1)
            elif key == curses.KEY_DOWN:
                self.scroll_y += 1
            elif key == curses.KEY_LEFT:
                self.scroll_x = max(0, self.scroll_x - 1)
            elif key == curses.KEY_RIGHT:
                self.scroll_x += 1

    @staticmethod
    def _initialize_colors(curses: Any) -> tuple[int, ...]:
        """Configure wall colours, falling back to white on limited terms."""
        colors = (
            curses.COLOR_CYAN,
            curses.COLOR_YELLOW,
            curses.COLOR_GREEN,
            curses.COLOR_MAGENTA,
        )
        try:
            curses.curs_set(0)
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, colors[0], -1)
        except curses.error:
            return (curses.COLOR_WHITE,)
        return colors

    def _change_color(self, curses: Any, colors: tuple[int, ...]) -> None:
        """Select the next wall colour when the terminal supports colours."""
        try:
            curses.init_pair(1, colors[self.wall_color], -1)
        except curses.error:
            pass

    def _maze_lines(self) -> list[str]:
        """Build aligned ASCII rows with walls and cell markers."""
        grid = self.generator.get_grid()
        solution = (
            set(self.generator.get_solution_path())
            if self.show_solution else set()
        )
        pattern = self.generator.get_pattern_cells()
        lines = []

        for y, row in enumerate(grid):
            north = "+".join("---" if cell & NORTH else "   " for cell in row)
            lines.append("+" + north + "+")

            middle = "|" if row[0] & WEST else " "
            for x, cell in enumerate(row):
                point = (x, y)
                marker = " E " if point == self.generator.entry else "   "
                if point == self.generator.exit:
                    marker = " X "
                elif point in pattern:
                    marker = " 4 "
                elif point in solution:
                    marker = " * "
                middle += marker
                middle += "|" if cell & EAST else " "
            lines.append(middle)

        south = "+".join(
            "---" if cell & SOUTH else "   " for cell in grid[-1]
        )
        lines.append("+" + south + "+")
        return lines

    def _print_ascii(self) -> None:
        """Print the maze and solution when keyboard input is unavailable."""
        self.show_solution = True
        print("A-Maze-ing: E entry, X exit, * shortest path, 4 pattern")
        print(
            "Interactive controls: R regenerate, S solution, C colour, Q quit"
        )
        print("\n".join(self._maze_lines()))
