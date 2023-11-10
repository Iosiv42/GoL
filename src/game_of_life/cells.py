""" Main class where game of life action takes place. """

from typing import Optional, Iterable
from operator import itemgetter

import numpy as np

import globals
from module_typing import GameState, Pos, ShaderProgram

# Directions for evaluating neighbors count.
dirs = ((-1, 0), (1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))


def _neighbors_count(x: int, y: int, state: GameState) -> int:
    return sum(1 for dx, dy in dirs if (dx + x, dy + y) in state)


def _bounding_box(state: GameState) -> tuple[Pos, Pos, Pos, Pos]:
    return (
        min(state, key=itemgetter(0))[0],
        min(state, key=itemgetter(1))[1],
        max(state, key=itemgetter(0))[0],
        max(state, key=itemgetter(1))[1],
    )


class Cells:
    """ Class where game of life action takes place. """

    def __init__(
        self, lived_cells: Optional[Iterable[Pos]] = None
    ):
        """ Give only cells that alive and other is dead. """

        try:
            self.current_state = set(lived_cells)
        except TypeError:
            self.current_state = set()

        self.previous_state = set()
        self.bounding_box = _bounding_box(self.current_state)

    def step(self) -> None:
        """ Do next iteration of game. """

        self.previous_state = self.current_state.copy()
        self.current_state = set()

        # Iterate over bounding_box's coordinates and also over its outline.
        # This way program will guarantee that all cells that need
        # to be updated will be updated.
        for y in range(self.bounding_box[1] - 1, self.bounding_box[3] + 2):
            for x in range(self.bounding_box[0] - 1, self.bounding_box[2] + 2):
                curr_pos = (x, y)
                neighs = _neighbors_count(x, y, self.previous_state)

                # Standard game of life rules:
                # if live cell count of neighbors 2 or 3, then proceed as is,
                # if dead one has 3, then proceed as live one.
                if (
                    (curr_pos in self.previous_state and neighs in {2, 3})
                    or (curr_pos not in self.previous_state and neighs == 3)
                ):
                    self.current_state.add(curr_pos)

        self.bounding_box = _bounding_box(self.current_state)
