"""Program class 
----------------------------------
Author: Manu Saini
Course: COSC 3P71
Assignment: 1
Reference: Based on the assignment PDF.

Purpose
------------------------------------
This class describes a small program that changes a grid.
A program can be:
- a single action like change color, rotate, mirror or
- a sequence of two smaller programs.

We also keep a simple number called complexity:
- 0 = empty
- 1 = one simple action
- for a sequence, it's the sum of the two parts
"""
from __future__ import annotations
from typing import Any, Optional, List, Tuple

# Other files can import these type names
Grid = List[List[int]]
TrainPair = Tuple[Grid, Grid]

class Program:
    """One node in our program tree (either a leaf action or a Sequence)."""
    def __init__(self, op: Optional[str] = None,
                 left: Optional['Program'] = None,
                 right: Optional[Any] = None):
        # op = the action name (e.g., 'Rotate', 'Mirror', 'ColorChange', or 'Sequence')
        # left/right = for 'Sequence', these are two Program children
        #              for leaf actions, 'right' holds the action's parameters
        self.op = op
        self.left = left
        self.right = right

        # compute a simple size score
        if op == 'Sequence' and isinstance(left, Program) and isinstance(right, Program):
            self.complexity = left.complexity + right.complexity
        elif op is not None:
            self.complexity = 1
        else:
            self.complexity = 0

    def __str__(self) -> str:
        # Make a short, readable string for printing/debugging
        if self.op == 'Sequence':
            return f"Sequence({self.left}, {self.right})"
        elif self.op == 'ColorChange':
            return f"ColorChange({self.right[0]}, {self.right[1]})"
        elif self.op == 'Mirror':
            return f"Mirror({self.right})"
        elif self.op == 'Rotate':
            return f"Rotate({self.right})"
        elif self.op == 'Scale2x2':
            return "Scale2x2()"
        elif self.op == 'Scale3x3':
            return "Scale3x3()"
        elif self.op == 'Scale2x1':
            return "Scale2x1()"
        elif self.op == 'Scale1x2':
            return "Scale1x2()"
        elif self.op == 'ResizeIrregular':
            return f"ResizeIrregular({self.right[0]}x{self.right[1]})"
        elif self.op == 'PositionalShift':
            return f"PositionalShift({self.right[0]}, {self.right[1]}, {self.right[2]}, {self.right[3]})"
        elif self.op == 'ColorMapMultiple':
            return f"ColorMapMultiple({dict(self.right)})"
        elif self.op == 'ScaleWithColorMap':
            return f"ScaleWithColorMap({self.right[0]}, {dict(self.right[1])})"
        elif self.op == 'SwapColors':
            return f"SwapColors({self.right[0]}, {self.right[1]})"
        elif self.op == 'DiagonalReflection':
            return f"DiagonalReflection({self.right[0]}, {self.right[1]})"
        return "Program()"

    def __lt__(self, other: 'Program') -> bool:
        # Let Python compare programs by their complexity (smaller = simpler)
        return self.complexity < other.complexity

    def __eq__(self, other: object) -> bool:
        # Two programs are equal if their structure and parameters match
        return isinstance(other, Program) and (
            self.op == other.op and
            self.left == other.left and
            self.right == other.right
        )
