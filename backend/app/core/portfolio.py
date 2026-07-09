from dataclasses import dataclass, field
from datetime import datetime
from app.core.strategy import SignalType


@dataclass
class Order:
    signal_type: SignalType
    ticker: str
    timestamp: datetime
    reason: str = ""


@dataclass
class Trade:
    ticker: str
    entry_timestamp: datetime
    entry_price: float
    exit_timestamp: datetime = None
    exit_price: float = None
    quantity: float = 0
    side: str = "long"

    @property
    def is_open(self):
        return self.exit_timestamp is None

    @property
    def pnl(self):
        if self.is_open:
            return None
        return (self.exit_price - self.entry_price) * self.quantity


@dataclass
class Position:
    ticker: str
    quantity: float = 0
    avg_entry_price: float = 0


class Portfolio:
    def __init__(self, starting_cash, order_matcher):
        self.cash = starting_cash
        self.starting_cash = starting_cash
        self.order_matcher = order_matcher
        self.position = None
        self.trades = []

    def process_signal(self, signal_type, ticker, next_bar_open, timestamp):
        if signal_type == SignalType.BUY and self.position is None:
            self._open_position(ticker, next_bar_open, timestamp)

        elif signal_type == SignalType.SELL and self.position is not None:
            self._close_position(next_bar_open, timestamp)

    def _open_position(self, ticker, next_bar_open, timestamp):
        fill_price = self.order_matcher.calculate_fill_price(next_bar_open, is_buy=True)
        quantity = self.cash // fill_price

        if quantity <= 0:
            return

        commission = self.order_matcher.calculate_commission(fill_price, quantity)
        cost = (fill_price * quantity) + commission

        self.cash -= cost
        self.position = Position(ticker=ticker, quantity=quantity, avg_entry_price=fill_price)

        self.trades.append(Trade(
            ticker=ticker,
            entry_timestamp=timestamp,
            entry_price=fill_price,
            quantity=quantity
        ))

    def _close_position(self, next_bar_open, timestamp):
        fill_price = self.order_matcher.calculate_fill_price(next_bar_open, is_buy=False)
        commission = self.order_matcher.calculate_commission(fill_price, self.position.quantity)
        proceeds = (fill_price * self.position.quantity) - commission

        self.cash += proceeds

        open_trade = next(t for t in self.trades if t.is_open)
        open_trade.exit_timestamp = timestamp
        open_trade.exit_price = fill_price

        self.position = None

    def total_value(self, current_price):
        position_value = 0
        if self.position is not None:
            position_value = self.position.quantity * current_price
        return self.cash + position_value
    
        