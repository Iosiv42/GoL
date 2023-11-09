""" Renderer module to render game of life grid. """

import threading
import ctypes

import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders

import globals
from . import Grid
from utils import MutexVar


class Renderer:
    """ Class to render game of life grid. """

    def __init__(self, grid: Grid, shader):
        self.grid = grid
        self.shader = shader

        self.view_matrix = np.matrix((
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), np.float32)

        self.should_update_instance_vbo = MutexVar(True)
        self.instance_vbo = glGenBuffers(1)

        self.__create_cell_buffers()
        self.__create_instance_vbo()

    def render(self) -> None:
        """ Render game of life grid to current context. """

        if self.should_update_instance_vbo.inner:
            self.should_update_instance_vbo.inner = False
            self.__create_instance_vbo()

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glVertexAttribDivisor(1, 1)

        location = glGetUniformLocation(self.shader, "proj_matrix")
        glProgramUniformMatrix4fv(
            self.shader, location, 1, GL_TRUE, globals.proj_matrix
        )

        location = glGetUniformLocation(self.shader, "view_matrix")
        glProgramUniformMatrix4fv(
            self.shader, location, 1, GL_TRUE, self.view_matrix
        )

        shaders.glUseProgram(self.shader)
        glDrawElementsInstanced(
            GL_TRIANGLES, 6, GL_UNSIGNED_INT, None, self.cells_count
        )

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

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
        ), np.float32)

    def __create_cell_buffers(self) -> None:
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        verts = np.array((
            (1, 1), (0, 1), (0, 0), (1, 0)
        ), np.float32).flatten()
        inds = np.array((0, 1, 2, 0, 2, 3), np.uint32)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, inds.nbytes, inds, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def __create_instance_vbo(self) -> None:
        offsets = self.__get_offsets()
        self.cells_count = len(offsets)

        glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        glBufferData(GL_ARRAY_BUFFER, offsets.nbytes, offsets, GL_STREAM_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def __get_offsets(self) -> np.ndarray:
        offsets = np.empty((len(self.grid.current_state), 2), np.float32)
        for idx, pos in enumerate(self.grid.current_state):
            offsets[idx] = pos

        return offsets.flatten()
