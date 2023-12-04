import sys
import threading
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize, QThread, Signal

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget, QDialog, QTextEdit
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt, QSize

from .ui_element_factory import UI_Element_Factory
from .results_menu import Results_Window
from .progress_bar import Progress_Bar
from .ui_context import UI_Context

from stats.searching_attributes import searching_attributes
from simulation.other_variables import OutcomeEnum

import matplotlib
matplotlib.use('Qt5Agg')

import numpy as np
import matplotlib.pyplot as plt

class IntensiveSearchingWorker(QThread):
    progress_updated = Signal(float)
    search_complete = Signal(list)

    def __init__(self, intensive_search_function):
        super().__init__()
        self.intensive_search_function = intensive_search_function

    def run(self): 
        results = self.intensive_search_function(self.update_progress)
        self.search_complete.emit(results)

    def update_progress(self, percentage):
        self.progress_updated.emit(percentage)

