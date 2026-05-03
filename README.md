# ARC-AGI Program Synthesis via Search Algorithms

> Solving the **ARC-AGI benchmark** — one of AI's hardest reasoning tests — using BFS, Greedy Best-First Search, and A* to synthesize grid-transformation programs from examples.

---

## Overview

The **Abstraction and Reasoning Corpus (ARC-AGI)** challenges AI systems to infer transformation rules from just a few input-output grid examples — a task that stumps most machine learning models. This project tackles it through **program synthesis via heuristic search**:

Given a few training pairs `(input grid → output grid)`, the system searches a space of compositional programs until it finds one that correctly maps every input to its expected output.

Built entirely in **Python** 

---

## How It Works

```
Training Pairs: [(Input Grid, Output Grid), ...]
         │
         ▼
Generate Primitive Operations
  ColorChange, SwapColors, Mirror, Rotate, Scale2x2
         │
         ▼
Search Program Space
  ┌──────────────────────────────┐
  │  BFS    → explore by depth   │
  │  GBFS   → guided by h(prog)  │
  │  A*     → guided by g + h    │
  └──────────────────────────────┘
         │
         ▼
Test program against ALL training pairs
         │
         ▼
Found? → Apply to test input → Output
```

Programs are built by composing primitives into **Sequences** up to a configurable complexity limit. The search terminates as soon as a program correctly maps all training inputs to their expected outputs.

---

## Search Algorithms

### 1. Breadth-First Search (BFS)
Uninformed baseline — explores programs in order of increasing complexity. Guaranteed to find the simplest solution if one exists within the budget.

### 2. Greedy Best-First Search (GBFS)
Informed search using only the heuristic `h(program)`. Prioritizes programs that are already "close" to the correct output — much faster than BFS in practice.

### 3. A* Search
Combines `g` (program complexity / number of ops) with `h` (heuristic score): `f = g + h`. Balances solution quality and search efficiency.

---

## Primitive Operations

| Operation | Description |
|---|---|
| `ColorChange(c1, c2)` | Replace all occurrences of color c1 with c2 |
| `SwapColors(c1, c2)` | Swap all c1 and c2 cells |
| `Mirror(vertical)` | Flip grid left↔right |
| `Mirror(horizontal)` | Flip grid top↔bottom |
| `Rotate(90/180/270)` | Rotate grid by given angle |
| `Scale2x2` | Scale grid to 2× size |
| `Sequence(p1, p2)` | Apply p1 then p2 (composition) |

Programs are composed recursively up to a `max_complexity` depth.

---

## Heuristics

### Heuristic 1 — Cell Mismatch
Counts the total number of cells that differ between the program's output and the expected output across all training pairs. Simple and effective baseline.

```
h(prog) = Σ mismatched_cells(apply(prog, input), expected_output)
```

### Heuristic 2 — Adaptive Meta-Heuristic (Custom)
Extends cell mismatch with adaptive weighting based on structural features of the target grids:

- **Color diversity** — more colors → slightly higher weight
- **Symmetry signals** — if targets are vertically/horizontally/rotationally symmetric, weight adjusts
- **Background ratio** — proportion of zero-cells in target influences weight
- **Op alignment discount** — if the current program already uses ops that match the target's structure (e.g. `Mirror` when target is symmetric), the score gets a small discount

```
h2(prog) = base_mismatch × weight(symmetry, color_diversity, bg_ratio) + nudge(op_alignment)
```

This guides the search toward structurally appropriate programs, not just cell-accurate ones.

---

## Project Structure

```
A1/
├── main.py                  # Entry point — runs all algorithms, prints accuracy & timing
├── search_algorithms.py     # BFS, GBFS, A* implementations
├── heuristics.py            # Cell mismatch + custom adaptive heuristic
├── semantics.py             # apply_program(): executes a program on a grid
├── program.py               # Program data structure + complexity scoring
├── data_loader.py           # Loads ARC-AGI JSON challenge/solution files
├── arc-agi_challenges.json  # ARC-AGI task inputs
└── arc-agi_solutions.json   # ARC-AGI expected outputs
```

---

## Results

Evaluated on **28 ARC-AGI tasks** across all 5 algorithm/heuristic combinations:

| Algorithm | Tasks Solved | Accuracy | Avg Time |
|---|---|---|---|
| BFS (Cell Mismatch) | 14/28 | 50.00% | 0.023s |
| GBFS (Cell Mismatch) | 16/28 | 57.14% | 0.015s |
| A* (Cell Mismatch) | 16/28 | 57.14% | 0.016s |
| GBFS (Custom H2) | 16/28 | 57.14% | 0.020s |
| **A* (Custom H2)** | **17/28** | **60.71%** | **0.016s** |

