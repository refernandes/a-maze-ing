"""GUI and Terminal interactive maze renderer for École 42."""
from __future__ import annotations

import os
import sys
from typing import Callable, Any

try:
    import tkinter as tk
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False


# Theme definitions (wall, path, bg, entry, exit, pattern)
GUI_THEMES: list[dict[str, str]] = [
    {
        "name": "Cyberpunk",
        "bg": "#1a1a2e",
        "wall": "#00d2d3",
        "path": "#54a0ff",
        "entry": "#10ac84",
        "exit": "#ee5253",
        "pattern": "#ff9ff3",
        "text": "#ffffff",
    },
    {
        "name": "Sunset",
        "bg": "#2d3436",
        "wall": "#ffe66d",
        "path": "#ff7675",
        "entry": "#55efc4",
        "exit": "#fd79a8",
        "pattern": "#a29bfe",
        "text": "#ffffff",
    },
    {
        "name": "Matrix",
        "bg": "#0d0d0d",
        "wall": "#00ff66",
        "path": "#009933",
        "entry": "#ffffff",
        "exit": "#ff3333",
        "pattern": "#ffff00",
        "text": "#00ff66",
    },
]

CELL_SIZE = 24
PADDING = 20


class MazeRenderer:
    """Hybrid GUI (Tkinter 2D Window) and Terminal (Curses) renderer."""

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
        animated_regenerate_callback: Callable[
            [Callable[[list[list[int]], tuple[int, int]], None]],
            tuple[list[list[int]], list[tuple[int, int]]],
        ] | None = None,
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
            animated_regenerate_callback: Optional animated callback.
        """
        self.grid = grid
        self.grid_w = width
        self.grid_h = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.solution_path = solution_path
        self.pattern_cells = pattern_cells
        self.regenerate_callback = regenerate_callback
        self.animated_regenerate_callback = animated_regenerate_callback

        self.show_solution = False
        self.theme_idx = 0
        self.highlight_pattern = True
        self.animate_gen = True

    def run(self) -> None:
        """Run the graphical GUI or fallback to terminal."""
        if HAS_TKINTER and self._can_open_display():
            try:
                self._run_tkinter_gui()
                return
            except Exception:
                pass

        self._run_curses_or_ascii()

    def _can_open_display(self) -> bool:
        """Check if X11 display is available for Tkinter GUI."""
        if sys.platform.startswith("win"):
            return True
        disp = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        return bool(disp)

    def _run_tkinter_gui(self) -> None:
        """Launch 2D graphical Tkinter GUI Window."""
        root = tk.Tk()
        root.title("A-Maze-ing Maze Generator & Solver (École 42)")

        canvas_w = self.grid_w * CELL_SIZE + PADDING * 2
        canvas_h = self.grid_h * CELL_SIZE + PADDING * 2

        control_frame = tk.Frame(root, bg="#222222", bd=2, relief=tk.RAISED)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        theme_bg = GUI_THEMES[self.theme_idx]["bg"]
        canvas = tk.Canvas(
            root, width=canvas_w, height=canvas_h, bg=theme_bg
        )
        canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        def redraw() -> None:
            theme = GUI_THEMES[self.theme_idx]
            canvas.config(bg=theme["bg"])
            canvas.delete("all")

            sol_set = set(self.solution_path) if self.show_solution else set()

            # Draw cell backgrounds (entry, exit, pattern, solution)
            for y in range(self.grid_h):
                for x in range(self.grid_w):
                    pos = (x, y)
                    px = PADDING + x * CELL_SIZE
                    py = PADDING + y * CELL_SIZE

                    color = None
                    if pos == self.entry:
                        color = theme["entry"]
                    elif pos == self.exit_pos:
                        color = theme["exit"]
                    elif self.highlight_pattern and pos in self.pattern_cells:
                        color = theme["pattern"]
                    elif pos in sol_set:
                        color = theme["path"]

                    if color:
                        canvas.create_rectangle(
                            px, py, px + CELL_SIZE, py + CELL_SIZE,
                            fill=color, outline=""
                        )

            # Draw walls (Bit encoding: 0=N, 1=E, 2=S, 3=W)
            wall_color = theme["wall"]
            wall_t = max(2, CELL_SIZE // 10)

            for y in range(self.grid_h):
                for x in range(self.grid_w):
                    cell = self.grid[y][x]
                    px = PADDING + x * CELL_SIZE
                    py = PADDING + y * CELL_SIZE

                    if cell & 1:  # North
                        canvas.create_line(
                            px, py, px + CELL_SIZE, py,
                            fill=wall_color, width=wall_t
                        )
                    if cell & 2:  # East
                        canvas.create_line(
                            px + CELL_SIZE, py, px + CELL_SIZE, py + CELL_SIZE,
                            fill=wall_color, width=wall_t
                        )
                    if cell & 4:  # South
                        canvas.create_line(
                            px, py + CELL_SIZE, px + CELL_SIZE, py + CELL_SIZE,
                            fill=wall_color, width=wall_t
                        )
                    if cell & 8:  # West
                        canvas.create_line(
                            px, py, px, py + CELL_SIZE,
                            fill=wall_color, width=wall_t
                        )

            # Labels for Entry (E) and Exit (X)
            ex, ey = self.entry
            canvas.create_text(
                PADDING + ex * CELL_SIZE + CELL_SIZE // 2,
                PADDING + ey * CELL_SIZE + CELL_SIZE // 2,
                text="E", fill="#ffffff", font=("Helvetica", 12, "bold")
            )
            xx, xy = self.exit_pos
            canvas.create_text(
                PADDING + xx * CELL_SIZE + CELL_SIZE // 2,
                PADDING + xy * CELL_SIZE + CELL_SIZE // 2,
                text="X", fill="#ffffff", font=("Helvetica", 12, "bold")
            )

        def do_regenerate() -> None:
            if self.animate_gen and self.animated_regenerate_callback:
                def anim_step(
                    grid: list[list[int]], curr: tuple[int, int]
                ) -> None:
                    self.grid = grid
                    redraw()
                    root.update()

                self.grid, self.solution_path = (
                    self.animated_regenerate_callback(anim_step)
                )
            else:
                self.grid, self.solution_path = self.regenerate_callback()
            redraw()

        def toggle_solution() -> None:
            self.show_solution = not self.show_solution
            redraw()

        def cycle_theme() -> None:
            self.theme_idx = (self.theme_idx + 1) % len(GUI_THEMES)
            redraw()

        def toggle_pattern() -> None:
            self.highlight_pattern = not self.highlight_pattern
            redraw()

        def toggle_anim() -> None:
            self.animate_gen = not self.animate_gen
            btn_anim.config(
                text=f"Animation: {'ON' if self.animate_gen else 'OFF'}"
            )

        # Control Toolbar Buttons
        btn_regen = tk.Button(
            control_frame, text="↻ Regenerate (R)", command=do_regenerate,
            bg="#0984e3", fg="#ffffff", font=("Helvetica", 10, "bold")
        )
        btn_regen.pack(side=tk.LEFT, padx=5, pady=5)

        btn_sol = tk.Button(
            control_frame, text="✦ Solution (S)", command=toggle_solution,
            bg="#6c5ce7", fg="#ffffff", font=("Helvetica", 10, "bold")
        )
        btn_sol.pack(side=tk.LEFT, padx=5, pady=5)

        btn_theme = tk.Button(
            control_frame, text="🎨 Theme (C)", command=cycle_theme,
            bg="#fdcb6e", fg="#2d3436", font=("Helvetica", 10, "bold")
        )
        btn_theme.pack(side=tk.LEFT, padx=5, pady=5)

        btn_pat = tk.Button(
            control_frame, text="★ '42' (P)", command=toggle_pattern,
            bg="#e84393", fg="#ffffff", font=("Helvetica", 10, "bold")
        )
        btn_pat.pack(side=tk.LEFT, padx=5, pady=5)

        btn_anim = tk.Button(
            control_frame, text="Animation: ON", command=toggle_anim,
            bg="#00b894", fg="#ffffff", font=("Helvetica", 10, "bold")
        )
        btn_anim.pack(side=tk.LEFT, padx=5, pady=5)

        # Keyboard shortcuts
        root.bind("<r>", lambda e: do_regenerate())
        root.bind("<R>", lambda e: do_regenerate())
        root.bind("<s>", lambda e: toggle_solution())
        root.bind("<S>", lambda e: toggle_solution())
        root.bind("<c>", lambda e: cycle_theme())
        root.bind("<C>", lambda e: cycle_theme())
        root.bind("<p>", lambda e: toggle_pattern())
        root.bind("<P>", lambda e: toggle_pattern())
        root.bind("<Escape>", lambda e: root.destroy())

        redraw()
        root.mainloop()

    def _run_curses_or_ascii(self) -> None:
        """Run the interactive terminal renderer or a static ASCII view.

        A redirected stdout is not interactive, so trying to read keyboard
        input there would hang automated checks.  In that situation we print a
        complete wall diagram and the solution path instead.
        """
        if not sys.stdout.isatty():
            self._ascii_fallback()
            return

        try:
            import curses

            curses.wrapper(self._curses_main)
        except Exception:
            # Some minimal terminals do not provide a usable curses screen.
            # The project must still display something useful instead of
            # failing after the maze file has already been generated.
            self._ascii_fallback()

    def _curses_main(self, stdscr: Any) -> None:
        """Draw the complete wall diagram and process keyboard commands."""
        import curses

        try:
            curses.curs_set(0)
        except curses.error:
            # A few terminals do not support hiding the cursor; this is only
            # cosmetic, so the visualizer can continue safely.
            pass
        stdscr.nodelay(False)
        stdscr.keypad(True)
        curses.start_color()
        curses.use_default_colors()

        # Pair 1 is deliberately reinitialized when the user presses C.  The
        # other pairs keep stable semantic roles: solution, entry, exit, 42.
        wall_colors = (
            curses.COLOR_CYAN,
            curses.COLOR_YELLOW,
            curses.COLOR_GREEN,
        )
        curses.init_pair(1, wall_colors[self.theme_idx], -1)
        curses.init_pair(2, curses.COLOR_BLUE, -1)
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)

        def put(row: int, column: int, text: str, attr: int = 0) -> None:
            """Write text without crashing when it reaches the screen edge."""
            try:
                stdscr.addstr(row, column, text, attr)
            except curses.error:
                pass

        while True:
            stdscr.clear()
            max_y, max_x = stdscr.getmaxyx()

            title = " A-Maze-ing (École 42) - Terminal Renderer "
            put(0, max(0, (max_x - len(title)) // 2), title, curses.A_BOLD)

            ctrls = (
                "[R]egenerate  [S]olution  [C]olor  [4/P]attern  [Q]uit"
            )
            put(1, max(0, (max_x - len(ctrls)) // 2), ctrls, curses.A_DIM)

            start_y, start_x = 3, 2
            wall_attr = curses.color_pair(1)
            # The maze uses two terminal rows per logical row: one for north/
            # south walls and one for the cell contents and vertical walls.
            for line_no, line in enumerate(
                self._ascii_lines(self.show_solution), start=start_y
            ):
                put(line_no, start_x, line, wall_attr)

            # Markers are drawn over the structural diagram so their semantic
            # colours remain visible without losing any wall information.
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
                    elif (
                        self.highlight_pattern and (x, y) in self.pattern_cells
                    ):
                        attr = curses.color_pair(5) | curses.A_BOLD
                    elif (x, y) in solution:
                        attr = curses.color_pair(2) | curses.A_BOLD
                    put(start_y + 2 * y + 1, start_x + 1 + 4 * x,
                        marker, attr)

            stdscr.refresh()
            ch = stdscr.getch()
            if ch in (ord("q"), ord("Q"), 27):
                break
            elif ch in (ord("r"), ord("R")):
                self.grid, self.solution_path = self.regenerate_callback()
            elif ch in (ord("s"), ord("S")):
                self.show_solution = not self.show_solution
            elif ch in (ord("c"), ord("C")):
                self.theme_idx = (self.theme_idx + 1) % len(GUI_THEMES)
                curses.init_pair(1, wall_colors[self.theme_idx], -1)
            elif ch in (ord("p"), ord("P"), ord("4")):
                self.highlight_pattern = not self.highlight_pattern

    def _cell_marker(
        self,
        position: tuple[int, int],
        solution: set[tuple[int, int]],
    ) -> str:
        """Return a three-character label to place inside one cell.

        Three characters keep the diagram aligned with the ``+---+`` wall
        segments.  Entry and exit win over the solution marker so they remain
        obvious even when the shortest path starts or ends there.
        """
        if position == self.entry:
            return " E "
        if position == self.exit_pos:
            return " X "
        if position in self.pattern_cells:
            return " 4 " if self.highlight_pattern else "   "
        if position in solution:
            return " * "
        return "   "

    def _horizontal_line(self, row: int) -> str:
        """Build one horizontal wall line of the ASCII representation."""
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

    def _middle_line(self, row: int, solution: set[tuple[int, int]]) -> str:
        """Build one row containing cell labels and vertical walls."""
        first = self.grid[row][0]
        pieces = ["|" if first & 8 else " "]
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
        """Return a complete, wall-accurate diagram for any text terminal."""
        solution = set(self.solution_path) if show_solution else set()
        lines: list[str] = []
        for row in range(self.grid_h):
            lines.append(self._horizontal_line(row))
            lines.append(self._middle_line(row, solution))
        lines.append(self._horizontal_line(self.grid_h))
        return lines

    def _ascii_fallback(self) -> None:
        """Print a static wall diagram when keyboard input is unavailable."""
        print("=== A-Maze-ing ASCII Display ===")
        print("Legend: E=entry  X=exit  *=shortest path  4='42' pattern")
        # A non-interactive output should still demonstrate the complete
        # solution, making ``python3 ... > preview.txt`` useful in CI.
        for line in self._ascii_lines(show_solution=True):
            print(line)
