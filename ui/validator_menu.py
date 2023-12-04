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

class ValidatorWorker(QThread):
    progress_updated = Signal(float)
    validation_complete = Signal(list)

    def __init__(self, validate_function, perc_honest_defectors):
        super().__init__()
        self.validate_function = validate_function
        self.perc_honest_defectors = perc_honest_defectors

    def run(self):

        # Run the validation function
        validator_results = self.validate_function(self.perc_honest_defectors, self.update_progress)
        # Emit the signal when validation is complete
        self.validation_complete.emit(validator_results)

    def update_progress(self, percentage):
        self.progress_updated.emit(percentage)

class Validator_Menu:
    def __init__(self, uic, widget_width=None):
        self.uic = uic
        self.uief = UI_Element_Factory(widget_width)

        self.field1_label = "Percentage of Assigned Honest Defectors you want to validate"
        self.field1_tooltip = """Validator will keep the amount of assigned honest defectors (EV4) contant, but will
        \rsample all of the other variables repeatedly."""

        self.dialog = None

    def create_menu_dialog(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Validator Menu")
        
        self.layout = QVBoxLayout()

        self.field1_hbox = self.uief.make_float_entry_element(self.field1_label, self.field1_tooltip, 20, 0, 100)
        self.layout.addLayout(self.field1_hbox)
        
        self.run_button = self.uief.make_push_button_element("Validate", "Perform validation with these parameters", self.run)
        self.layout.addWidget(self.run_button)
        
        self.dialog.setLayout(self.layout)
        return self.dialog

    def open_validator_menu(self):
        if not self.dialog:
            self.create_menu_dialog()

        self.dialog.setModal(False)
        self.dialog.show()

  
    def handle_validation_complete(self, validator_results):
        validator_results, avg_actual = zip(*validator_results)

        # this should only execute when run_validate is done executing:
        result_str = ""
        if len(validator_results) == 1:
            result_str = f"""
            \rValidated Result: {validator_results[0]*100:.4f}% group collapse
            \rAssigned Defectors: {self.perc_honest_defectors*100:.4f}%
            \rActual Defectors: {avg_actual[0]:.4f}%
            """
        else:
            mean = sum(validator_results) / len(validator_results)
            sd = (sum((x - mean) ** 2 for x in validator_results) / len(validator_results)) ** 0.5
        
            mean_ad = sum(avg_actual) / len(avg_actual)
            sd_ad = (sum((x - mean_ad) ** 2 for x in avg_actual) / len(avg_actual)) ** 0.5

            result_str = f"""
            \rValidated Result: {mean*100:.4f}% +/- {sd*100:.4f}% group collapse
            \rAssigned Defectors: {self.perc_honest_defectors*100:.4f}%
            \rActual Defectors: {mean_ad:.4f}% +/- {sd_ad:.4f}%
            """
        
        self.results_window = Results_Window("Validator Results")
        self.results_window.set_results_text(result_str)
        self.results_window.setWindowFlags(Qt.Window)
        self.results_window.show()
    
    def run(self):
        self.progress_bar = Progress_Bar()

        self.perc_honest_defectors = self.uief.getValue(self.field1_label) / 100 
        self.worker = ValidatorWorker(self.uic.run_validate, self.perc_honest_defectors)
        self.worker.validation_complete.connect(self.handle_validation_complete)
        self.worker.progress_updated.connect(self.progress_bar.update_progress)
        self.worker.start()

        self.dialog.close()
