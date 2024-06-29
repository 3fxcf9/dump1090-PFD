import sys

import requests
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from QPrimaryFlightDisplay import QPrimaryFlightDisplay

app = QApplication(sys.argv)
pfd = QPrimaryFlightDisplay()
pfd.zoom = 1

flight = "CHOOSE"
url = "http://localhost:8080/dump1090/data.json"


class ChooserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Choose a flight to track")

        response = requests.get(url)
        aircrafts = response.json()
        flights = [fl["flight"] for fl in aircrafts if len(fl["flight"]) > 0]
        self.listwidget = QListWidget()
        self.listwidget.setObjectName("list")
        self.listwidget.setStyleSheet(
            "#list {background-color:#1e1f29;color: #F8F8F2;}"
        )
        self.listwidget.addItems(flights)

        self.listwidget.itemSelectionChanged.connect(self.selection_changed)

        self.setCentralWidget(self.listwidget)

    def selection_changed(self):
        global flight
        selected = self.listwidget.currentItem().text()
        flight = selected
        self.close()


chooserWindow = ChooserWindow()


def change_tracked_flight():
    chooserWindow.show()


pfd.change_tracked_flight = change_tracked_flight


def update():

    response = requests.get(url)

    aircrafts = response.json()
    print(aircrafts)

    tracked = [ac for ac in aircrafts if flight in ac["flight"]]

    if len(tracked) == 0:
        pfd.error = "NO DATA"
        pfd.flight = flight
        print("ERROR: No data")
        return

    tracked = tracked[0]
    pfd.error = None
    pfd.flight = flight
    pfd.seen = tracked["seen"]
    pfd.roll = 0
    pfd.pitch = 0
    pfd.heading = tracked["track"]
    pfd.airspeed = tracked["speed"]
    pfd.alt = tracked["altitude"]
    pfd.vspeed = -100
    pfd.update()


# Create a timer to update the display of the vehicle state
timer = QTimer()
# Connect the timer to the callback function
timer.timeout.connect(update)
# Start the timer
timer.start(500)

# Start the application
pfd.show()

try:
    sys.exit(app.exec())
except AttributeError:
    sys.exit(app.exec_())
