import sys

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget, QDialog, QTextEdit
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt, QSize

from .ui_element_factory import UI_Element_Factory
from stats.hypothesis_test import TestTypeEnum
from stats.statistics_attributes import statistics_attributes

class Stats_Layout:
    def __init__(self, ui_context, widget_width=None):
        self.uic = ui_context
        self.uief = UI_Element_Factory(widget_width)

        self.ov1_label = "Trial Sample Size"
        self.ov1_tooltip = "Number of simulation runs to use in each trial"

        self.ov2_label = "Trial Count"
        self.ov2_tooltip = "Number of trials to perform (Minimum: 30)"

        self.ov3_label = "Alpha"
        self.ov3_tooltip = "Chance of error you're willing to accept. Example: if you want 95% confidence, select an alpha of 0.05"

        self.ov4_label = "Test Type"
        self.ov4_tooltip = "Type of hypothesis test to perform."

        self.ov5_label = "Outcome to test"
        self.ov5_tooltip = "which outcome do you want to test?"

        self.ov6_label = "Value to test"
        self.ov6_tooltip = "which value do you want to test against? (should be a percentage. Accepts decimal values, such as 66.67)"

        self.ov7_label = "Select Graph"
        self.ov7_tooltip = "select which statistics outcome you would like to plot on a graph"

    def save(self):
        self.uic.ov_obj.trial_sample_size   = self.uief.getValue(self.ov1_label)
        self.uic.ov_obj.trial_count         = self.uief.getValue(self.ov2_label)
        self.uic.ov_obj.alpha               = self.uief.getValue(self.ov3_label)
        self.uic.ov_obj.test_type           = TestTypeEnum[self.uief.getValue(self.ov4_label)]
        self.uic.ov_obj.test_outcome        = self.uief.getValue(self.ov5_label)
        self.uic.ov_obj.value_to_test       = self.uief.getValue(self.ov6_label)
        self.uic.ov_obj.selected_graph      = self.uief.getValue(self.ov7_label)
        return self.uic

    def get_stats_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        header = QLabel("Statistics Variables")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        self.ov1_hbox = self.uief.make_numeric_entry_element(self.ov1_label, self.ov1_tooltip, self.uic.ov_obj.trial_sample_size)
        layout.addLayout(self.ov1_hbox)

        self.ov2_hbox = self.uief.make_numeric_entry_element(self.ov2_label, self.ov2_tooltip, self.uic.ov_obj.trial_count, 30, 2147483647)
        layout.addLayout(self.ov2_hbox)

        self.ov3_hbox = self.uief.make_float_entry_element(self.ov3_label, self.ov3_tooltip, self.uic.ov_obj.alpha, 0.0, 1.0)
        layout.addLayout(self.ov3_hbox)

        options = [option.name for option in TestTypeEnum]
        self.ov4_hbox = self.uief.make_dropdown_entry_element(self.ov4_label, options, self.ov4_tooltip, self.uic.ov_obj.test_type.name)
        layout.addLayout(self.ov4_hbox)
        
        options = statistics_attributes
        self.ov5_hbox = self.uief.make_dropdown_entry_element(self.ov5_label, options, self.ov5_tooltip, self.uic.ov_obj.test_outcome)
        layout.addLayout(self.ov5_hbox)

        self.ov6_hbox = self.uief.make_float_entry_element(self.ov6_label, self.ov6_tooltip, self.uic.ov_obj.value_to_test, 0.0, 100000.0)
        layout.addLayout(self.ov6_hbox)
        
        options = statistics_attributes
        self.ov7_hbox = self.uief.make_dropdown_entry_element(self.ov7_label, options, self.ov7_tooltip, self.uic.ov_obj.selected_graph)
        layout.addLayout(self.ov7_hbox)

        return layout
