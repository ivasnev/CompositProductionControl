from random import uniform, randint
from models import *
from collections import deque
from sqlalchemy import update


class MillyMachine:
    def __init__(self, id_db: int, session, best_value: int = 50, name: str = "Датчик чего-то", delta: int = 5,
                 debug: bool = False,
                 len_history: int = 1000):
        self.session = session
        self.id_db = id_db
        self.debug = debug
        self.name = name
        self.status = "AllGood"
        self.error = None
        self.cur_value = 0
        self.__best_value = best_value
        self.__delta = delta
        self.len_history = len_history
        self.values_history = deque([0.0 for _ in range(self.len_history)], maxlen=self.len_history)

    def get_current(self):
        return self.status, self.cur_value, self.best_value, self.delta

    @property
    def best_value(self):
        return self.__best_value

    @best_value.setter
    def best_value(self, value):
        self.__best_value = value
        table = Curentsettings.__table__
        self.session.execute(update(table).where(table.c.id_sensor == self.id_db).values({"bestvalue": value}))
        self.session.commit()

    @property
    def delta(self):
        return self.__delta

    @delta.setter
    def delta(self, value):
        self.__delta = value
        table = Curentsettings.__table__
        self.session.execute(update(table).where(table.c.id_sensor == self.id_db).values({"delta": value}))
        self.session.commit()

    def next_value(self) -> None:
        if self.debug:
            print("-" * 15, self.name, "-" * 15, sep="")
            print("Current state {}, current value {}".format(self.status, self.cur_value))
        if self.status == "AllGood":
            if self.cur_value > self.best_value * (100 + self.delta) / 100:
                self.status = "OverValue"
            elif self.cur_value < self.best_value * (100 - self.delta) / 100:
                self.status = "UnderValue"
            else:
                self.calc_value()
                self.random_bug()
        elif self.status == "OverValue":
            if self.best_value >= self.cur_value:
                self.status = "AllGood"
            else:
                self.cur_value -= 1
                self.values_history.append(self.cur_value)
                if self.debug:
                    print("Still wait current value: {}".format(self.cur_value))
                # sleep(0.5)
        elif self.status == "UnderValue":
            if self.best_value <= self.cur_value:
                self.status = "AllGood"
            else:
                self.cur_value += 1
                self.values_history.append(self.cur_value)
                if self.debug:
                    print("Still wait current value: {}".format(self.cur_value))
                # sleep(0.5)

        elif self.status == "OcureError":
            if not self.error:
                self.status = "AllGood"
                return
            if self.debug:
                print("PANIC AAAAAAA {}".format(self.error))
            self.random_bug()
        else:
            if self.debug:
                print("I DONT KNOW WHAT TO DO")
            exit(0)
        if self.error:
            self.status = "OcureError"

    def calc_value(self):
        if self.debug:
            print("take data from plc")
        # sleep(1)
        if self.values_history[-1]-self.values_history[-2] > 0:
            self.cur_value = uniform(self.cur_value, self.cur_value * 1.05)
        else:
            self.cur_value = uniform(self.cur_value * 0.95, self.cur_value)
        self.values_history.append(self.cur_value)

    def random_bug(self):
        if randint(0, 100) > 90 and not self.error:
            self.error = 400 if randint(0, 1) else 500
        elif self.error and randint(0, 100) > 90:
            if self.debug:
                print("All good i fix myself")
            self.error = None
