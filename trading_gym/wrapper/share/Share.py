from dataclasses import dataclass
from datetime import datetime


@dataclass
class Share:
    symbol: str
    bought_at: datetime
    bought_for_unit_price: float
    quantity: int

    def __init__(self, symbol, bought_at, bought_for_unit_price, quantity):
        self.symbol = symbol
        self.bought_at = bought_at
        self.bought_for_unit_price = bought_for_unit_price
        self.quantity = quantity

    def total_cost(self) -> float:
        return self.quantity * self.bought_for_unit_price

    def sold(self, quantity: int) -> int:
        """
        Tell this share that you sold a certain number of it
        :param quantity: How many you sold
        :return: The actual number of shares you sold, if you want to sell more shares then you have
        """

        if self.quantity > quantity:
            self.quantity -= quantity
            return quantity

        else:
            could_not_sell = self.quantity - quantity

            self.quantity = 0
            return quantity - could_not_sell
