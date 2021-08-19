import requests
from datetime import datetime

from enum import Enum

from trading_gym.wrapper.course import StockCourse

alpha_vintage_api_key = "4PTO09I6RGA02P9S"


class RequestType(Enum):
    INTRADAY = "TIME_SERIES_INTRADAY",
    DAILY = "TIME_SERIES_DAILY",


def raw_data_to_course(data, date_format: str):
    course = []
    for raw_date in data.keys():
        date = datetime.strptime(raw_date, date_format)
        point = (
            date, float(data[raw_date]["1. open"]), float(data[raw_date]["2. high"]), float(data[raw_date]["3. low"]),
            float(data[raw_date]["4. close"]), int(data[raw_date]["5. volume"])
        )
        course.append(point)

    return course


def consume_raw_response(response):
    data = response.json()

    for pos, key in enumerate(data.keys()):
        if pos == 0:
            metadata_key = key

        if pos == 1:
            data_key = key

    try:
        metadata = data[metadata_key]
        consumed_data = data[data_key]
    except UnboundLocalError:
        print(response.request.url)
        raise Exception(response.text)

    return metadata, consumed_data


class AlphaAPI:
    base_url = "https://www.alphavantage.co/query"

    def __init__(self, api_key, stock_symbol):
        self.api_key = api_key
        self.stock_symbol = stock_symbol

    def intraday(self, interval, outputsize="compact") -> StockCourse:
        params = {'function': 'TIME_SERIES_INTRADAY', 'interval': interval}

        return self.__process_request("%Y-%m-%d %H:%M:%S", params, outputsize=outputsize)

    def daily(self, outputsize="compact") -> StockCourse:
        params = {'function': 'TIME_SERIES_DAILY'}

        return self.__process_request("%Y-%m-%d", params, outputsize=outputsize)

    def __process_request(self, date_format: str,  params={}, headers={}, outputsize="compact"):
        params['outputsize'] = outputsize
        response = self.__request(params, headers)
        metadata, data = consume_raw_response(response)

        course = raw_data_to_course(data, date_format)

        return StockCourse(self.stock_symbol + "Stock Course", self.stock_symbol, course)

    def __request(self, params={}, headers={}):
        params['apikey'] = self.api_key
        params['symbol'] = self.stock_symbol
        return requests.get(self.base_url, params, headers=headers)


if __name__ == '__main__':
    a: AlphaAPI = AlphaAPI(alpha_vintage_api_key, "GME")
    s: StockCourse = a.intraday("5min")
    print(s.to_df())
