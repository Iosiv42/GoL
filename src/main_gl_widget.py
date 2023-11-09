""" Module that contains class with main QOpenGLWidget for displaying
    game of life grid.
"""

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QWheelEvent, QCursor, QMouseEvent

import globals    # pylint: disable=W0622
from game_of_life import Grid, Renderer, GameOfLife, parse_rle
from module_typing import Hz
from utils import MutexVar


class MainGlWidget(QOpenGLWidget):
    """ Qt widget for dealing with OpenGL using PyOpenGL. """

    def __init__(self, parent):
        QOpenGLWidget.__init__(self, parent)
        self.setMinimumSize(100, 100)
        self.setUpdateBehavior(QOpenGLWidget.UpdateBehavior.PartialUpdate)

    def paintGL(self):
        """ Paint on current OpenGL context. """

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        self.game.renderer.render()

    def resizeGL(self, w: int, h: int):
        """ Do some staff when window is resized (precisely, self widget). """
        self.__create_matricies()

    def initializeGL(self):
        """ Initialize or do mandatory variables. """

        # Create shaders.
        self.cell_shader = self.__create_shader_prog(
            "src/shaders/vertex.glsl", "src/shaders/fragment.glsl"
        )
        self.fade_shader = self.__create_shader_prog(
            "src/shaders/fade_vertex.glsl", "src/shaders/fade_fragment.glsl"
        )

        self.__create_matricies()

        self.__create_game(globals.TEST_RLE)

        # Variables for moving game's viwe matrix.
        self.last_move_point = np.matrix((float("nan"),) * 2, dtype=np.float32).T
        self.move_view = False

        # Enable tranparency.
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

    def __create_game(self, rle_path: str) -> None:
        lived_cells = parse_rle(rle_path)

        self.grid = Grid(lived_cells)
        self.renderer = Renderer(self.grid, self.cell_shader)
        self.game = GameOfLife(self.grid, self.renderer)

        self.game.fit_view(1.2)
        self.game.start_threads()

    def restart_game(self, rle_path: str) -> None:
        """ Restart game. """

        lived_cells = parse_rle(rle_path)
        self.game.grid.inner = Grid(lived_cells)
        self.game.renderer.grid = self.game.grid.inner
        self.game.renderer.should_update_instance_vbo.inner = True
        self.game.stop()

    def __create_shader_prog(self, vertex_path, fragment_path) -> int:
        with open(vertex_path, encoding="utf-8") as src:
            v_src = src.read()
        with open(fragment_path, encoding="utf-8") as src:
            f_src = src.read()

        v_shader = shaders.compileShader(v_src, GL_VERTEX_SHADER)
        f_shader = shaders.compileShader(f_src, GL_FRAGMENT_SHADER)
        return shaders.compileProgram(v_shader, f_shader)

    def __create_matricies(self) -> None:
        # Project matrix to keep up squareness.
        min_dim = min(self.width(), self.height())
        globals.proj_matrix = np.matrix((
            (2*min_dim / self.width(), 0, 0, -1),
            (0, 2*min_dim / self.height(), 0, -1),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)
        globals.i_proj_matrix = globals.proj_matrix.I

        # Matrix to convert windows coordinates to homogeneous one.
        self.__win_to_homo = np.matrix((
            (2/self.width(), 0, 0, -1),
            (0, -2/self.height(), 0, 1),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)

    def wheelEvent(self, event: QWheelEvent):
        """ Event when mouse wheel or trackpad was moved or touched. """

        num_pixels = event.pixelDelta()
        num_degrees = event.angleDelta() / 8

        if not num_degrees.isNull():
            self.__scroll_with_degrees(num_degrees.y())
        elif not num_pixels.isNull():
            raise NotImplementedError(
                "Sorry, but touchpads isn't supported now, "
                "because author hasn't one. Please, use Ctrl-+ and Ctrl-- "
                "(control plus and control minus, respectively) or "
                "implement it by yourself. "
            )

        event.accept()

    def __scroll_with_degrees(self, degrees: float) -> None:
        l_pos = self.mapFromGlobal(QCursor.pos())
        l_pos = np.matrix((l_pos.x(), l_pos.y(), 0, 1)).T

        grid_pos = self.__win_to_grid(l_pos)[:2]

        a = 1 / self.game.renderer.view_matrix[0, 0]
        k = 0.9 + (1 - degrees/abs(degrees)) / 10
        new_a = k * a

        t = -a * np.matrix(self.game.renderer.view_matrix.T[3, 0:2]).T
        new_t = (grid_pos - t) * (1 - k) + t

        self.game.renderer.view_matrix = np.matrix((
            (1/new_a, 0, 0, -new_t[0, 0] / new_a),
            (0, 1/new_a, 0, -new_t[1, 0] / new_a),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """ Event when any mouse button was pressed. """

        if event.button() == Qt.LeftButton:
            l_pos = event.position()
            self.last_move_point = np.matrix(
                (l_pos.x(), l_pos.y(), 0, 1), dtype=np.float32
            ).T
            self.last_move_point = self.__win_to_grid(self.last_move_point)
            self.move_view = True

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """ Event when mouse was moved. """

        if (event.buttons() & Qt.LeftButton) and self.move_view:
            l_pos = event.position()
            end_point = np.matrix(
                (l_pos.x(), l_pos.y(), 0, 1), dtype=np.float32
            ).T
            self.__move_view(self.__win_to_grid(end_point))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """ Event when mouse button was released. """

        if event.button() == Qt.LeftButton and self.move_view:
            self.move_view = False

    def __move_view(self, end_point: np.matrix) -> None:
        a = 1/self.game.renderer.view_matrix[0, 0]
        t = -a * np.matrix(self.game.renderer.view_matrix.T[3, 0:2]).T
        ds = end_point - self.last_move_point
        new_t = t - ds[0:2]

        self.game.renderer.view_matrix = np.matrix((
            (1/a, 0, 0, -new_t[0, 0] / a),
            (0, 1/a, 0, -new_t[1, 0] / a),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)

    def __win_to_grid(self, win_pos: np.matrix) -> np.matrix:
        homo_pos = self.__win_to_homo * win_pos
        return self.game.renderer.i_view_matrix * globals.i_proj_matrix * homo_pos

    def toggle_game(self) -> None:
        """ Toggle game of life instance. """
        self.game.toggle()

    def set_game_frequency(self, freq: Hz) -> None:
        """ Set game update frequency (in Hertz). """
        self.game.frames_per_step = globals.FPS // freq
