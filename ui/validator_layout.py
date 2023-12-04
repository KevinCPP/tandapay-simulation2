import sys

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget, QDialog, QTextEdit
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt, QSize

from .ui_element_factory import UI_Element_Factory
from stats.hypothesis_test import TestTypeEnum
from stats.statistics_attributes import statistics_attributes

class Validator_Layout:
    def __init__(self, ui_context, widget_width=None):
        self.uic = ui_context
        self.uief = UI_Element_Factory(widget_width)

        self.warning = "[WARN: RECOMMENDED NOT TO CHANGE VALIDATOR SETTINGS]"

        self.ov1_label = "Validator Repeats"
        self.ov1_tooltip = f"{self.warning} Number of times validator will run. With 1 you get a result, with multiple you get a mean and std. dev."

        self.ov2_label = "Validator Samples"
        self.ov2_tooltip = f"{self.warning} How many times validator will sample new variables from the search space"

        self.ov3_label = "Validator Sample Size"
        self.ov3_tooltip = f"{self.warning} How many times will validator run the simulation for each sample to get a result?"

        self.ov4_label = "Max SD"
        self.ov4_tooltip = f"{self.warning} Determines the probability of validator sampling more extreme values. Higher Setting = lower probability"

    def save(self):
        self.uic.ov_obj.validator_repeats     = self.uief.getValue(self.ov1_label) 
        self.uic.ov_obj.validator_num_samples = self.uief.getValue(self.ov2_label) 
        self.uic.ov_obj.validator_sample_size = self.uief.getValue(self.ov3_label) 
        self.uic.ov_obj.maxsd                 = self.uief.getValue(self.ov4_label) 
        return self.uic.ov_obj

    def get_validator_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        header = QLabel("Validator Variables")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        warning_label = QLabel(self.warning)
        warning_label.setStyleSheet("QLabel {color: yellow;}") # make warning message yellow
        warning_font = QFont()
        warning_font.setPointSize(10)
        warning_label.setFont(warning_font)
        warning_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning_label)
        
        self.ov1_hbox = self.uief.make_numeric_entry_element(self.ov1_label, self.ov1_tooltip, self.uic.ov_obj.validator_repeats)
        layout.addLayout(self.ov1_hbox)
        self.ov2_hbox = self.uief.make_numeric_entry_element(self.ov2_label, self.ov2_tooltip, self.uic.ov_obj.validator_num_samples)
        layout.addLayout(self.ov2_hbox)
        self.ov3_hbox = self.uief.make_numeric_entry_element(self.ov3_label, self.ov3_tooltip, self.uic.ov_obj.validator_sample_size)
        layout.addLayout(self.ov3_hbox)
        self.ov4_hbox = self.uief.make_numeric_entry_element(self.ov4_label, self.ov4_tooltip, self.uic.ov_obj.maxsd)
        layout.addLayout(self.ov4_hbox)
        
        return layout
