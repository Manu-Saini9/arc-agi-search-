""" We score how "good" a program is. Lower score = better.
These scores help search pick which program to try next.

Author: Manu Saini
Course: COSC 3P71
Assignment: 1

"""
from __future__ import annotations
from typing import List, Tuple, Set
from program import Grid
from semantics import apply_program


# Count how many cells are different between two grids.
# If shapes don't match, we give a big penalty = all cells in target.
def mismatched_cells(G1: Grid, G2: Grid) -> int:
    if not G1 or not G2 or len(G1) != len(G2) or len(G1[0]) != len(G2[0]):
        return len(G2) * (len(G2[0]) if G2 else 0)
    mism = 0
    H, W = len(G2), len(G2[0])
    for i in range(H):
        for j in range(W):
            mism += (G1[i][j] != G2[i][j])
    return mism

# Count how many times each color (0..9) appears.
def color_histogram(grid: Grid) -> List[int]:
    hist = [0] * 10
    for row in grid:
        for v in row:
            if 0 <= v < 10:
                hist[v] += 1
    return hist

# Make a set of colors that appear in the grid (0..9 only).
def _color_set(grid: Grid) -> Set[int]:
    s: Set[int] = set()
    for row in grid:
        for v in row:
            if 0 <= v < 10:
                s.add(v)
    return s

# Count connected groups of non‑zero cells (simply 4‑direction check).
def _count_connected_components(grid: Grid) -> int:
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    seen = [[False]*n for _ in range(m)]

    def bfs(sr, sc):
        from collections import deque
        q = deque([(sr, sc)])
        seen[sr][sc] = True
        while q:
            r, c = q.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < m and 0 <= nc < n and not seen[nr][nc] and grid[nr][nc] != 0:
                    seen[nr][nc] = True
                    q.append((nr, nc))

    comps = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] != 0 and not seen[i][j]:
                comps += 1
                bfs(i, j)
    return comps

# Get grid height and width.
def _shape(g: Grid) -> Tuple[int, int]:
    return (len(g), len(g[0]) if g else 0)

# symmetry helpers methods used in custom heuristics
def _is_vertically_symmetric(g: Grid) -> bool:
    # Same if we flip left↔right
    return all(row == row[::-1] for row in g) if g else True

def _is_horizontally_symmetric(g: Grid) -> bool:
    # Same if we flip top↔bottom
    return g == g[::-1] if g else True

def _rot90(g: Grid) -> Grid:
    # Rotate 90° clockwise
    return [list(col)[::-1] for col in zip(*g)] if g else g

def _is_rotationally_symmetric(g: Grid) -> bool:
    # Same if we rotate 180°
    if not g:
        return True
    r180 = _rot90(_rot90(g))
    return g == r180


# Basic heuristics

# Add up how many cells are wrong across all training examples.
# Lower is better.
def heuristic_cell_mismatch(program, train_pairs: List[Tuple[Grid, Grid]]) -> int:
    s = 0
    for I, O in train_pairs:
        P = apply_program(I, program)
        s += mismatched_cells(P, O)
    return s

# Like above, but if shapes don't match we add a small extra penalty.
# This gently prefers programs that also fix size.
def heuristic_custom(program, train_pairs: List[Tuple[Grid, Grid]]) -> int:
    score = 0
    for I, O in train_pairs:
        P = apply_program(I, program)
        base = mismatched_cells(P, O)
        if _shape(P) == _shape(O):
            score += base
        else:
            score += base + 5
    return score


# Admissible lower bound for A* (counts remaining ops at least)

# Minimum ops needed to fix shape: 0 if same size, else 1 (we assume one resize op could fix it).
def _shape_lb_ops(P: Grid, O: Grid) -> int:
    if _shape(P) == _shape(O):
        return 0
    return 1

# Lower bound: what is the least number of ops we still need?
# We look at missing/extra colors and if shape differs.
# Take the max over all train pairs so we stay a true lower bound.
def heuristic_admissible_ops(program, train_pairs: List[Tuple[Grid, Grid]]) -> int:
    lb = 0
    for I, O in train_pairs:
        P = apply_program(I, program)
        cP = _color_set(P)
        cO = _color_set(O)
        color_lb = max(len(cP - cO), len(cO - cP))
        shape_lb = _shape_lb_ops(P, O)
        lb = max(lb, max(color_lb, shape_lb))
    return lb


# BONUS: Adaptive Meta‑Heuristic (extra guidance)


# Start with cell mismatch. Then adjust the weight using simple signals
# from the targets: symmetry, number of colors, how much background.
# If the program already uses a matching op (Mirror/Rotate/ColorChange/SwapColors),
# we give a tiny discount. Not a strict bound; just guidance.
def heuristic_custom_2(program, train_pairs: List[Tuple[Grid, Grid]]) -> float:
    # 1) Base mismatch
    base = 0
    total_cells = 0
    target_colors: Set[int] = set()
    input_colors: Set[int] = set()
    symmetric_v = symmetric_h = symmetric_r = True
    target_bg_count = 0

    for I, O in train_pairs:
        P = apply_program(I, program)
        base += mismatched_cells(P, O)

        # simple features from targets & inputs
        target_colors |= _color_set(O)
        input_colors  |= _color_set(I)
        symmetric_v = symmetric_v and _is_vertically_symmetric(O)
        symmetric_h = symmetric_h and _is_horizontally_symmetric(O)
        symmetric_r = symmetric_r and _is_rotationally_symmetric(O)

        H, W = _shape(O)
        cells = H * W
        total_cells += cells
        # estimate background: count zeros in target
        target_bg_count += sum(1 for row in O for c in row if c == 0)

    if base == 0:
        return 0.0

    # 2) Build an easy weight
    color_diversity = max(len(target_colors), 1)
    bg_frac = (target_bg_count / total_cells) if total_cells > 0 else 0.0

    weight = 1.0
    weight += 0.15 * (min(color_diversity, 8) / 5.0)   # small bump for many colors
    if symmetric_v: weight += 0.10
    if symmetric_h: weight += 0.10
    if symmetric_r: weight += 0.05
    weight += 0.15 * bg_frac                           # more background → small bump

    # 3) Little discounts if program already uses helpful ops
    prog_s = str(program)
    nudge = 0.0
    if (symmetric_v or symmetric_h) and ("Mirror" in prog_s):
        nudge -= 0.25
    if symmetric_r and ("Rotate" in prog_s):
        nudge -= 0.15
    recolor_needed = (not target_colors.issubset(input_colors)) or (len(target_colors) != len(input_colors))
    if recolor_needed and (("ColorChange" in prog_s) or ("SwapColors" in prog_s)):
        nudge -= 0.10

    # 4) Final score
    weight = max(0.5, weight + nudge)  # keep positive
    return base * weight
