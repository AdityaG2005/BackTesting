from app.core.strategy import Strategy, Signal, SignalType


class MovingAverageCrossover(Strategy):
    def __init__(self, short_window=20, long_window=50):
        self.short_window = short_window
        self.long_window = long_window

    def on_bar(self, bar, history) -> Signal:
        if len(history) < self.long_window:
            return Signal(
                signal_type=SignalType.HOLD,
                timestamp=bar.timestamp,
                ticker=bar.ticker,
                reason="Not enough history yet"
            )

        closes = [b.close for b in history[-self.long_window:]]

        short_ma = sum(closes[-self.short_window:]) / self.short_window
        long_ma = sum(closes) / self.long_window

        prev_closes = [b.close for b in history[-(self.long_window + 1):-1]]
        prev_short_ma = sum(prev_closes[-self.short_window:]) / self.short_window
        prev_long_ma = sum(prev_closes) / self.long_window

        if prev_short_ma <= prev_long_ma and short_ma > long_ma:
            return Signal(
                signal_type=SignalType.BUY,
                timestamp=bar.timestamp,
                ticker=bar.ticker,
                reason=f"{self.short_window}-day MA crossed above {self.long_window}-day MA"
            )
        elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
            return Signal(
                signal_type=SignalType.SELL,
                timestamp=bar.timestamp,
                ticker=bar.ticker,
                reason=f"{self.short_window}-day MA crossed below {self.long_window}-day MA"
            )

        return Signal(
            signal_type=SignalType.HOLD,
            timestamp=bar.timestamp,
            ticker=bar.ticker,
            reason="No crossover"
        )
    
    