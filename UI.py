import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTabWidget)
import pyqtgraph as pg
from MillyMachine import MillyMachine as Sensor
from typing import List
from datetime import datetime
from models import *
from sqlalchemy import insert


class PlotWidget(QWidget):
    def __init__(self, parent, sensor: Sensor):
        super().__init__(parent)
        self.sensor = sensor

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#303030')  # Set background color to dark

        self.status_label = QLabel(f"Status ({self.sensor.name}): {self.sensor.status}")
        self.cur_value_label = QLabel(f"Current Value ({self.sensor.name}): {self.sensor.cur_value}")
        self.best_value_label = QLabel(f"Best Value ({self.sensor.name}): {self.sensor.best_value}")
        self.best_value_input = QLineEdit()
        self.delta_label = QLabel(f"Delta ({self.sensor.name}): {self.sensor.delta}")
        self.delta_input = QLineEdit()

        self.update_best_value_button = QPushButton("Change Best Value")
        self.update_best_value_button.clicked.connect(self.update_best_value)

        self.update_delta_button = QPushButton("Change Delta")
        self.update_delta_button.clicked.connect(self.update_delta)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.status_label)
        layout.addWidget(self.cur_value_label)
        layout.addWidget(self.best_value_label)
        layout.addWidget(self.best_value_input)
        layout.addWidget(self.update_best_value_button)
        layout.addWidget(self.delta_label)
        layout.addWidget(self.delta_input)
        layout.addWidget(self.update_delta_button)

        self.generate_data()
        self.plot_data()

        # Create a QTimer to update the plot every 100 milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_sensor_data)
        self.timer.start(100)

    def generate_data(self):
        self.x = [i for i in range(len(self.sensor.values_history))]
        self.y = self.sensor.values_history

    def plot_data(self):
        # Plot the data
        self.plot_widget.clear()
        self.plot_widget.plot(self.x, self.sensor.values_history, pen='b',
                              name=f'{self.sensor.name} - Modified Sin Wave')

    def update_sensor_data(self):
        status, cur_value, best_value, delta = self.sensor.get_current()
        self.sensor.next_value()
        self.status_label.setText(f"Status ({self.sensor.name}): {status}")
        self.cur_value_label.setText(f"Current Value ({self.sensor.name}): {cur_value}")
        self.best_value_label.setText(f"Best Value ({self.sensor.name}): {best_value}")
        self.delta_label.setText(f"Delta ({self.sensor.name}): {delta}")

        # Call plot_data to update the plot
        self.plot_data()

    def update_best_value(self):
        new_best_value = float(self.best_value_input.text())
        self.sensor.best_value = new_best_value
        self.best_value_label.setText(f"Best Value ({self.sensor.name}): {new_best_value}")

    def update_delta(self):
        new_delta = float(self.delta_input.text())
        self.sensor.delta = new_delta
        self.delta_label.setText(f"Delta ({self.sensor.name}): {new_delta}")


class MainWindow(QMainWindow):
    def __init__(self, sensors: List[Sensor], session):
        super().__init__()
        self.session = session

        with open('styles.qss', 'r') as styles_file:
            self.setStyleSheet(styles_file.read())

        self.sensors = sensors

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.dump)
        self.timer.start(10000)

        self.central_widget = QTabWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tabs = []

        for sensor in self.sensors:
            tab = PlotWidget(self.central_widget, sensor)
            self.tabs.append(tab)
            self.central_widget.addTab(tab, sensor.name)

        self.setWindowTitle("Sensor Monitoring Application")
        self.setGeometry(100, 100, 800, 600)

    def dump(self):
        types = {row.code: row.id_typeerror for row in self.session.query(Typeerror)}
        time = datetime.now()
        data = [(*s.sensor.get_current(), s.sensor.id_db) for s in self.tabs]
        self.session.execute(
            insert(Sensorvalue.__table__),
            [
                {
                    'time': time,
                    'value': cur_value,
                    'id_sensor': id_db
                }
                for status, cur_value, best_value, delta, id_db in data
            ]
        )
        errors = [
                {
                    'time': time,
                    'id_typeerror': types[s.sensor.error],
                    'id_sensor': s.sensor.id_db
                }
                for s in self.tabs if s.sensor.error is not None
            ]
        if errors:
            self.session.execute(
                insert(Sensorserror.__table__),
                errors
            )
        self.session.commit()
