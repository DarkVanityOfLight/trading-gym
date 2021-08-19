from dataclasses import dataclass
from typing import List, Dict

from datetime import datetime

from trading_gym.apis.AlphaAPI import AlphaAPI, RequestType
from trading_gym.wrapper.course import StockCourse
from trading_gym.wrapper.share import Share
from trading_gym.apis.AlphaAPI import alpha_vintage_api_key


@dataclass
class Wallet:
    money: int
    shares: Dict[str, List[Share]]
    courses: List[StockCourse]
    apis: List[AlphaAPI]

    def __init__(self, start_capital: int):
        self.money = start_capital
        self.shares = {}
        self.courses = []
        self.apis = []

    def add_course(self, course: StockCourse):
        self.courses.append(course)

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

        self.add_course(course)
        return course

    def sell(self, share: Share, quantity: int) -> float:
        course = None
        for _course in self.courses:
            if _course.symbol == share.symbol:
                course = _course

        sold_at = datetime.now()

        if course is None:
            raise Exception("Could not find any course with the symbol {} try adding it by using add_course or "
                            "new_course.".format(share.symbol))

        return self.__sell(share, course, sold_at, quantity)

    def __sell(self, stock: Share, course: StockCourse, date: datetime, quantity: int) -> float:
        value = course.get_price(date)

        self.money += value * quantity
        stock.sold(quantity)

        if stock.quantity == 0:
            self.shares[stock.symbol].remove(stock)

        return value * quantity

    def create_new_api(self, symbol: str) -> AlphaAPI:
        api = AlphaAPI(alpha_vintage_api_key, symbol)
        self.apis.append(api)
        return api

    def buy(self, stock_course: StockCourse, quantity: int):
        self.__buy(stock_course, datetime.now(), quantity)

    def __buy(self, stock_course: StockCourse, date: datetime, quantity: int):
        value = stock_course.get_price(date)

        while value * quantity > self.money:
            quantity -= 1

        self.money -= value * quantity

        stock = Share(stock_course.symbol, date, value, quantity)

        if stock_course.symbol in self.shares.keys():
            self.shares[stock_course.symbol].append(stock)
        else:
            self.shares[stock_course.symbol] = [stock]

    def __getitem__(self, key: str) -> List[Share]:
        return self.shares[key]


def test():
    w = Wallet(1000)
    w.new_course("GME", RequestType.INTRADAY, "5min", "full")
    print(w)
    course = w.courses[0]
    print(course)
    w.buy(course, 1)
    stock_to_sell = w["GME"][0]
    w.sell(stock_to_sell, 1)
    print(w)


if __name__ == '__main__':
    test()
