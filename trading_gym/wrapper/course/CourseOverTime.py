from dataclasses import dataclass
from datetime import datetime

from .Course import StockCourse

@dataclass
class StockCourseOverTime(StockCourse):
    has_ended: bool
    step: int

    def __init__(self, name, symbol, course):
        StockCourse.__init__(self, name, symbol, course)
        self.step = 0
        self.has_ended = False

    @staticmethod
    def from_stock_course(stock_course: StockCourse):
        return StockCourseOverTime(stock_course.name, stock_course.symbol, stock_course.course)

    def next_step(self):
        if self.step == len(self.course)-1:
            self.has_ended = True
            return
        self.step += 1

        return self.course[self.step]

    def reset(self):
        self.step = 0

    def __iter__(self):
        return self.course.__iter__()

    def get_last_n_steps(self, n):
        hist = self.course[self.step - n:self.step]
        if len(hist) < 5:
            raise Exception("Not long enough, it is only {}".format(len(hist)))
        return hist

    def get_current_price(self) -> float:
        return self.get_price(self.course[self.step])

    def get_current_date(self) -> datetime:
        return self.course[self.step][0]
