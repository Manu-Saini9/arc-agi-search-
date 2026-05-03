"""Semantics: apply a Program to a Grid 
-------------------------------------------------------
Author: Manu Saini
Course: COSC 3P71
Assignment: 1
Reference: Based on the assignment PDF.
Purpose
------------------------------------
It takes a program and input grid, and returns a new grid after
running the operations. If the Program is a Sequence, it runs the left part
first, then the right part.
"""
from __future__ import annotations
from typing import List
from program import Program

Grid = List[List[int]]


def apply_program(input_grid: Grid, program: Program) -> Grid:
    """Apply a Program (primitive or Sequence) to an input grid and return the result."""
    if program is None:
        return input_grid

    # Work on a copy so we don't change the original input
    grid = [row[:] for row in input_grid]
    op = program.op      # the operation name
    args = program.right # parameters for leaf ops (or right child if Sequence)

    if op == 'ColorChange':
        # Change all cells with old_color to new_color
        old_color, new_color = args
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == old_color:
                    grid[i][j] = new_color

    elif op == 'Mirror':
        # Flip the grid horizontally or vertically
        axis = args
        if axis == 'horizontal':
            grid = grid[::-1]
        elif axis == 'vertical':
            grid = [row[::-1] for row in grid]

    elif op == 'Rotate':
        # Rotate the grid by 90/180/270 degrees clockwise
        degrees = args
        m, n = len(grid), len(grid[0])
        if degrees == 90:
            grid = [[grid[m - 1 - j][i] for j in range(m)] for i in range(n)]
        elif degrees == 180:
            grid = [row[::-1] for row in grid[::-1]]
        elif degrees == 270:
            grid = [[grid[j][n - 1 - i] for j in range(m)] for i in range(n)]

    elif op == 'Scale2x2':
        # Make each cell into a 2x2 block
        new_grid: Grid = []
        for row in grid:
            r1, r2 = [], []
            for v in row:
                r1.extend([v, v])
                r2.extend([v, v])
            new_grid.append(r1)
            new_grid.append(r2)
        grid = new_grid

    elif op == 'Scale3x3':
        # Make each cell into a 3x3 block
        new_grid: Grid = []
        for row in grid:
            r1, r2, r3 = [], [], []
            for v in row:
                r1.extend([v, v, v])
                r2.extend([v, v, v])
                r3.extend([v, v, v])
            new_grid.extend([r1, r2, r3])
        grid = new_grid

    elif op == 'Scale2x1':
        # Stretch horizontally by 2 (duplicate columns)
        new_grid: Grid = []
        for row in grid:
            new_row = []
            for v in row:
                new_row.extend([v, v])
            new_grid.append(new_row)
        grid = new_grid

    elif op == 'Scale1x2':
        # Stretch vertically by 2 (duplicate rows)
        new_grid: Grid = []
        for row in grid:
            new_grid.append(row[:])
            new_grid.append(row[:])
        grid = new_grid

    elif op == 'ResizeIrregular':
        # Resize to (hnew, wnew) by clamping indices
        hnew, wnew = args
        m, n = len(grid), len(grid[0])
        new_grid: Grid = []
        for i in range(hnew):
            new_row = []
            for j in range(wnew):
                oi = min(i, m - 1)
                oj = min(j, n - 1)
                new_row.append(grid[oi][oj])
            new_grid.append(new_row)
        grid = new_grid

    elif op == 'PositionalShift':
        # Move all cells of old_color by (dr, dc); write new_color; 0 = background
        old_color, new_color, dr, dc = args
        m, n = len(grid), len(grid[0])
        Gp = [row[:] for row in grid]
        for r in range(m):
            for c in range(n):
                if grid[r][c] == old_color:
                    Gp[r][c] = 0  # clear from old spot
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n:
                        Gp[nr][nc] = new_color
        grid = Gp

    elif op == 'ColorMapMultiple':
        # Change many colors at once using a dictionary mapping
        cmap = dict(args)  # tuple of pairs -> dict
        m, n = len(grid), len(grid[0])
        Gp = [row[:] for row in grid]
        for r in range(m):
            for c in range(n):
                if Gp[r][c] in cmap:
                    Gp[r][c] = cmap[Gp[r][c]]
        grid = Gp

    elif op == 'ScaleWithColorMap':
        # Scale by s and also remap colors using cmap during scaling
        s, cmap = args[0], dict(args[1])
        m, n = len(grid), len(grid[0])
        new_grid: Grid = []
        for i in range(m):
            for _ in range(s):
                new_row = []
                for j in range(n):
                    val = grid[i][j]
                    mapped = cmap.get(val, val)
                    for _ in range(s):
                        new_row.append(mapped)
                new_grid.append(new_row)
        grid = new_grid

    elif op == 'SwapColors':
        # Swap two colors everywhere in the grid
        c1, c2 = args
        m, n = len(grid), len(grid[0])
        Gp = [row[:] for row in grid]
        for r in range(m):
            for c in range(n):
                if Gp[r][c] == c1:
                    Gp[r][c] = c2
                elif Gp[r][c] == c2:
                    Gp[r][c] = c1
        grid = Gp

    elif op == 'DiagonalReflection':
        # Reflect old_color across the main diagonal and paint new_color
        old_color, new_color = args
        m, n = len(grid), len(grid[0])
        Gp = [row[:] for row in grid]
        for r in range(m):
            for c in range(n):
                if grid[r][c] == old_color:
                    Gp[r][c] = 0
                    if c < m and r < n:
                        Gp[c][r] = new_color
        grid = Gp

    elif op == 'Sequence':
        # Run the left program first, then the right program
        grid = apply_program(grid, program.left)
        grid = apply_program(grid, program.right)

    return grid