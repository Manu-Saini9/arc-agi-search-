"""ARC Program Synthesis Runner 
--------------------------------------------
Author: Manu Saini
Course: COSC 3P71
Assignment: 1

Purpose
-------
Entry point to load ARC tasks/solutions, run multiple search algorithms (BFS,
GBFS, A*) with selected heuristics, and print accuracy/time summaries.
"""
from __future__ import annotations
import os, time
from typing import List

Grid = List[List[int]]  # local alias

import semantics  # use as semantics.apply_program
from data_loader import load_arc_json
from search_algorithms import bfs_search, gbfs_search, a_star_search
from heuristics import (
    heuristic_cell_mismatch,
    heuristic_custom_2
)

MAX_COMPLEXITY = 4          # runs
BUDGET_SEC     = 0.05       # ~50ms per algorithm per task 
USE_CUSTOM_H2  = True


def pretty_grid(G: Grid) -> str:
    return "[" + ", ".join(str(row) for row in G) + "]"

def run_all(challenges_path="arc-agi_challenges.json",
            solutions_path="arc-agi_solutions.json",
            max_complexity=MAX_COMPLEXITY,
            
            use_custom_h2=USE_CUSTOM_H2):

    # Load tasks/solutions if present; otherwise run a tiny built-in demo
    if os.path.exists(challenges_path) and os.path.exists(solutions_path):
        tasks, solutions = load_arc_json(challenges_path, solutions_path)
    else:
        print("Note: Could not find JSON files; running a tiny demo.\n")
        train_pairs = [(
            [[0,1,0],[1,0,1],[0,1,0]],
            [[2,0,2],[0,2,0],[2,0,2]]
        )]
        test_inputs = [[[0,1,0],[1,0,1],[0,1,0]]]
        tasks = [("demo_2a7b8c3d", train_pairs, test_inputs)]
        solutions = {"demo_2a7b8c3d": [[[2,0,2],[0,2,0],[2,0,2]]]}

    total = len(tasks)

    # accuracy counters
    bfs_correct = gbfs_cell_correct = astar_cell_correct = 0
    gbfs_h1_correct = astar_h1_correct = 0
    gbfs_h2_correct = astar_h2_correct = 0

    # timing accumulators (to show Avg Time like the expected table)
    t_bfs = t_gbfs_cell = t_astar_cell = 0.0
    
    t_gbfs_h2 = t_astar_h2 = 0.0

    for (task_id, train_pairs, test_inputs) in tasks:
        print(f"Testing Task {task_id}")

        # BFS (un-informed) 
        t0 = time.time()
        prog_bfs = bfs_search(train_pairs, max_complexity, time_budget_sec=BUDGET_SEC)
        t1 = time.time(); t_bfs += (t1 - t0)
        if prog_bfs:
            outs_bfs = [semantics.apply_program(ti, prog_bfs) for ti in test_inputs]
            print(f"BFS Program: {prog_bfs}, Time: {t1 - t0:.3f}s")
            for idx, out in enumerate(outs_bfs):
                print(f"Test {idx} Output: {pretty_grid(out)}")
        else:
            print(f"BFS Program: None, Time: {t1 - t0:.3f}s")

        #  GBFS (Cell mismatch heuristic)
        t0 = time.time()
        prog_gbfs_cell = gbfs_search(
            train_pairs, max_complexity, heuristic_cell_mismatch,
            time_budget_sec=BUDGET_SEC
        )
        t1 = time.time(); t_gbfs_cell += (t1 - t0)
        if prog_gbfs_cell:
            outs = [semantics.apply_program(ti, prog_gbfs_cell) for ti in test_inputs]
            print(f"GBFS Program: {prog_gbfs_cell}, Time: {t1 - t0:.3f}s")
            for idx, out in enumerate(outs):
                print(f"Test {idx} Output: {pretty_grid(out)}")
        else:
            print(f"GBFS Program: None, Time: {t1 - t0:.3f}s")

        #  A* (Cell mismatch heuristic)
        # Using the same mismatch heuristic (not admissible), but good for the performance comparison pattern.
        t0 = time.time()
        prog_astar_cell = a_star_search(
            train_pairs, max_complexity, heuristic_cell_mismatch,
            time_budget_sec=BUDGET_SEC
        )
        t1 = time.time(); t_astar_cell += (t1 - t0)
        if prog_astar_cell:
            outs = [semantics.apply_program(ti, prog_astar_cell) for ti in test_inputs]
            print(f"A* Program: {prog_astar_cell}, Time: {t1 - t0:.3f}s")
            for idx, out in enumerate(outs):
                print(f"Test {idx} Output: {pretty_grid(out)}")
        else:
            print(f"A* Program: None, Time: {t1 - t0:.3f}s")


        
        
        #  GBFS (Custom Heuristic )
        if use_custom_h2:
            t0 = time.time()
            prog_gbfs_h2 = gbfs_search(
                train_pairs, max_complexity, heuristic_custom_2,
                time_budget_sec=BUDGET_SEC
            )
            t1 = time.time(); t_gbfs_h2 += (t1 - t0)
            if prog_gbfs_h2:
                outs = [semantics.apply_program(ti, prog_gbfs_h2) for ti in test_inputs]
                print(f"GBFS (Custom Heuristic 2) Program: {prog_gbfs_h2}, Time: {t1 - t0:.3f}s")
                for idx, out in enumerate(outs):
                    print(f"Test {idx} Output: {pretty_grid(out)}")
            else:
                print(f"GBFS (Custom Heuristic 2) Program: None, Time: {t1 - t0:.3f}s")

        #  A* (Custom Heuristic ) 
        if use_custom_h2:
            t0 = time.time()
            prog_astar_h2 = a_star_search(
                train_pairs, max_complexity, heuristic_custom_2,
                time_budget_sec=BUDGET_SEC
            )
            t1 = time.time(); t_astar_h2 += (t1 - t0)
            if prog_astar_h2:
                outs = [semantics.apply_program(ti, prog_astar_h2) for ti in test_inputs]
                print(f"A* (Custom Heuristic 2) Program: {prog_astar_h2}, Time: {t1 - t0:.3f}s")
                for idx, out in enumerate(outs):
                    print(f"Test {idx} Output: {pretty_grid(out)}")
            else:
                print(f"A* (Custom Heuristic 2) Program: None, Time: {t1 - t0:.3f}s")

        #Accuracy records
        expected_list = solutions.get(task_id)
        if expected_list is not None:
            def eq_all(preds: List[Grid]) -> bool:
                return isinstance(preds, list) and preds == expected_list

            if prog_bfs and eq_all([semantics.apply_program(ti, prog_bfs) for ti in test_inputs]):
                bfs_correct += 1
            if prog_gbfs_cell and eq_all([semantics.apply_program(ti, prog_gbfs_cell) for ti in test_inputs]):
                gbfs_cell_correct += 1
            if prog_astar_cell and eq_all([semantics.apply_program(ti, prog_astar_cell) for ti in test_inputs]):
                astar_cell_correct += 1
            
            if use_custom_h2 and 'prog_gbfs_h2' in locals() and prog_gbfs_h2 and eq_all([semantics.apply_program(ti, prog_gbfs_h2) for ti in test_inputs]):
                gbfs_h2_correct += 1
            if use_custom_h2 and 'prog_astar_h2' in locals() and prog_astar_h2 and eq_all([semantics.apply_program(ti, prog_astar_h2) for ti in test_inputs]):
                astar_h2_correct += 1

            print(f"Expected Output(s): {[pretty_grid(g) for g in expected_list]}")
        print()

    #  Summary
    def avg(t: float) -> float:
        return (t / total) if total else 0.0

    print("================================")
    print("ACCURACY SUMMARY")
    print("================================")
    print(f"Total Tasks: {total}")
    print(f"BFS (cell) Accuracy: {bfs_correct}/{total} ({(100.0*bfs_correct/total):.2f}%), Avg Time: {avg(t_bfs):.3f}s")
    print(f"GBFS (cell) Accuracy: {gbfs_cell_correct}/{total} ({(100.0*gbfs_cell_correct/total):.2f}%), Avg Time: {avg(t_gbfs_cell):.3f}s")
    print(f"A*   (cell) Accuracy: {astar_cell_correct}/{total} ({(100.0*astar_cell_correct/total):.2f}%), Avg Time: {avg(t_astar_cell):.3f}s")

    if USE_CUSTOM_H2:
        print(f"GBFS (H2)   Accuracy: {gbfs_h2_correct}/{total} ({(100.0*gbfs_h2_correct/total):.2f}%), Avg Time: {avg(t_gbfs_h2):.3f}s")
        print(f"A*   (H2)   Accuracy: {astar_h2_correct}/{total} ({(100.0*astar_h2_correct/total):.2f}%), Avg Time: {avg(t_astar_h2):.3f}s")
    else:
        print("GBFS (H2)   Accuracy: N/A")
        print("A*   (H2)   Accuracy: N/A")
    print("================================")

if __name__ == "__main__":
    run_all(
        challenges_path="arc-agi_challenges.json",
        solutions_path="arc-agi_solutions.json",
        max_complexity= MAX_COMPLEXITY
    )
