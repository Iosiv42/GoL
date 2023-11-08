""" Wrapper for Grid and Renderer. """

import time
import threading

import numpy as np

import globals
from . import Grid, Renderer


class GameOfLife:
    """ Wrapper class over Grid and Renderer. """

    def __init__(self, grid: Grid, renderer: Renderer):
        self.grid_lock = threading.Lock()
        self.should_update_lock = threading.Lock()
        self.update_period_lock = threading.Lock()

        self.grid = grid
        self.renderer = renderer
        self.should_update = False
        self.update_period = 0.1

        self.__create_threads()

    def update_loop(self) -> None:
        """ Loop for updating game of life grid. """

        next_call = time.time()
        while True:
            if self.should_update:
                self.grid.step()
                self.renderer.should_update_instance_vbo = True
                next_call += self.update_period
            else:
                next_call += globals.FRAME_PERIOD

            delta = next_call - time.time()
            time.sleep(delta * (delta >= 0))

    def toggle(self) -> None:
        """ Toggle game's updating. """
        self.should_update = not self.should_update

    def stop(self) -> None:
        """ Stop game's updating. """
        self.should_update = False

    def start(self) -> None:
        """ Start game's updating. """
        self.should_update = True

    def start_threads(self) -> None:
        """ Starts mandatory threads. Note that there's no renderer thread,
            because it's called at paintGL method of main GL widget.
        """

        self.update_thread.start()

    def fit_view(self, side_scale: float) -> None:
        """ Fit current view matrix to game's current state. """

        bnd_box = self.grid.bounding_box

        a = side_scale * max(bnd_box[2] - bnd_box[0], bnd_box[3] - bnd_box[1])
        t_x = (bnd_box[2] + bnd_box[0] - a) / 2
        t_y = (bnd_box[3] + bnd_box[1] - a) / 2

        self.renderer.view_matrix = np.matrix((
            (1/a, 0, 0, -t_x/a),
            (0, 1/a, 0, -t_y/a),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ), np.float32)

    @property
    def grid(self) -> Grid:
        """ Return game of life grid. """
        with self.grid_lock:
            return self.__grid

    @grid.setter
    def grid(self, new_grid: Grid) -> None:
        with self.grid_lock:
            self.__grid = new_grid

    @property
    def should_update(self) -> bool:
        """ Should game will be updated at next update? """
        with self.should_update_lock:
            return self.__should_update

    @should_update.setter
    def should_update(self, stmt: bool) -> None:
        with self.should_update_lock:
            self.__should_update = stmt

    @property
    def update_period(self) -> float:
        with self.update_period_lock:
            return self.__update_period

    @update_period.setter
    def update_period(self, new_period: float) -> None:
        with self.update_period_lock:
            self.__update_period = new_period

    def __create_threads(self) -> None:
        self.update_thread = threading.Thread(
            target=self.update_loop, daemon=True
        )
