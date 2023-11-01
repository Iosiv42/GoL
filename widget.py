# This Python file uses the following encoding: utf-8
import sys
import time

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutSwapBuffers, glutInit
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimer, QPoint, Qt
from PySide6.QtGui import QWheelEvent, QCursor, QMouseEvent
import numpy as np

import globals    # pylint: disable=W0622
from game_of_life import GameOfLife

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.widget = glWidget(self)
        self.ui.horizontalLayout.insertWidget(0, self.widget, 7)

        timer = QTimer(self)
        timer.setInterval(100)   # period, in milliseconds
        timer.timeout.connect(self.widget.repaint)
        timer.start()


class glWidget(QOpenGLWidget):

    def __init__(self, parent):
        QOpenGLWidget.__init__(self, parent)
        self.setMinimumSize(100, 100)

    def paintGL(self):
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)

        self.game.draw(self.shader)
        self.game.step()

    def initializeGL(self):
        with open("vertex.glsl", encoding="utf-8") as f:
            vertex_shader_src = f.read()

        with open("fragment.glsl", encoding="utf-8") as f:
            fragment_shader_src = f.read()

        vertex_shader = shaders.compileShader(vertex_shader_src, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(fragment_shader_src, GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vertex_shader, fragment_shader)

        min_dim = min(self.width(), self.height())
        globals.proj_matrix = np.matrix((
            (2*min_dim / self.width(), 0, 0, -1),
            (0, 2*min_dim / self.height(), 0, -1),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)

        self.__win_to_homo = np.matrix((
            (2/self.width(), 0, 0, -1),
            (0, -2/self.height(), 0, 1),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)

        self.game = GameOfLife((
            (2, 0), (3, 0), (4, -1), (3, -2), (2, -3), (1, -4), (0, -2),
            (0, -3), (6, -1), (7, -1), (6, -2), (7, -2), (1, -6), (2, -6),
            (1, -7), (2, -7),
        ))

        self.last_move_point = np.matrix((float("nan"),) * 2, dtype=np.float32).T
        self.move_view = False

    def wheelEvent(self, event: QWheelEvent):
        num_pixels = event.pixelDelta()
        num_degrees = event.angleDelta() / 8

        if not num_degrees.isNull():
            self.__scroll_with_degrees(num_degrees.y())
        elif not num_pixels.isNull():
            self.__scroll_with_pixels(num_pixels)

        event.accept()

    def __scroll_with_degrees(self, degrees: float) -> None:
        l_pos = self.mapFromGlobal(QCursor.pos())
        steps = degrees / 15

        h_pos = self.__win_to_homo * np.matrix((l_pos.x(), l_pos.y(), 0, 1)).T
        grid_pos = (
            self.game.view_matrix.I
            * globals.proj_matrix.I
            * h_pos
        )[0:2]

        a = 1 / self.game.view_matrix[0, 0]
        k = 0.9 + (1 - degrees/abs(degrees)) / 10
        new_a = k * a

        t = -a * np.matrix(self.game.view_matrix.T[3, 0:2]).T
        new_t = (grid_pos - t) * (1 - k) + t

        self.game.view_matrix = np.matrix((
            (1/new_a, 0, 0, -new_t[0, 0] / new_a),
            (0, 1/new_a, 0, -new_t[1, 0] / new_a),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            l_pos = event.localPos()
            self.last_move_point = np.matrix(
                (l_pos.x(), l_pos.y(), 0, 1), dtype=np.float32
            ).T
            self.last_move_point = self.__win_to_grid(self.last_move_point)
            self.move_view = True

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (event.buttons() & Qt.LeftButton) and self.move_view:
            l_pos = event.localPos()
            end_point = np.matrix(
                (l_pos.x(), l_pos.y(), 0, 1), dtype=np.float32
            ).T
            self.__move_view(self.__win_to_grid(end_point))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and self.move_view:
            self.move_view = False

    def __move_view(self, end_point: np.matrix) -> None:
        a = 1/self.game.view_matrix[0, 0]
        t = -a * np.matrix(self.game.view_matrix.T[3, 0:2]).T
        ds = end_point - self.last_move_point
        new_t = t - ds[0:2]

        self.game.view_matrix = np.matrix((
            (1/a, 0, 0, -new_t[0, 0] / a),
            (0, 1/a, 0, -new_t[1, 0] / a),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), dtype=np.float32)

    def __win_to_grid(self, win_pos: np.matrix) -> np.matrix:
        homo_pos = self.__win_to_homo * win_pos
        return self.game.view_matrix.I * globals.proj_matrix.I * homo_pos

    def __scroll_with_pixels(self, pixels: int) -> None:
        NotImplemented


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
