from typing import List

from dataclasses import dataclass

from trading_gym.apis.AlphaAPI import RequestType
from trading_gym.wrapper.course import StockCourseOverTime
from trading_gym.wrapper.wallet import Wallet


@dataclass
class TimedWallet(Wallet):
    courses: List[StockCourseOverTime]
    
    def __init__(self, start_capital: int):
        Wallet.__init__(self, start_capital)

    def new_course(self, symbol: str, data_type: RequestType = None, interval: str = "5min",
                   outputsize: str = "compact"):

        api = None
        for a in self.apis:
            if a.stock_symbol == symbol:
                api = a

        if api is None:
            api = self.create_new_api(symbol)

        course = None
        if data_type is None:
            course = api.intraday(interval, outputsize)
        elif data_type is RequestType.INTRADAY:
            course = api.intraday(interval, outputsize)
        elif data_type is RequestType.DAILY:
            course = api.daily(outputsize)

        course = StockCourseOverTime.from_stock_course(course)
        self.add_course(course)
        return course
