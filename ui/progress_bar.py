import sys
from datetime import datetime
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QProgressBar, QVBoxLayout, QLabel

class Progress_Bar(QWidget):
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()  # Record the start time
        self.initUI()

    def initUI(self):
        # Create a vertical layout
        layout = QVBoxLayout(self)

        # Create the progress bar and add it to the layout
        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)
        
        # Create the time elapsed label and add it to the layout
        self.time_label = QLabel("Time Elapsed: 00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)

        # Set the range of the progress bar
        self.progressBar.setRange(0, 100)
        
        # Set up the window
        self.setWindowTitle('Progress Bar')
        self.setLayout(layout)
        self.resize(300, 100)
        self.show()

    def update_progress(self, percentage):
        # Update the time elapsed label
        elapsed_time = datetime.now() - self.start_time
        hours, remainder = divmod(elapsed_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_label.setText(f"Time Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}")

        # Update the progress bar
        if 0 <= percentage <= 1:
            # Convert to scale of 0 to 100
            progress = int(percentage * 100)
            self.progressBar.setValue(progress)
        else:
            print("Invalid progress value. Please provide a value between 0 and 1.")

