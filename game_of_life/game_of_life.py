""" Main class where game of life action takes place. """

from typing import Optional, Iterable
from operator import itemgetter

import numpy as np
from OpenGL.GL import shaders
from OpenGL.arrays import vbo
from OpenGL.GL import *

import globals

Pos = tuple[int, int]
State = set[Pos]
ShaderProgram = GLuint

dirs = ((-1, 0), (1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))


def _neighbors_count(x: int, y: int, state: State) -> int:
    return sum(1 for dx, dy in dirs if (dx + x, dy + y) in state)


def _bounding_box(state: State) -> tuple[Pos]:
    return (
        min(state, key=itemgetter(0))[0],
        max(state, key=itemgetter(1))[1],
        max(state, key=itemgetter(0))[0],
        min(state, key=itemgetter(1))[1],
    )


class GameOfLife:
    """ Class where game of life action takes place. """

    def __init__(self, live_cells: Optional[Iterable[Pos]]):
        """ Give only cells that alive and other is dead. """

        try:
            self.current_state = set(live_cells)
        except TypeError:
            self.current_state = set()

        self.previous_state = set()
        self.bounding_box = _bounding_box(self.current_state)
        self.__create_vbo()
        
        self.view_matrix = np.matrix((
            (0.05, 0, 0, 0),
            (0, 0.05, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)

    def step(self) -> None:
        """ Do next iteration of game. """

        self.previous_state = self.current_state.copy()
        self.current_state = set()

        # Iterate over bounding_box's coordinates and also over its outline.
        # This way program will guarantee that all cells that need
        # to be updated will be updated.
        for y in range(self.bounding_box[3] - 1, self.bounding_box[1] + 2):
            for x in range(self.bounding_box[0] - 1, self.bounding_box[2] + 2):
                curr_pos = (x, y)
                neighs = _neighbors_count(x, y, self.previous_state)

                # Standard game of life rules:
                # if live cell count of neighbors 2 or 3, then proceed as is,
                # if dead one has 3, then proceed as live one.
                if curr_pos in self.previous_state and neighs in {2, 3}:
                    self.current_state.add(curr_pos)
                elif neighs == 3:
                    self.current_state.add(curr_pos)

        self.bounding_box = _bounding_box(self.current_state)
        self.__create_vbo()

    def draw(self, shader: ShaderProgram) -> None:
        """ Draw cells at current iteration. """

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, self.vbo)

        location = glGetUniformLocation(shader, "proj_matrix")
        glProgramUniformMatrix4fv(
            shader, location, 1, GL_TRUE, globals.proj_matrix
        )

        location = glGetUniformLocation(shader, "view_matrix")
        glProgramUniformMatrix4fv(
            shader, location, 1, GL_TRUE, self.view_matrix
        )

        shaders.glUseProgram(shader)
        glDrawElements(
            GL_TRIANGLES,
            len(self.inds),
            GL_UNSIGNED_INT,
            self.inds,
        )

    def __create_vbo(self) -> None:
        self.verts = np.empty(8 * len(self.current_state), dtype=np.float32)
        self.inds = np.empty(6 * len(self.current_state), dtype=np.float32)
        for idx, pos in enumerate(self.current_state):
            idx  = 8*idx

            self.verts[idx:idx + 2] = pos

            pos = (pos[0], pos[1] + 1)
            self.verts[idx + 2:idx + 4] = pos

            pos = (pos[0] + 1, pos[1])
            self.verts[idx + 4:idx + 6] = pos

            pos = (pos[0], pos[1] - 1)
            self.verts[idx + 6:idx + 8] = pos

            idx = idx//8 * 6
            shift = idx//6 * 4
            self.inds[idx:idx + 6] = tuple(
                i + shift for i in (0, 1, 2, 0, 2, 3)
            )

        self.vbo = vbo.VBO(self.verts)
        self.vbo.bind()
