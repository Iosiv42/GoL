""" Main class where game of life action takes place. """

from typing import Optional, Iterable
from operator import itemgetter

import numpy as np
from OpenGL.GL import shaders
from OpenGL.arrays import vbo
from OpenGL.GL import *

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


class GameOfLife:
    """ Class where game of life action takes place. """

    def __init__(self, live_cells: Optional[Iterable[Pos]] = None):
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
        self.__create_vbo()

    def draw(self, shader: ShaderProgram) -> None:
        """ Draw cells at current iteration. """

        self.vbo.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, self.vbo)

        location = glGetUniformLocation(shader, "proj_matrix")
        glProgramUniformMatrix4fv(
            shader, location, 1, GL_TRUE, globals.proj_matrix
        )

        location = glGetUniformLocation(shader, "view_matrix")
        glProgramUniformMatrix4fv(
            shader, location, 1, GL_TRUE, self.__view_matrix
        )

        shaders.glUseProgram(shader)
        glDrawElements(
            GL_TRIANGLES,
            len(self.inds),
            GL_UNSIGNED_INT,
            self.inds,
        )

        self.vbo.unbind()

    def __create_vbo(self) -> None:
        self.verts = np.empty((4*len(self.current_state), 2), dtype=np.float32)
        self.inds = np.empty(6*len(self.current_state), dtype=np.float32)
        for idx, pos in enumerate(self.current_state):
            idx  = 4*idx
            self.verts[idx] = pos

            pos = [pos[0], pos[1] + 1]
            self.verts[idx + 1] = pos

            pos[0] += 1
            self.verts[idx + 2] = pos

            pos[1] -= 1
            self.verts[idx + 3] = pos

            idx = idx//4 * 6
            shift = idx//6 * 4
            self.inds[idx:idx + 6] = tuple(
                i + shift for i in (0, 1, 2, 0, 2, 3)
            )

        self.vbo = vbo.VBO(self.verts)

    @property
    def view_matrix(self):
        """ It's kind of view matrix for 3D games, but for 2D. """
        return self.__view_matrix

    @view_matrix.setter
    def view_matrix(self, new_val):
        self.__view_matrix = new_val

        a = 1/new_val[0, 0]
        t_x = -a * new_val[0, 3]
        t_y = -a * new_val[1, 3]
        self.i_view_matrix = np.matrix((
            (a, 0, 0, t_x),
            (0, a, 0, t_y),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)
