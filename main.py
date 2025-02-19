#mk9.1602 PRIME
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, QScrollArea,
                            QFileDialog, QMessageBox, QComboBox)  # Added QComboBox
from datetime import timedelta
from PyQt6.QtCore import QTimer, Qt, QDateTime
import sys
import json
from datetime import datetime
from pathlib import Path

class StopwatchWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.minutes = 0
        self.precise_seconds = 0
        self.is_running = False
        self.last_started = None
        self.project_name = ""
        self.parent_layout = parent  # Store reference to parent layout for deletion

        # Main layout for the widget
        main_layout = QVBoxLayout()

        # Top row layout (project name, chunked time, play button)
        top_row = QHBoxLayout()

        # Project name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Project Name")
        self.name_input.textChanged.connect(self.update_project_name)
        top_row.addWidget(self.name_input)

        # 15-minute chunked time display
        self.chunk_time_label = QLabel("00:00")
        self.chunk_time_label.setStyleSheet("font-family: monospace; font-size: 20px;")
        top_row.addWidget(self.chunk_time_label)

        # Play/Pause button
        self.toggle_button = QPushButton("▶")
        self.toggle_button.clicked.connect(self.toggle_timer)
        top_row.addWidget(self.toggle_button)

        # Reset button
        self.reset_button = QPushButton("↺")
        self.reset_button.setToolTip("Reset Timer")
        self.reset_button.clicked.connect(self.reset_timer)
        top_row.addWidget(self.reset_button)

        # Delete button
        self.delete_button = QPushButton("✕")
        self.delete_button.setToolTip("Delete Timer")
        self.delete_button.clicked.connect(self.delete_timer)
        top_row.addWidget(self.delete_button)

        # Copy to Next Day button
        self.copy_next_day_button = QPushButton("↪")
        self.copy_next_day_button.setToolTip("Copy to Next Day")
        self.copy_next_day_button.clicked.connect(self.copy_to_next_day)
        top_row.addWidget(self.copy_next_day_button)

        main_layout.addLayout(top_row)

        # Bottom row layout (precise time and last started)
        bottom_row = QHBoxLayout()

        # Precise time display
        self.precise_time_label = QLabel("Precise time: 00:00:00")
        self.precise_time_label.setStyleSheet("font-family: monospace; font-size: 12px; color: gray;")
        bottom_row.addWidget(self.precise_time_label)

        # Last started time display
        self.last_started_label = QLabel("Last started: --:--:--")
        self.last_started_label.setStyleSheet("font-family: monospace; font-size: 12px; color: gray;")
        bottom_row.addWidget(self.last_started_label)

        main_layout.addLayout(bottom_row)

        self.setLayout(main_layout)

        # Timers setup
        self.chunk_timer = QTimer(self)
        self.chunk_timer.timeout.connect(self.update_chunk_time)
        self.chunk_timer.setInterval(60000)

        self.precise_timer = QTimer(self)
        self.precise_timer.timeout.connect(self.update_precise_time)
        self.precise_timer.setInterval(1000)

    def reset_timer(self):
        """Reset the timer to zero"""
        # Stop the timer if it's running
        if self.is_running:
            self.toggle_timer()

        # Reset all time values
        self.minutes = 0
        self.precise_seconds = 0
        self.last_started = None

        # Update displays
        self.update_chunk_display()
        self.update_precise_display()
        self.update_last_started()

        # Show confirmation
        self.parent().parent().parent().statusBar().showMessage("Timer reset", 3000)

    def delete_timer(self):
        """Remove this stopwatch from the layout"""
        if self.parent_layout:
            # Ask for confirmation
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                "Are you sure you want to delete this timer?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Stop timers
                self.chunk_timer.stop()
                self.precise_timer.stop()

                # Remove widget from layout and delete it
                self.parent_layout.removeWidget(self)
                self.deleteLater()

    def change_theme(self, index):
        """Change the application theme based on the selected index"""
        if index == 0:  # Default
            self.setStyleSheet("")  # Clear any existing styles
        elif index == 1:  # Dark Blue
            self.apply_dark_blue_theme()
        elif index == 2:  # Light Mode
            self.apply_light_theme()
        elif index == 3:  # High Contrast
            self.apply_high_contrast_theme()
        elif index == 4:  # Imperial Fists
            self.apply_imperial_fists_theme()
    def apply_dark_blue_theme(self):
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #1e2a38;
            color: #e0e0e0;
        }
        
        QLabel {
            color: #e0e0e0;
        }
        
        QPushButton {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton:hover {
            background-color: #34495e;
        }
        
        QLineEdit {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox::drop-down {
            border: 0px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2c3e50;
            color: #ecf0f1;
            selection-background-color: #34495e;
        }
        """
        self.setStyleSheet(stylesheet)

    def apply_light_theme(self):
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #f5f5f5;
            color: #333333;
        }
        
        QLabel {
            color: #333333;
        }
        
        QPushButton {
            background-color: #e0e0e0;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        
        QLineEdit {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #333333;
            selection-background-color: #e0e0e0;
        }
        """
        self.setStyleSheet(stylesheet)

    def apply_high_contrast_theme(self):
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #000000;
            color: #ffffff;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #000000;
            color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton:hover {
            background-color: #ffffff;
            color: #000000;
        }
        
        QLineEdit {
            background-color: #000000;
            color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox {
            background-color: #000000;
            color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #000000;
            color: #ffffff;
            selection-background-color: #ffffff;
            selection-color: #000000;
        }
        """
        self.setStyleSheet(stylesheet)

    def update_project_name(self, text):
        self.project_name = text

    def toggle_timer(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.toggle_button.setText("⏸")
            # Start with 15 minutes immediately for chunked time
            if self.minutes == 0:  # Only set to 15 if starting fresh
                self.minutes = 15
            self.update_chunk_display()
            self.chunk_timer.start()

            # Start precise timer
            self.precise_timer.start()

            # Update last started time
            self.last_started = datetime.now()
            self.update_last_started()
        else:
            self.toggle_button.setText("▶")
            self.chunk_timer.stop()
            self.precise_timer.stop()
            # Round to nearest 15 when stopping
            self.minutes = ((self.minutes + 7) // 15) * 15
            self.update_chunk_display()

    def update_chunk_time(self):
        if self.is_running:
            self.minutes += 15
            self.update_chunk_display()

    def update_precise_time(self):
        if self.is_running:
            self.precise_seconds += 1
            self.update_precise_display()

    def update_chunk_display(self):
        hours = self.minutes // 60
        display_minutes = self.minutes % 60
        self.chunk_time_label.setText(f"{hours:02d}:{display_minutes:02d}")

    def update_precise_display(self):
        hours = self.precise_seconds // 3600
        minutes = (self.precise_seconds % 3600) // 60
        seconds = self.precise_seconds % 60
        self.precise_time_label.setText(f"Precise time: {hours:02d}:{minutes:02d}:{seconds:02d}")


    def copy_to_next_day(self):
        """Copy this timer to the next day with reset time"""
        try:
            # Get the main window through parent references
            parent = self.parent()
            while parent and not isinstance(parent, TimeTrackerApp):
                parent = parent.parent()

            if not parent or not isinstance(parent, TimeTrackerApp):
                raise Exception("Could not find TimeTrackerApp parent")

            main_window = parent

            # Save current state
            main_window.save_state()

            # Get next day's date
            current_date = QDateTime.fromString(main_window.current_date, "yyyy-MM-dd")
            next_date = current_date.addDays(1)
            next_date_str = next_date.toString("yyyy-MM-dd")

            # Load existing data
            save_path = main_window.get_save_path()
            all_data = {}
            if save_path.exists():
                with open(save_path) as f:
                    try:
                        all_data = json.load(f)
                    except json.JSONDecodeError:
                        all_data = {}

            # Create or get the next day's data
            if next_date_str not in all_data:
                all_data[next_date_str] = []

            # Create a copy of this timer's state with reset time
            new_state = {
                'project_name': self.project_name,
                'minutes': 0,
                'precise_seconds': 0,
                'is_running': False,
                'last_started': None
            }

            # Add the new state to the next day's data
            all_data[next_date_str].append(new_state)

            # Save all data
            with open(save_path, 'w') as f:
                json.dump(all_data, f)

            # Show confirmation
            main_window.statusBar().showMessage(f"Timer copied to {next_date_str}", 3000)

        except Exception as e:
            # Show error message if something goes wrong
            QMessageBox.warning(
                self,
                "Error Copying Timer",
                f"Could not copy timer to next day: {str(e)}"
            )
    def update_last_started(self):
        if self.last_started:
            time_str = self.last_started.strftime("%H:%M:%S")
            self.last_started_label.setText(f"Last started: {time_str}")

    def get_state(self):
        """Return the current state of the stopwatch for saving"""
        return {
            'project_name': self.project_name,
            'minutes': self.minutes,
            'precise_seconds': self.precise_seconds,
            'is_running': self.is_running,
            'last_started': self.last_started.isoformat() if self.last_started else None
        }

    def load_state(self, state):
        """Load a saved state into the stopwatch"""
        self.project_name = state['project_name']
        self.minutes = state['minutes']
        self.precise_seconds = state['precise_seconds']
        self.is_running = state['is_running']
        self.last_started = datetime.fromisoformat(state['last_started']) if state['last_started'] else None

        self.name_input.setText(self.project_name)
        self.update_chunk_display()
        self.update_precise_display()
        self.update_last_started()

        if self.is_running:
            self.toggle_button.setText("⏸")
            self.chunk_timer.start()
            self.precise_timer.start()
        else:
            self.toggle_button.setText("▶")

class TimeTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Templeton Track")
        self.setMinimumSize(600, 400)

        # Create status bar
        self.statusBar()

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Theme selection dropdown
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Default", "Dark Blue", "Light Mode", "High Contrast", "Imperial Fists"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        # Add theme selector before the date navigation
        main_layout.addLayout(theme_layout)

        # Date navigation
        date_nav = QHBoxLayout()
        prev_button = QPushButton("←")
        prev_button.clicked.connect(self.previous_day)
        self.date_label = QLabel(QDateTime.currentDateTime().toString("yyyy-MM-dd"))
        next_button = QPushButton("→")
        next_button.clicked.connect(self.next_day)

        date_nav.addWidget(prev_button)
        date_nav.addWidget(self.date_label)
        date_nav.addWidget(next_button)
        main_layout.addLayout(date_nav)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Container widget for scroll area
        scroll_widget = QWidget()
        self.stopwatches_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Button layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add New Timer")
        add_button.clicked.connect(self.add_stopwatch)
        report_button = QPushButton("Generate Report")
        report_button.clicked.connect(self.create_report)

        button_layout.addWidget(add_button)
        button_layout.addWidget(report_button)
        main_layout.addLayout(button_layout)

        # Initialize the current date's data
        self.current_date = QDateTime.currentDateTime().toString("yyyy-MM-dd")

        # Load saved state for current date
        self.load_state()

        # Save state when closing
        self.destroyed.connect(self.save_state)

        self.change_theme(0)

    def change_theme(self, index):
        """Change the application theme based on the selected index"""
        if index == 0:  # Default
            self.setStyleSheet("")  # Clear any existing styles
        elif index == 1:  # Dark Blue
            self.apply_dark_blue_theme()
        elif index == 2:  # Light Mode
            self.apply_light_theme()
        elif index == 3:  # High Contrast
            self.apply_high_contrast_theme()
        elif index == 4:  # High Contrast
            self.apply_imperial_fists_theme()
    def apply_dark_blue_theme(self):
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #1e2a38;
            color: #e0e0e0;
        }
        
        QLabel {
            color: #e0e0e0;
        }
        
        QPushButton {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton:hover {
            background-color: #34495e;
        }
        
        QLineEdit {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox::drop-down {
            border: 0px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2c3e50;
            color: #ecf0f1;
            selection-background-color: #34495e;
        }
        """
        self.setStyleSheet(stylesheet)

    def apply_light_theme(self):
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #f5f5f5;
            color: #333333;
        }
        
        QLabel {
            color: #333333;
        }
        
        QPushButton {
            background-color: #e0e0e0;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        
        QLineEdit {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #333333;
            selection-background-color: #e0e0e0;
        }
        """
        self.setStyleSheet(stylesheet)

    def apply_imperial_fists_theme(self):
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #f9be21;
            color: #000000;
        }
        
        QLabel {
            color: #000000; 
        }
        
        QPushButton {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton:hover {
            background-color: #000000;
            color: #ffffff;
        }
        
        QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #000000;
            selection-background-color: #000000;
            selection-color: #ffffff;
            
        }
        """
        self.setStyleSheet(stylesheet)

    def apply_high_contrast_theme(self):
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #000000;
            color: #ffffff;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #000000;
            color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton:hover {
            background-color: #ffffff;
            color: #000000;
        }
        
        QLineEdit {
            background-color: #000000;
            color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox {
            background-color: #000000;
            color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #000000;
            selection-background-color: #000000;
            selection-color: #ffffff;
        }
        """
        self.setStyleSheet(stylesheet)

    def get_save_path(self):
        """Get the path for saving app state"""
        home = str(Path.home())
        save_dir = Path(home) / ".trackey"
        save_dir.mkdir(exist_ok=True)
        return save_dir / "state.json"

    def save_state(self):
        """Save the current state of all stopwatches"""
        save_path = self.get_save_path()

        # Load existing data first
        all_data = {}
        if save_path.exists():
            with open(save_path) as f:
                try:
                    all_data = json.load(f)
                except json.JSONDecodeError:
                    all_data = {}

        # Get current date's stopwatch states
        current_states = []
        for i in range(self.stopwatches_layout.count()):
            widget = self.stopwatches_layout.itemAt(i).widget()
            if isinstance(widget, StopwatchWidget):
                current_states.append(widget.get_state())

        # Update the data for current date
        all_data[self.current_date] = current_states

        # Save all data
        with open(save_path, 'w') as f:
            json.dump(all_data, f)

    def load_state(self):
        """Load saved stopwatches for current date"""
        save_path = self.get_save_path()

        # Clear existing stopwatches
        while self.stopwatches_layout.count():
            child = self.stopwatches_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if save_path.exists():
            with open(save_path) as f:
                try:
                    all_data = json.load(f)
                    if self.current_date in all_data:
                        states = all_data[self.current_date]
                        for state in states:
                            stopwatch = self.add_stopwatch()
                            stopwatch.load_state(state)
                        return
                except json.JSONDecodeError:
                    pass

        # Add one initial stopwatch if no saved state
        self.add_stopwatch()

    def add_stopwatch(self):
        stopwatch = StopwatchWidget(parent=self.stopwatches_layout)
        self.stopwatches_layout.addWidget(stopwatch)
        return stopwatch

    def previous_day(self):
        # Save current state before changing date
        self.save_state()

        current_date = QDateTime.fromString(self.date_label.text(), "yyyy-MM-dd")
        new_date = current_date.addDays(-1)
        self.date_label.setText(new_date.toString("yyyy-MM-dd"))
        self.current_date = new_date.toString("yyyy-MM-dd")

        # Load state for new date
        self.load_state()

    def next_day(self):
        # Save current state before changing date
        self.save_state()

        current_date = QDateTime.fromString(self.date_label.text(), "yyyy-MM-dd")
        new_date = current_date.addDays(1)
        self.date_label.setText(new_date.toString("yyyy-MM-dd"))
        self.current_date = new_date.toString("yyyy-MM-dd")

        # Load state for new date
        self.load_state()

    def create_report(self):
        """Generate a report for the current day's time tracking"""
        report = []
        total_time = 0
        report.append(f"Time Tracking Report for {self.current_date}\n")
        report.append("-" * 50 + "\n\n")

        for i in range(self.stopwatches_layout.count()):
            widget = self.stopwatches_layout.itemAt(i).widget()
            if isinstance(widget, StopwatchWidget):
                project_name = widget.project_name or "Unnamed Project"
                precise_seconds = widget.precise_seconds
                chunked_minutes = widget.minutes

                # Calculate times
                precise_time = timedelta(seconds=precise_seconds)
                chunked_time = timedelta(minutes=chunked_minutes)

                # Add to total time (using chunked time for consistency)
                total_time += chunked_minutes

                report.append(f"Project: {project_name}\n")
                report.append(f"Precise Time: {str(precise_time)}\n")
                report.append(f"Chunked Time: {chunked_time}\n")
                if widget.last_started:
                    report.append(f"Last Started: {widget.last_started.strftime('%H:%M:%S')}\n")
                report.append("\n")

        # Add total time summary
        hours = total_time // 60
        minutes = total_time % 60
        report.append(f"\nTotal Time Tracked: {hours:02d}:{minutes:02d}\n")

        # Save report to file
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            f"time_report_{self.current_date}.txt",
            "Text Files (*.txt)"
        )

        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.writelines(report)
                QMessageBox.information(self, "Success", "Report saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save report: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())
