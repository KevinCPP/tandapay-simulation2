import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget, QDialog, QTextEdit
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt, QSize

import matplotlib
matplotlib.use("Qt5Agg")




import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

from .ui_element_factory import UI_Element_Factory
from .ui_context import UI_Context
from .settings_menu import Settings_Menu
from .results_menu import Results_Window
from .history_menu import History_Menu
from .searching_menu import Searching_Menu

class Main_Menu(QMainWindow):
    def __init__(self, ui_context: UI_Context):
        super().__init__()
        self.setWindowTitle("Tandapay Simulation")
        self.resize(300, 350)
        self.uief = UI_Element_Factory()
        self.uic = ui_context

        # Set the global style sheet
        self.setStyleSheet("""
            QMainWindow {
                background-color:  #2b2b2b; 
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #555555;
                border: 3px solid #FFFFFF;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QLabel {
                font-size: 35px;
            }
        """)

        self.layout = QVBoxLayout()
        self.title = self.get_title_widget()
        self.layout.addWidget(self.title)
        self.layout.addStretch(1)

        # Create buttons with the new style
        self.run_simulation_btn = self.uief.make_push_button_element("Run Simulation", None, self.run_simulation)
        self.layout.addWidget(self.run_simulation_btn)

        self.run_statistics_btn = self.uief.make_push_button_element("Run Statistics", None, self.run_statistics)
        self.layout.addWidget(self.run_statistics_btn)

        self.run_searching_btn = self.uief.make_push_button_element("Run Searching", None, self.run_searching)
        self.layout.addWidget(self.run_searching_btn)

        self.run_debug_btn = self.uief.make_push_button_element("Run Debug", None, self.run_debug)
        self.layout.addWidget(self.run_debug_btn)

        self.settings_btn = self.uief.make_push_button_element("Settings", None, self.settings)
        self.layout.addWidget(self.settings_btn)

        self.history_btn = self.uief.make_push_button_element("History", None, self.history)
        self.layout.addWidget(self.history_btn)

        self.about_btn = self.uief.make_push_button_element("About", None, self.uic.about)
        self.layout.addWidget(self.about_btn)
    
        self.quit_btn = self.uief.make_push_button_element("Quit", None, self.quit)
        self.layout.addWidget(self.quit_btn)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def run_simulation(self):
        result_str = self.uic.run_simulation()
        self.results_window = Results_Window("Simulation Results")
        self.results_window.set_results_text(result_str)
        self.results_window.show()

    def run_statistics(self):
        result_str, statistics_aggregator = self.uic.run_statistics()
        self.results_window = Results_Window("Statistics Results")
        self.results_window.set_results_text(result_str)
        self.results_window.show()

        


        mean = statistics_aggregator.mean_dict[self.uic.ov_obj.selected_graph]
        std_dev = statistics_aggregator.std_dict[self.uic.ov_obj.selected_graph]

        # Creating a range around the mean, covering 99.7% of the data (3 standard deviations)
        x = np.linspace(mean - 3*std_dev, mean + 3*std_dev, 1000)
        y = stats.norm.pdf(x, mean, std_dev)

        # Plotting the bell curve
        plt.plot(x, y)

        # Adding titles and labels
        plt.title(f'Normal Distribution of {self.uic.ov_obj.selected_graph}', fontsize=14, fontweight='bold')
        plt.xlabel(f'{self.uic.ov_obj.selected_graph}', fontsize=12, fontweight='bold')
        plt.ylabel('Probability Density', fontsize=12, fontweight='bold')

        # Showing the plot
        plt.show()



    def run_searching(self):
        self.searching_menu = Searching_Menu(self.uic)
        self.searching_menu.open_searching_menu()

    def run_debug(self):
        result_str = self.uic.run_debug()
        self.results_window = Results_Window("Debug Results")
        self.results_window.set_results_text(result_str)
        self.results_window.show()

    def settings(self):
        self.settings_menu = Settings_Menu(self.uic, 150)
        self.settings_menu.open_settings_menu()

    def history(self):
        self.history_menu = History_Menu(self.uic, self)
        self.history_menu.show()

    def quit(self):
        self.uic.save_settings()
        sys.exit()

    def get_title_widget(self) -> QLabel:
        title = QLabel("Tandapay")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(64)  # Increase the font size
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")  # Set the font color to white
        return title

