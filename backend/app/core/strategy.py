from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    signal_type: SignalType
    timestamp: object
    ticker: str
    reason: str = ""


class Strategy(ABC):
    @abstractmethod
    def on_bar(self, bar, history) -> Signal:
        """
        Called once per bar in time order.
        bar: the current bar (Open, High, Low, Close, Volume, timestamp)
        history: all bars seen so far for this ticker, up to and including 'bar'
        Returns a Signal (BUY, SELL, or HOLD).
        """
        pass

    