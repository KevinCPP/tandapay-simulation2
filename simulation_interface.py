import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget, QDialog, QTextEdit
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt, QSize

from environment_variables import *
from pricing_variables import *
from system_record import *
from user_record import *

from settings_menu import *

from simulation import *
from simulation_results import *
from results_aggregator import Results_Aggregator

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()

        title = QLabel("TandaPay")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(18)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addStretch(1)

        self.run_simulation_btn = QPushButton("Run Simulation")
        self.run_simulation_btn.clicked.connect(self.run_simulation)
        layout.addWidget(self.run_simulation_btn)

        self.history_btn = QPushButton("History")
        self.history_btn.clicked.connect(self.history)
        layout.addWidget(self.history_btn)

        # create variables that could be changed in settings
        self.env_vars = Environment_Variables()
        self.pricing_vars = Pricing_Variables() 
        self.simulation_info = Simulation_Info()

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_btn)

        self.about_btn = QPushButton("About")
        self.about_btn.clicked.connect(self.open_about)
        layout.addWidget(self.about_btn)

        self.quit_btn = QPushButton("Quit")
        self.quit_btn.clicked.connect(self.quit_program)
        layout.addWidget(self.quit_btn)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def run_simulation(self):
        results_aggregator = Results_Aggregator(self.simulation_info.sample_size, False)

        for i in range(self.simulation_info.sample_size):
            simulation_results = exec_simulation(self.env_vars, self.pricing_vars)
            results_aggregator.add_result(simulation_results)    

        self.window = ResultsWindow("Results")
        self.window.set_results_text(results_aggregator.get_string())
        self.window.show()

    def history(self):
        self.window = PlaceholderWindow("History")
        self.window.show()

    def open_settings(self):
        self.settings_dialog = SettingsDialog(self.env_vars, self.pricing_vars, self.simulation_info, self)
        self.settings_dialog.show()

    def open_about(self):
        self.about_window = AboutWindow()
        self.about_window.show()

    def quit_program(self):
        sys.exit()

class AboutWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.setFixedSize(800, 600)

        layout = QVBoxLayout()

        # Define your HTML content here
        html_content = """
        <h1>About TandaPay</h1>
        <p><a href="https://yourwebsite.com">Link to project</a></p>
        <p>License info...</p>
        """

        text_edit = QTextEdit()
        text_edit.setHtml(html_content)
        text_edit.setReadOnly(True)  # Make it read-only
#        text_edit.setStyleSheet("background-color: white;")  # Set white background

        # Add to layout
        layout.addWidget(text_edit)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

class PlaceholderWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(800, 600)
        label = QLabel("Results will be shown here.")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

class ResultsWindow(QMainWindow):
    def __init__(self, title):
        super(ResultsWindow, self).__init__()
        self.setWindowTitle(title)

        # Initialize to 800x600 but make it resizable
        self.resize(800, 600)

        # Create a QPlainTextEdit widget
        self.textbox = QPlainTextEdit()

        # Disable line wrapping
        self.textbox.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Enable horizontal scrollbar
        self.textbox.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Set to read-only
        self.textbox.setReadOnly(True)

        # Set monospace font
        font = QFont("Courier")
        self.textbox.setFont(font)

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.textbox)

        # Create a central widget for the QMainWindow and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def set_results_text(self, text):
        self.textbox.setPlainText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())