> 💡 **Key finding:** A* with the custom adaptive heuristic achieved the best accuracy (60.71%) while remaining as fast as the cell-mismatch version. GBFS and A* were both significantly faster than BFS — heuristic guidance cuts through the exponentially growing program space.

---

## Sample Terminal Output

```
Testing Task 2a7b8c3d
BFS Program:  ColorChange(1, 2), Time: 0.000s
GBFS Program: ColorChange(1, 2), Time: 0.000s
A* Program:   ColorChange(1, 2), Time: 0.000s
Expected:     [[0, 2, 0], [0, 0, 0], [0, 0, 0]] 

Testing Task f4e91d2c
BFS Program:  Rotate(90), Time: 0.000s
GBFS Program: Rotate(90), Time: 0.001s
A* Program:   Rotate(90), Time: 0.001s
Expected:     [[0, 2, 0], [5, 3, 1], [0, 4, 0]] 

Testing Task 9d4f6a8e   (composite program needed)
BFS Program:  Sequence(ColorChange(1, 2), Mirror(vertical)), Time: 0.003s
GBFS Program: Sequence(ColorChange(1, 2), Mirror(vertical)), Time: 0.001s
A* Program:   Sequence(ColorChange(1, 2), Mirror(vertical)), Time: 0.002s
Expected:     [[2, 0, 0], [0, 0, 0], [0, 0, 0]] 

Testing Task e8c4b1f6   (BFS fails, heuristic search succeeds)
BFS Program:  None, Time: 0.054s  
GBFS Program: Sequence(Sequence(ColorChange(0, 4), ColorChange(1, 0)), ColorChange(2, 3)), Time: 0.004s 
A* Program:   Sequence(Sequence(ColorChange(0, 4), ColorChange(1, 0)), ColorChange(2, 3)), Time: 0.003s 

================================
ACCURACY SUMMARY
================================
Total Tasks: 28
BFS  (cell) Accuracy: 14/28 (50.00%), Avg Time: 0.023s
GBFS (cell) Accuracy: 16/28 (57.14%), Avg Time: 0.015s
A*   (cell) Accuracy: 16/28 (57.14%), Avg Time: 0.016s
GBFS (H2)   Accuracy: 16/28 (57.14%), Avg Time: 0.020s
A*   (H2)   Accuracy: 17/28 (60.71%), Avg Time: 0.016s
================================
```

> Full terminal output available in `Terminal_Output.pdf`. Full written report in `A1_Report.pdf`.

---

## Getting Started

### Prerequisites
```bash
pip install python>=3.10
```
No external ML libraries required — pure Python.

### Run
```bash
cd A1
python main.py
```

The program loads `arc-agi_challenges.json` and `arc-agi_solutions.json`, runs all 5 algorithm/heuristic combinations on each task, and prints a full accuracy and timing summary:

```
================================
ACCURACY SUMMARY
================================
Total Tasks: N
BFS  (cell) Accuracy: X/N (xx.xx%), Avg Time: 0.xxx s
GBFS (cell) Accuracy: X/N (xx.xx%), Avg Time: 0.xxx s
A*   (cell) Accuracy: X/N (xx.xx%), Avg Time: 0.xxx s
GBFS (H2)   Accuracy: X/N (xx.xx%), Avg Time: 0.xxx s
A*   (H2)   Accuracy: X/N (xx.xx%), Avg Time: 0.xxx s
================================
```

### Configuration (in `main.py`)

| Parameter | Default | Description |
|---|---|---|
| `MAX_COMPLEXITY` | 4 | Max number of ops in a program |
| `BUDGET_SEC` | 0.05 | Time budget per algorithm per task (50ms) |
| `USE_CUSTOM_H2` | True | Enable custom adaptive heuristic |

---

## Key Concepts Demonstrated

- **Program synthesis** — automatically generating programs from input-output examples
- **Heuristic search** — BFS vs. GBFS vs. A* on a structured program space
- **Custom heuristic design** — adaptive weighting using symmetry, color, and structural signals
- **ARC-AGI benchmark** — one of the most challenging AI reasoning benchmarks, designed to require genuine generalization

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![ARC-AGI](https://img.shields.io/badge/Benchmark-ARC--AGI-purple?style=for-the-badge)

> No ML frameworks. Pure search, pure reasoning.

---

