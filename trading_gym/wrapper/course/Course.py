from dataclasses import dataclass
from typing import List, Tuple
from datetime import datetime
import numpy as np
from matplotlib import pylab as plt


@dataclass
class StockCourse:
    symbol: str
    name: str
    # Date/Open/high/low/close/volume
    course: List[Tuple[datetime, float, float, float, float, int]]
    start_date: datetime
    end_date: datetime

    def __init__(self, name, symbol, course):
        self.symbol = symbol
        self.name = name
        self.course = sorted(course)

        self.start_date = course[0][0]
        self.end_date = course[-1][0]

    def __hash__(self):
        return hash((self.name, self.symbol, self.start_date))

    def __repr__(self):
        return "StockCourse(name='{}', stock_symbol='{}', start_date='{}')".format(self.name, self.symbol,
                                                                                   self.start_date)

    def to_df(self):
        return np.array(self.course)

    def __get_price(self, date) -> float:

        for point in self.course:
            if point[0] == date:
                return point[1]

    def get_price(self, date) -> float:
        closest_available_date = None

        for point in self.course:
            if closest_available_date is None:
                closest_available_date = point[0]
                continue
            if (point[0] - date[0]) < (date[0] - closest_available_date):
                closest_available_date = point[0]

        return self.__get_price(closest_available_date)

    def plot(self):
        dates = [data[0] for data in self.course]
        values = [data[1] for data in self.course]
        plt.plot(dates, values)
        plt.show()

    def __getitem__(self, key: datetime):
        for point in course:
            if point[0] == key:
                return point


if __name__ == '__main__':
    # Test some shit
    course = [(datetime(1, 2, 3), 1, 1, 1, 1, 1), (datetime(1, 2, 4), 2, 2, 2, 2, 2),
              (datetime(1, 2, 6), 4, 4, 4, 4, 4), (datetime(1, 2, 5), 3, 3, 3, 3, 3)]
    s = StockCourse("FOO", "Foo", course)
    print(s.course)
    print("_" * 100)
    print(s.to_df())
