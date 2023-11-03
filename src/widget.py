""" Main Qt widget and file as well. """

import sys

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import QTimer

import globals
from main_gl_widget import MainGlWidget

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget


class Widget(QWidget):
    """ Program main Qt Widget. """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.main_gl_widget = MainGlWidget(self)
        self.ui.horizontalLayout.insertWidget(0, self.main_gl_widget, 7)
        self.ui.horizontalLayout.setStretch(1, 4)

        self.__connect_signals()

        # Set refresh rate.
        timer = QTimer(self)
        timer.setInterval(1000 / globals.FPS)
        timer.timeout.connect(self.main_gl_widget.paint_update)
        timer.start()

    def __connect_signals(self) -> None:
        self.ui.toggleButton.clicked.connect(self.__toggle_button_clicked)
        self.ui.rewindButton.clicked.connect(
            lambda: self.main_gl_widget.restart_game("tests/p18_glider_shuttle.rle")
        )

        self.ui.frequencySlider.valueChanged.connect(
            self.__freqency_slider_val_changed
        )

    def __toggle_button_clicked(self) -> None:
        idk = {"⏵": "⏸", "⏸": "⏵"}
        self.ui.toggleButton.setText(idk[self.ui.toggleButton.text()])
        self.main_gl_widget.toggle_game()

    def __freqency_slider_val_changed(self, value: int) -> None:
        self.main_gl_widget.set_game_frequency(value)
        self.ui.frequencyLabel.setText(f"{value}/s")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
