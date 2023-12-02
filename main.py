from DataBase import get_session
from MillyMachine import MillyMachine as Sensor
from UI import MainWindow
from PySide6.QtWidgets import QApplication
from models import *
from sqlalchemy.orm import joinedload

import sys


def get_sensors(session):
    data = session.query(
        Sensors
    ).filter(
        Sensors.id_productionline == 1
    ).options(
        joinedload(Sensors.typesensor).joinedload(Typesensor.typedata),
        joinedload(Sensors.zone),
        joinedload(Sensors.settings)
    ).all()
    return [
        Sensor(
            session=session,
            id_db=row.id_sensor,
            best_value=row.settings.bestvalue,
            delta=row.settings.delta,
            name=row.typesensor.name + ' ' + row.zone.name
        )
        for row in data
    ]


def main():
    session = get_session()
    app = QApplication(sys.argv)
    window = MainWindow(get_sensors(session), session)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
