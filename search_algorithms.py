"""Search over Program Space 
-----------------------------------------
Author: Manu Saini
Course: COSC 3P71
Assignment: 1
Reference: Strategy skeletons and operator set adapted from the assignment PDF.

Purpose
-------
Provide simple search baselines (BFS, Greedy Best‑First, A*) to synthesize a
Program that maps each training input grid to its expected output grid.
"""
from __future__ import annotations
from collections import deque
import heapq
import time
from typing import List, Tuple, Callable, Any, Dict

import program as program_mod          
from semantics import apply_program

Program = program_mod.Program  # alias for convenience
Grid = List[List[int]]         # lightweight local alias



def _extract_palette(train_data: List[Tuple[Grid, Grid]]) -> List[int]:
    """Collect colors that actually appear in inputs/outputs of this task."""
    seen = set()
    for inp, out in train_data:
        for G in (inp, out):
            for row in G:
                for v in row:
                    if 0 <= v < 10:
                        seen.add(v)
    # ensure background is present
    seen.add(0)
    return sorted(seen)


def generate_basic_ops(train_data: List[Tuple[Grid, Grid]]) -> List[Program]:
    """
    Generate primitive, single-step operations.
    We bind color-based ops to the palette observed in this task
    to keep branching under control.
    """
    palette = _extract_palette(train_data)
    basics: List[Program] = []

    # ColorChange c1->c2 (exclude identity)
    for c1 in palette:
        for c2 in palette:
            if c1 != c2:
                basics.append(Program("ColorChange", None, (c1, c2)))

    # SwapColors unordered pairs
    for i in range(len(palette)):
        for j in range(i + 1, len(palette)):
            basics.append(Program("SwapColors", None, (palette[i], palette[j])))

    # Mirrors
    basics.append(Program("Mirror", None, "vertical"))
    basics.append(Program("Mirror", None, "horizontal"))

    # Rotations
    basics.append(Program("Rotate", None, 90))
    basics.append(Program("Rotate", None, 180))
    basics.append(Program("Rotate", None, 270))

    # A small set of scale ops (too many would explode the search)
    basics.append(Program("Scale2x2", None, None))

    return basics


def expand_with_basics(prog: Program, basic_ops: List[Program], max_complexity: int):
    """Yield Sequence(prog, b) and Sequence(b, prog) if within max complexity."""
    for b in basic_ops:
        # prog ; b
        c1 = prog.complexity + b.complexity
        if c1 <= max_complexity:
            yield Program("Sequence", prog, b)
        # b ; prog
        c2 = b.complexity + prog.complexity
        if c2 <= max_complexity:
            yield Program("Sequence", b, prog)


def test_program(program: Program, train_data: List[Tuple[Grid, Grid]]) -> bool:
    """True if program maps every input to the expected output."""
    for inp, expected in train_data:
        out = apply_program(inp, program)
        if out != expected:
            return False
    return True

# 1) BFS

def bfs_search(
    train_data: List[Tuple[Grid, Grid]],
    max_complexity: int,
    time_budget_sec: float | None = None
) -> Program | None:
    """Breadth‑First Search by increasing program complexity (shortest in #ops)."""
    start = time.time()
    basic_ops = generate_basic_ops(train_data)

    # Try primitives first (optimal in number of ops if solution is primitive)
    for b in basic_ops:
        if time_budget_sec is not None and (time.time() - start) > time_budget_sec:
            return None
        if test_program(b, train_data):
            return b

    # Layered expansion by complexity
    queue = deque(basic_ops)
    seen: set[str] = set(map(str, basic_ops))

    while queue:
        if time_budget_sec is not None and (time.time() - start) > time_budget_sec:
            return None

        prog = queue.popleft()
        if prog.complexity >= max_complexity:
            continue

        for new_prog in expand_with_basics(prog, basic_ops, max_complexity):
            s = str(new_prog)
            if s in seen:
                continue
            seen.add(s)
            if test_program(new_prog, train_data):
                return new_prog
            queue.append(new_prog)

    return None



# 2) Greedy Best-First Search (GBFS)


def gbfs_search(
    train_data: List[Tuple[Grid, Grid]],
    max_complexity: int,
    heuristic_fn: Callable[[Program, List[Tuple[Grid, Grid]]], int],
    time_budget_sec: float | None = None
) -> Program | None:
    """Greedy Best‑First using only the heuristic h(prog). Lower is better."""
    start = time.time()
    basic_ops = generate_basic_ops(train_data)

    heap: list[tuple[int, int, Program]] = []
    seen: set[str] = set()
    push_id = 0

    # Seed with primitives (priority = h only)
    for b in basic_ops:
        h = heuristic_fn(b, train_data)
        heapq.heappush(heap, (h, push_id, b))
        push_id += 1

    while heap:
        if time_budget_sec is not None and (time.time() - start) > time_budget_sec:
            return None

        h, _, prog = heapq.heappop(heap)
        s = str(prog)
        if s in seen:
            continue
        seen.add(s)

        if test_program(prog, train_data):
            return prog

        if prog.complexity >= max_complexity:
            continue

        for new_prog in expand_with_basics(prog, basic_ops, max_complexity):
            t = str(new_prog)
            if t in seen:
                continue
            hn = heuristic_fn(new_prog, train_data)
            heapq.heappush(heap, (hn, push_id, new_prog))
            push_id += 1

    return None



# 3) A* Search

def a_star_search(
    train_data: List[Tuple[Grid, Grid]],
    max_complexity: int,
    heuristic_fn: Callable[[Program, List[Tuple[Grid, Grid]]], int],
    time_budget_sec: float | None = None
) -> Program | None:
    """A* with f=g+h, where g=#ops (complexity) and h is user‑provided heuristic."""
    start = time.time()
    basic_ops = generate_basic_ops(train_data)

    # f = g + h; we’ll store (f, g, id, prog)
    heap: list[tuple[int, int, int, Program]] = []
    seen: set[str] = set()
    push_id = 0

    for b in basic_ops:
        g = b.complexity
        h = heuristic_fn(b, train_data)
        f = g + h
        heapq.heappush(heap, (f, g, push_id, b))
        push_id += 1

    while heap:
        if time_budget_sec is not None and (time.time() - start) > time_budget_sec:
            return None

        f, g, _, prog = heapq.heappop(heap)
        s = str(prog)
        if s in seen:
            continue
        seen.add(s)

        if test_program(prog, train_data):
            return prog

        if prog.complexity >= max_complexity:
            continue

        for new_prog in expand_with_basics(prog, basic_ops, max_complexity):
            t = str(new_prog)
            if t in seen:
                continue
            g2 = new_prog.complexity
            h2 = heuristic_fn(new_prog, train_data)
            f2 = g2 + h2
            heapq.heappush(heap, (f2, g2, push_id, new_prog))
            push_id += 1

    return None
