"""Maze generation algorithms."""
from __future__ import annotations

import random

from mazegen.types import DELTA, OPPOSITE, Direction


def generate_dfs(
    grid: list[list[int]],
    width: int,
    height: int,
    start_x: int,
    start_y: int,
    blocked: set[tuple[int, int]],
    rng: random.Random,
) -> None:
    """Generate maze using Iterative DFS Recursive Backtracker.

    Args:
        grid: The maze grid to modify.
        width: Grid width.
        height: Grid height.
        start_x: Starting x coordinate.
        start_y: Starting y coordinate.
        blocked: Set of coordinates that cannot be visited.
        rng: Random instance for randomness.
    """
    if (start_x, start_y) in blocked:
        return
    visited: set[tuple[int, int]] = {(start_x, start_y)}
    stack: list[tuple[int, int]] = [(start_x, start_y)]

    while stack:
        x, y = stack[-1]
        neighbors: list[tuple[Direction, int, int]] = []
        for d, (dx, dy) in DELTA.items():
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and (nx, ny) not in blocked
                and (nx, ny) not in visited
            ):
                neighbors.append((d, nx, ny))

        if neighbors:
            nd, nx, ny = rng.choice(neighbors)
            grid[y][x] &= ~(1 << nd)
            grid[ny][nx] &= ~(1 << OPPOSITE[nd])
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()

    for y in range(height):
        for x in range(width):
            if (x, y) not in blocked and (x, y) not in visited:
                for d, (dx, dy) in DELTA.items():
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and (nx, ny) in visited
                    ):
                        grid[y][x] &= ~(1 << d)
                        grid[ny][nx] &= ~(1 << OPPOSITE[d])
                        visited.add((x, y))
                        stack.append((x, y))
                        break

                while stack:
                    cx, cy = stack[-1]
                    c_neighbors: list[tuple[Direction, int, int]] = []
                    for cd, (cdx, cdy) in DELTA.items():
                        cnx, cny = cx + cdx, cy + cdy
                        if (
                            0 <= cnx < width
                            and 0 <= cny < height
                            and (cnx, cny) not in blocked
                            and (cnx, cny) not in visited
                        ):
                            c_neighbors.append((cd, cnx, cny))

                    if c_neighbors:
                        ccd, cnx, cny = rng.choice(c_neighbors)
                        grid[cy][cx] &= ~(1 << ccd)
                        grid[cny][cnx] &= ~(1 << OPPOSITE[ccd])
                        visited.add((cnx, cny))
                        stack.append((cnx, cny))
                    else:
                        stack.pop()


def generate_prim(
    grid: list[list[int]],
    width: int,
    height: int,
    start_x: int,
    start_y: int,
    blocked: set[tuple[int, int]],
    rng: random.Random,
) -> None:
    """Generate maze using Randomized Prim's algorithm.

    Args:
        grid: The maze grid to modify.
        width: Grid width.
        height: Grid height.
        start_x: Starting x coordinate.
        start_y: Starting y coordinate.
        blocked: Set of coordinates that cannot be visited.
        rng: Random instance for randomness.
    """
    if (start_x, start_y) in blocked:
        return
    visited: set[tuple[int, int]] = {(start_x, start_y)}
    walls: list[tuple[int, int, Direction, int, int]] = []

    for d, (dx, dy) in DELTA.items():
        nx, ny = start_x + dx, start_y + dy
        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in blocked:
            walls.append((start_x, start_y, d, nx, ny))

    while walls:
        idx = rng.randrange(len(walls))
        x, y, d, nx, ny = walls.pop(idx)

        if (nx, ny) not in visited:
            grid[y][x] &= ~(1 << d)
            grid[ny][nx] &= ~(1 << OPPOSITE[d])
            visited.add((nx, ny))

            for nd, (ndx, ndy) in DELTA.items():
                nnx, nny = nx + ndx, ny + ndy
                if (
                    0 <= nnx < width
                    and 0 <= nny < height
                    and (nnx, nny) not in blocked
                    and (nnx, nny) not in visited
                ):
                    walls.append((nx, ny, nd, nnx, nny))

    for y in range(height):
        for x in range(width):
            if (x, y) not in blocked and (x, y) not in visited:
                for d, (dx, dy) in DELTA.items():
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and (nx, ny) in visited
                    ):
                        grid[y][x] &= ~(1 << d)
                        grid[ny][nx] &= ~(1 << OPPOSITE[d])
                        visited.add((x, y))
                        for nnd, (ndx, ndy) in DELTA.items():
                            nnx, nny = x + ndx, y + ndy
                            if (
                                0 <= nnx < width
                                and 0 <= nny < height
                                and (nnx, nny) not in blocked
                                and (nnx, nny) not in visited
                            ):
                                walls.append((x, y, nnd, nnx, nny))
                        break

                while walls:
                    idx = rng.randrange(len(walls))
                    wx, wy, wd, wnx, wny = walls.pop(idx)
                    if (wnx, wny) not in visited:
                        grid[wy][wx] &= ~(1 << wd)
                        grid[wny][wnx] &= ~(1 << OPPOSITE[wd])
                        visited.add((wnx, wny))
                        for nnd, (ndx, ndy) in DELTA.items():
                            nnx, nny = wnx + ndx, wny + ndy
                            if (
                                0 <= nnx < width
                                and 0 <= nny < height
                                and (nnx, nny) not in blocked
                                and (nnx, nny) not in visited
                            ):
                                walls.append((wnx, wny, nnd, nnx, nny))


class UnionFind:
    """Union-Find data structure for Kruskal's algorithm."""

    def __init__(self, size: int) -> None:
        """Initialize Union-Find with given size.

        Args:
            size: Number of elements.
        """
        self.parent: list[int] = list(range(size))
        self.rank: list[int] = [0] * size

    def find(self, x: int) -> int:
        """Find the root of element x with path compression.

        Args:
            x: Element to find.

        Returns:
            The root identifier.
        """
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        """Union the sets containing x and y.

        Args:
            x: First element.
            y: Second element.

        Returns:
            True if merged, False if already in same set.
        """
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def generate_kruskal(
    grid: list[list[int]],
    width: int,
    height: int,
    blocked: set[tuple[int, int]],
    rng: random.Random,
) -> None:
    """Generate maze using Randomized Kruskal's algorithm.

    Args:
        grid: The maze grid to modify.
        width: Grid width.
        height: Grid height.
        blocked: Set of coordinates that cannot be visited.
        rng: Random instance for randomness.
    """
    uf = UnionFind(width * height)
    edges: list[tuple[int, int, Direction, int, int]] = []

    for y in range(height):
        for x in range(width):
            if (x, y) in blocked:
                continue
            for d in (Direction.EAST, Direction.SOUTH):
                dx, dy = DELTA[d]
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < width
                    and 0 <= ny < height
                    and (nx, ny) not in blocked
                ):
                    edges.append((x, y, d, nx, ny))

    rng.shuffle(edges)

    for x, y, d, nx, ny in edges:
        idx1 = y * width + x
        idx2 = ny * width + nx
        if uf.union(idx1, idx2):
            grid[y][x] &= ~(1 << d)
            grid[ny][nx] &= ~(1 << OPPOSITE[d])
