"""ARC Data Loader 
-----------------------------------
Author: Manu Saini
Course: COSC 3P71
Assignment: 1
Reference: Based on the assignment PDF.
Purpose
------------------------------------
It reads tasks and answers from JSON files and converts them into one
clean format so the rest of the code can use them easily.
- "challenges" → list of (task_id, training pairs, test inputs)
- "solutions" → dict: task_id → list of correct output grids
"""
from __future__ import annotations
import json
from typing import List, Dict, Tuple
from typing import List, Dict, Tuple   # kept as-is
Grid = List[List[int]]                 # a grid is a list of rows of ints
TrainPair = Tuple[Grid, Grid]          # (input_grid, output_grid)


def _load_json_flexible(path: str):
    """Load either JSON or JSONL (one JSON object per line)."""
    # Try: read the whole file as one JSON object
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read().strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # If that fails, treat it as JSONL (read many lines, each is JSON)
        objs = []
        with open(path, "r", encoding="utf-8") as f2:
            for line in f2:
                line = line.strip()
                if not line:
                    continue
                objs.append(json.loads(line))
        return objs


def _normalize_challenges(challenges_obj):
    """
    Make a clean list of: (task_id, train_pairs, test_inputs)
      - train_pairs: list of (Grid, Grid)
      - test_inputs: list of Grid
    Accepts different input shapes/field names.
    """
    tasks = []

    # Pick the list of task items (handle dict or list forms)
    if isinstance(challenges_obj, dict):
        if "tasks" in challenges_obj and isinstance(challenges_obj["tasks"], list):
            items = challenges_obj["tasks"]
        else:
            # Convert a dict like {id: task_dict} into a list of task_dicts
            items = []
            for k, v in challenges_obj.items():
                if isinstance(v, dict):
                    vv = dict(v)
                    vv.setdefault("task_id", k)
                    items.append(vv)
    else:
        items = challenges_obj

    # Walk over tasks and pull out fields using common names
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue

        tid = item.get("task_id") or item.get("id") or f"task_{idx}"

        # Training examples (pairs of input/output grids)
        train_pairs: List[TrainPair] = []
        train_list = item.get("train") or item.get("train_examples") or []
        for ex in train_list:
            if not isinstance(ex, dict):
                continue
            I = ex.get("input") if "input" in ex else ex.get("in")
            O = ex.get("output") if "output" in ex else ex.get("out")
            if I is not None and O is not None:
                train_pairs.append((I, O))

        # Test inputs (may be a list or a single dict)
        test_inputs: List[Grid] = []
        test_obj = item.get("test") or item.get("test_examples") or item.get("test_example")
        if isinstance(test_obj, list):
            for t in test_obj:
                if isinstance(t, dict):
                    ti = t.get("input") or t.get("in")
                    if ti is not None:
                        test_inputs.append(ti)
        elif isinstance(test_obj, dict):
            ti = test_obj.get("input") or test_obj.get("in")
            if ti is not None:
                test_inputs.append(ti)
        else:
            # Sometimes the test input is directly on the task
            ti = item.get("test_input")
            if ti is not None:
                test_inputs.append(ti)

        # Only keep tasks that actually have test inputs
        if test_inputs:
            tasks.append((tid, train_pairs, test_inputs))

    return tasks


def _normalize_solutions(solutions_obj):
    """
    Make a dict: task_id -> list of expected output grids.
    Accepts different input shapes/field names.
    """
    out: Dict[str, List[Grid]] = {}

    # If we got a dict, it might be {"solutions": [...]} or {id: ...}
    if isinstance(solutions_obj, dict):
        if "solutions" in solutions_obj:
            solutions_obj = solutions_obj["solutions"]
        else:
            # Handle many possible forms per id
            #   id -> grid | [grids] | {"output": grid} | {"test": {"output": grid}}
            for k, v in solutions_obj.items():
                if isinstance(v, dict):
                    grid = v.get("output")
                    if grid is None and isinstance(v.get("test"), dict):
                        grid = v["test"].get("output")
                else:
                    grid = v
                if grid is None:
                    continue
                # Normalize to a list of grids
                if (isinstance(grid, list) and grid and isinstance(grid[0], list)
                        and isinstance(grid[0][0], list)):
                    out[k] = grid
                else:
                    out[k] = [grid]
            return out

    # If we got a list, each item should name a task and give an output
    if isinstance(solutions_obj, list):
        for item in solutions_obj:
            if not isinstance(item, dict):
                continue
            tid = item.get("task_id") or item.get("id")
            if tid is None:
                continue
            grid = item.get("output") or (item.get("test") or {}).get("output")
            if grid is None:
                continue
            if (isinstance(grid, list) and grid and isinstance(grid[0], list)
                    and isinstance(grid[0][0], list)):
                out[tid] = grid
            else:
                out[tid] = [grid]
    return out


def load_arc_json(challenges_path: str, solutions_path: str):
    """Public function: read files, normalize them, and return (tasks, solutions)."""
    # Read raw JSON/JSONL
    challenges_obj = _load_json_flexible(challenges_path)
    solutions_obj  = _load_json_flexible(solutions_path)

    # Convert to the clean, standard shapes we use elsewhere
    tasks = _normalize_challenges(challenges_obj)
    solutions = _normalize_solutions(solutions_obj)

    # Basic checks: fail early if something is wrong
    if not tasks:
        raise ValueError("Could not parse challenges.")
    if not solutions:
        raise ValueError("Could not parse solutions.")
    return tasks, solutions
