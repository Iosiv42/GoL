""" Wrapper for Grid and Renderer. """

import time
import threading

import numpy as np

import globals
from . import Grid, Renderer
from utils import MutexVar, PeriodicLoop


class GameOfLife:
    """ Wrapper class over Grid and Renderer. """

    def __init__(self, grid: Grid, renderer: Renderer):
        self.grid = MutexVar(grid)
        self.renderer = renderer
        self.should_update = MutexVar(False)

        self.updater = PeriodicLoop(0.2, self.update_loop)
        self.updater.daemon = True

        self.__create_threads()

    def update_loop(self) -> None:
        """ Loop for updating game of life grid. """

        if self.should_update.inner:
            self.grid.inner.step()
            self.renderer.should_update_instance_vbo.inner = True

    def toggle(self) -> None:
        """ Toggle game's updating. """
        self.should_update.inner = not self.should_update.inner
        self.updater.sleep_event.set()

    def stop(self) -> None:
        """ Stop game's updating. """
        self.should_update.inner = False
        self.updater.sleep_event.set()

    def start(self) -> None:
        """ Start game's updating. """
        self.should_update.inner = True
        self.updater.sleep_event.set()

    def start_threads(self) -> None:
        """ Starts mandatory threads. Note that there's no renderer thread,
            because it's called at paintGL method of main GL widget.
        """

        self.updater.start()

    def fit_view(self, side_scale: float) -> None:
        """ Fit current view matrix to game's current state. """

        bnd_box = self.grid.inner.bounding_box

        a = side_scale * max(bnd_box[2] - bnd_box[0], bnd_box[3] - bnd_box[1])
        t_x = (bnd_box[2] + bnd_box[0] - a) / 2
        t_y = (bnd_box[3] + bnd_box[1] - a) / 2

        self.renderer.view_matrix = np.matrix((
            (1/a, 0, 0, -t_x/a),
            (0, 1/a, 0, -t_y/a),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), np.float32)

    def __create_threads(self) -> None:
        self.update_thread = threading.Thread(
            target=self.update_loop, daemon=True
        )
